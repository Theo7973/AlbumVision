
import os
import json
import pickle
import hashlib
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import OrderedDict
import logging
import asyncio
import aiosqlite

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QMutex, QMutexLocker

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    timestamp: datetime
    access_count: int
    size_bytes: int
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

class LRUCache:
    """Thread-safe LRU cache with size limits"""
    
    def __init__(self, max_size_mb: int = 100, max_items: int = 1000):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_items = max_items
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._total_size = 0
        self._mutex = QMutex()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with QMutexLocker(self._mutex):
            if key in self._cache:
                entry = self._cache[key]
                
                # Check expiration
                if entry.is_expired():
                    self._remove_entry(key)
                    self.misses += 1
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                entry.access_count += 1
                self.hits += 1
                return entry.data
            
            self.misses += 1
            return None
    
    def put(self, key: str, data: Any, expires_in_hours: Optional[int] = None) -> bool:
        """Put item in cache"""
        with QMutexLocker(self._mutex):
            try:
                # Calculate size
                size_bytes = self._calculate_size(data)
                
                # Check if item would exceed max size
                if size_bytes > self.max_size_bytes:
                    return False
                
                # Calculate expiration
                expires_at = None
                if expires_in_hours:
                    expires_at = datetime.now() + timedelta(hours=expires_in_hours)
                
                # Remove existing entry if present
                if key in self._cache:
                    self._remove_entry(key)
                
                # Make space if needed
                while (self._total_size + size_bytes > self.max_size_bytes or 
                       len(self._cache) >= self.max_items):
                    if not self._cache:
                        break
                    self._remove_oldest()
                
                # Add new entry
                entry = CacheEntry(
                    key=key,
                    data=data,
                    timestamp=datetime.now(),
                    access_count=1,
                    size_bytes=size_bytes,
                    expires_at=expires_at
                )
                
                self._cache[key] = entry
                self._total_size += size_bytes
                
                return True
                
            except Exception as e:
                self.logger.error(f"Cache put failed for {key}: {e}")
                return False
    
    def remove(self, key: str) -> bool:
        """Remove item from cache"""
        with QMutexLocker(self._mutex):
            return self._remove_entry(key)
    
    def _remove_entry(self, key: str) -> bool:
        """Remove entry (internal method)"""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._total_size -= entry.size_bytes
            return True
        return False
    
    def _remove_oldest(self):
        """Remove least recently used item"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes"""
        try:
            if isinstance(data, QPixmap):
                # Estimate QPixmap size
                return data.width() * data.height() * 4  # RGBA
            elif isinstance(data, (str, bytes)):
                return len(data.encode() if isinstance(data, str) else data)
            elif isinstance(data, dict):
                return len(json.dumps(data).encode())
            else:
                # Use pickle for other objects
                return len(pickle.dumps(data))
        except:
            return 1024  # Default estimate
    
    def clear(self):
        """Clear all cache entries"""
        with QMutexLocker(self._mutex):
            self._cache.clear()
            self._total_size = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with QMutexLocker(self._mutex):
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "items": len(self._cache),
                "size_mb": self._total_size / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "usage_percent": (self._total_size / self.max_size_bytes * 100)
            }

class DatabaseCache:
    """SQLite-based persistent cache for metadata"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        data BLOB,
                        timestamp REAL,
                        expires_at REAL,
                        access_count INTEGER DEFAULT 1
                    )
                """)
                
                # Create index for performance
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON cache_entries(expires_at)
                """)
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from database cache"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT data, expires_at FROM cache_entries WHERE key = ?",
                    (key,)
                )
                row = await cursor.fetchone()
                
                if row:
                    data_blob, expires_at = row
                    
                    # Check expiration
                    if expires_at and datetime.now().timestamp() > expires_at:
                        await self.remove(key)
                        return None
                    
                    # Update access count
                    await db.execute(
                        "UPDATE cache_entries SET access_count = access_count + 1 WHERE key = ?",
                        (key,)
                    )
                    await db.commit()
                    
                    # Deserialize data
                    return pickle.loads(data_blob)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Database get failed for {key}: {e}")
            return None
    
    async def put(self, key: str, data: Any, expires_in_hours: Optional[int] = None) -> bool:
        """Put item in database cache"""
        try:
            # Calculate expiration
            expires_at = None
            if expires_in_hours:
                expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).timestamp()
            
            # Serialize data
            data_blob = pickle.dumps(data)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key, data, timestamp, expires_at, access_count)
                    VALUES (?, ?, ?, ?, 1)
                """, (key, data_blob, datetime.now().timestamp(), expires_at))
                
                await db.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Database put failed for {key}: {e}")
            return False
    
    async def remove(self, key: str) -> bool:
        """Remove item from database cache"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                await db.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Database remove failed for {key}: {e}")
            return False
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        try:
            current_time = datetime.now().timestamp()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (current_time,)
                )
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database cache statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total entries
                cursor = await db.execute("SELECT COUNT(*) FROM cache_entries")
                total_entries = (await cursor.fetchone())[0]
                
                # Database size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                # Expired entries
                current_time = datetime.now().timestamp()
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM cache_entries WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (current_time,)
                )
                expired_entries = (await cursor.fetchone())[0]
                
                return {
                    "total_entries": total_entries,
                    "expired_entries": expired_entries,
                    "db_size_mb": db_size / (1024 * 1024),
                    "db_path": self.db_path
                }
                
        except Exception as e:
            self.logger.error(f"Stats failed: {e}")
            return {}

class CacheManager:
    """Unified cache manager for all application caching needs"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        # Set up cache directory
        if not cache_dir:
            cache_dir = str(Path.home() / ".albumvision" / "cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize different cache layers
        self.memory_cache = LRUCache(max_size_mb=100, max_items=1000)
        self.db_cache = DatabaseCache(str(self.cache_dir / "metadata.db"))
        
        # Specialized caches
        self.thumbnail_cache = LRUCache(max_size_mb=200, max_items=2000)
        self.ai_analysis_cache = LRUCache(max_size_mb=50, max_items=500)
        
        self.logger = logging.getLogger(__name__)
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start periodic cleanup task"""
        def cleanup_worker():
            while True:
                try:
                    asyncio.run(self.db_cache.cleanup_expired())
                    threading.Event().wait(3600)  # Wait 1 hour
                except Exception as e:
                    self.logger.error(f"Cleanup task error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    # Thumbnail caching
    def get_thumbnail(self, image_path: str, size: Tuple[int, int]) -> Optional[QPixmap]:
        """Get cached thumbnail"""
        cache_key = self._get_thumbnail_key(image_path, size)
        return self.thumbnail_cache.get(cache_key)
    
    def put_thumbnail(self, image_path: str, size: Tuple[int, int], pixmap: QPixmap) -> bool:
        """Cache thumbnail"""
        cache_key = self._get_thumbnail_key(image_path, size)
        return self.thumbnail_cache.put(cache_key, pixmap, expires_in_hours=24)
    
    def _get_thumbnail_key(self, image_path: str, size: Tuple[int, int]) -> str:
        """Generate thumbnail cache key"""
        path_hash = hashlib.md5(image_path.encode()).hexdigest()
        return f"thumb_{path_hash}_{size[0]}x{size[1]}"
    
    # AI analysis caching
    def get_ai_analysis(self, image_path: str) -> Optional[Dict]:
        """Get cached AI analysis"""
        cache_key = self._get_file_hash(image_path)
        return self.ai_analysis_cache.get(f"ai_{cache_key}")
    
    def put_ai_analysis(self, image_path: str, analysis: Dict) -> bool:
        """Cache AI analysis"""
        cache_key = self._get_file_hash(image_path)
        return self.ai_analysis_cache.put(f"ai_{cache_key}", analysis, expires_in_hours=168)  # 1 week
    
    # General metadata caching
    async def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata from memory or database"""
        # Try memory first
        data = self.memory_cache.get(key)
        if data is not None:
            return data
        
        # Try database
        data = await self.db_cache.get(key)
        if data is not None:
            # Put in memory for faster access
            self.memory_cache.put(key, data, expires_in_hours=1)
            return data
        
        return None
    
    async def put_metadata(self, key: str, data: Any, expires_in_hours: Optional[int] = None) -> bool:
        """Store metadata in both memory and database"""
        # Store in memory
        memory_success = self.memory_cache.put(key, data, expires_in_hours)
        
        # Store in database for persistence
        db_success = await self.db_cache.put(key, data, expires_in_hours)
        
        return memory_success or db_success
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file (path + modification time)"""
        try:
            stat = os.stat(file_path)
            content = f"{file_path}_{stat.st_mtime}_{stat.st_size}"
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return hashlib.md5(file_path.encode()).hexdigest()
    
    # Cache management
    def clear_all_caches(self):
        """Clear all cache layers"""
        self.memory_cache.clear()
        self.thumbnail_cache.clear()
        self.ai_analysis_cache.clear()
        # Note: Database cache requires async operation
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache layers"""
        return {
            "memory_cache": self.memory_cache.get_stats(),
            "thumbnail_cache": self.thumbnail_cache.get_stats(),
            "ai_analysis_cache": self.ai_analysis_cache.get_stats(),
            "cache_directory": str(self.cache_dir),
            "total_cache_size_mb": sum([
                self.memory_cache.get_stats()["size_mb"],
                self.thumbnail_cache.get_stats()["size_mb"],
                self.ai_analysis_cache.get_stats()["size_mb"]
            ])
        }
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database cache statistics"""
        return await self.db_cache.get_stats()
    
    # Utility methods
    def invalidate_file_caches(self, file_path: str):
        """Invalidate all caches for a specific file"""
        file_hash = self._get_file_hash(file_path)
        
        # Remove AI analysis
        self.ai_analysis_cache.remove(f"ai_{file_hash}")
        
        # Remove thumbnails (need to iterate as we don't know all sizes)
        # This is less efficient but necessary for complete invalidation
        # In practice, thumbnail cache will expire naturally
    
    async def optimize_caches(self):
        """Optimize all caches by cleaning expired entries"""
        await self.db_cache.cleanup_expired()
        
        # Memory caches clean themselves via LRU mechanism
        # but we can force a stats update
        _ = self.memory_cache.get_stats()
        _ = self.thumbnail_cache.get_stats()
        _ = self.ai_analysis_cache.get_stats()

# Global cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

# Convenience functions
def cache_thumbnail(image_path: str, size: Tuple[int, int], pixmap: QPixmap) -> bool:
    """Cache a thumbnail"""
    return get_cache_manager().put_thumbnail(image_path, size, pixmap)

def get_cached_thumbnail(image_path: str, size: Tuple[int, int]) -> Optional[QPixmap]:
    """Get a cached thumbnail"""
    return get_cache_manager().get_thumbnail(image_path, size)

async def cache_metadata(key: str, data: Any, expires_in_hours: Optional[int] = None) -> bool:
    """Cache metadata"""
    return await get_cache_manager().put_metadata(key, data, expires_in_hours)

async def get_cached_metadata(key: str) -> Optional[Any]:
    """Get cached metadata"""
    return await get_cache_manager().get_metadata(key)