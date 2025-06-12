# File: app/utils/image_quality.py
# Enhanced image quality analysis with AI integration and performance optimization

import cv2
import numpy as np
import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import logging

# Import AI services
try:
    from app.services.ai_service import AIImageAnalyzer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    class AIImageAnalyzer:
        async def analyze_image(self, image_path: str) -> Dict:
            return {"error": "AI service not available"}

# Import caching
try:
    from app.utils.cache_manager import CacheManager
    cache_manager = CacheManager()
except ImportError:
    cache_manager = None

@dataclass
class ImageQualityResult:
    """Comprehensive image quality analysis result"""
    path: str
    quality: str  # "excellent", "high", "medium", "low", "poor"
    score: float
    dimensions: Tuple[int, int]
    file_size: int
    
    # Technical metrics
    blur_score: float
    noise_score: float
    exposure_score: float
    contrast_score: float
    sharpness_score: float
    
    # AI-powered analysis (when available)
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_tags: Optional[List[str]] = None
    faces_detected: Optional[int] = None
    aesthetic_score: Optional[float] = None
    
    # Metadata
    timestamp: str = ""
    processing_time: float = 0.0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class EnhancedImageQualityChecker:
    """Enhanced image quality checker with AI integration and caching"""
    
    def __init__(self, use_ai: bool = True, use_cache: bool = True):
        self.use_ai = use_ai and AI_AVAILABLE
        self.use_cache = use_cache
        self.ai_analyzer = AIImageAnalyzer() if self.use_ai else None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Cache settings
        self.cache_dir = Path.home() / ".albumvision" / "quality_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    async def analyze_image_comprehensive(self, image_path: str, threshold: float = 150) -> ImageQualityResult:
        """
        Comprehensive image analysis combining traditional CV and AI methods
        """
        start_time = datetime.now()
        
        # Check cache first
        if self.use_cache:
            cached_result = await self._get_cached_result(image_path)
            if cached_result:
                return cached_result
        
        try:
            # Get basic file info
            file_size = os.path.getsize(image_path)
            
            # Run traditional CV analysis
            cv_result = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._analyze_cv_quality, image_path, threshold
            )
            
            # Initialize result with CV data
            result = ImageQualityResult(
                path=image_path,
                quality=cv_result["quality"],
                score=cv_result["score"],
                dimensions=cv_result["dimensions"],
                file_size=file_size,
                blur_score=cv_result["blur_score"],
                noise_score=cv_result["noise_score"],
                exposure_score=cv_result["exposure_score"],
                contrast_score=cv_result["contrast_score"],
                sharpness_score=cv_result["sharpness_score"]
            )
            
            # Add AI analysis if available
            if self.use_ai and self.ai_analyzer:
                try:
                    ai_result = await self.ai_analyzer.analyze_image(image_path)
                    result.ai_category = ai_result.get("category")
                    result.ai_confidence = ai_result.get("confidence")
                    result.ai_tags = ai_result.get("tags", [])
                    result.faces_detected = ai_result.get("faces", 0)
                    result.aesthetic_score = ai_result.get("aesthetic_score")
                    
                    # Enhance quality assessment with AI data
                    result = self._combine_cv_ai_scores(result, ai_result)
                    
                except Exception as e:
                    self.logger.warning(f"AI analysis failed for {image_path}: {e}")
            
            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Cache the result
            if self.use_cache:
                await self._cache_result(image_path, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {e}")
            return ImageQualityResult(
                path=image_path,
                quality="error",
                score=0,
                dimensions=(0, 0),
                file_size=0,
                blur_score=0,
                noise_score=0,
                exposure_score=0,
                contrast_score=0,
                sharpness_score=0,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _analyze_cv_quality(self, image_path: str, threshold: float) -> Dict:
        """Enhanced OpenCV-based quality analysis with multiple metrics"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")
            
            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur detection (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. Noise estimation
            noise_score = self._estimate_noise(gray)
            
            # 3. Exposure analysis
            exposure_score = self._analyze_exposure(gray)
            
            # 4. Contrast analysis
            contrast_score = self._analyze_contrast(gray)
            
            # 5. Sharpness analysis (Sobel)
            sharpness_score = self._analyze_sharpness(gray)
            
            # Adjust threshold based on image size
            size_factor = min(width, height) / 1000
            adjusted_threshold = threshold * max(0.5, size_factor)
            
            # Resolution score
            resolution_score = (height * width) / 1000000
            
            # Combined quality score
            combined_score = self._calculate_combined_score(
                laplacian_var, noise_score, exposure_score, 
                contrast_score, sharpness_score, resolution_score, size_factor
            )
            
            # Determine quality level
            quality = self._determine_quality_level(combined_score, adjusted_threshold)
            
            return {
                "quality": quality,
                "score": combined_score,
                "dimensions": (width, height),
                "blur_score": laplacian_var,
                "noise_score": noise_score,
                "exposure_score": exposure_score,
                "contrast_score": contrast_score,
                "sharpness_score": sharpness_score
            }
            
        except Exception as e:
            raise Exception(f"CV analysis failed: {e}")
    
    def _estimate_noise(self, gray_img: np.ndarray) -> float:
        """Estimate image noise using high-frequency components"""
        # Use high-pass filter to isolate noise
        kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]])
        filtered = cv2.filter2D(gray_img, -1, kernel)
        noise_var = np.var(filtered)
        return min(100, noise_var / 100)  # Normalize to 0-100
    
    def _analyze_exposure(self, gray_img: np.ndarray) -> float:
        """Analyze exposure quality"""
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
        
        # Check for clipping (over/under exposure)
        total_pixels = gray_img.shape[0] * gray_img.shape[1]
        
        # Under-exposed (too many dark pixels)
        dark_pixels = np.sum(hist[:20]) / total_pixels
        
        # Over-exposed (too many bright pixels)
        bright_pixels = np.sum(hist[235:]) / total_pixels
        
        # Well-exposed images have good distribution
        exposure_score = 100 - (dark_pixels + bright_pixels) * 200
        return max(0, min(100, exposure_score))
    
    def _analyze_contrast(self, gray_img: np.ndarray) -> float:
        """Analyze image contrast"""
        return gray_img.std()  # Standard deviation as contrast measure
    
    def _analyze_sharpness(self, gray_img: np.ndarray) -> float:
        """Analyze image sharpness using Sobel operators"""
        sobelx = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        return np.mean(magnitude)
    
    def _calculate_combined_score(self, blur_score: float, noise_score: float, 
                                exposure_score: float, contrast_score: float,
                                sharpness_score: float, resolution_score: float, 
                                size_factor: float) -> float:
        """Calculate weighted combined quality score"""
        
        # Weights for different factors
        weights = {
            'blur': 0.25,
            'noise': -0.15,  # Lower noise is better
            'exposure': 0.20,
            'contrast': 0.15,
            'sharpness': 0.20,
            'resolution': 0.15
        }
        
        # Normalize noise score (invert because lower is better)
        noise_normalized = max(0, 100 - noise_score)
        
        combined = (
            blur_score * weights['blur'] +
            noise_normalized * weights['noise'] +
            exposure_score * weights['exposure'] +
            contrast_score * weights['contrast'] +
            sharpness_score * weights['sharpness'] +
            (resolution_score * 30) * weights['resolution']
        ) * size_factor
        
        return combined
    
    def _determine_quality_level(self, score: float, threshold: float) -> str:
        """Determine quality level based on score"""
        if score > threshold * 2:
            return "excellent"
        elif score > threshold * 1.5:
            return "high"
        elif score > threshold:
            return "medium"
        elif score > threshold * 0.5:
            return "low"
        else:
            return "poor"
    
    def _combine_cv_ai_scores(self, cv_result: ImageQualityResult, ai_result: Dict) -> ImageQualityResult:
        """Combine CV and AI analysis for enhanced quality assessment"""
        
        # Enhance quality based on AI feedback
        aesthetic_score = ai_result.get("aesthetic_score", 0)
        faces_count = ai_result.get("faces", 0)
        
        # Boost score for aesthetically pleasing images
        if aesthetic_score and aesthetic_score > 0.7:
            cv_result.score *= 1.2
        
        # Boost score for images with faces (often more important)
        if faces_count > 0:
            cv_result.score *= 1.1
        
        # Re-evaluate quality level with enhanced score
        cv_result.quality = self._determine_quality_level(cv_result.score, 150)
        
        return cv_result
    
    async def _get_cached_result(self, image_path: str) -> Optional[ImageQualityResult]:
        """Get cached analysis result if available and fresh"""
        try:
            cache_file = self._get_cache_path(image_path)
            
            if not cache_file.exists():
                return None
            
            # Check if cache is fresh (24 hours)
            if datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime) > timedelta(hours=24):
                cache_file.unlink()  # Remove stale cache
                return None
            
            async with aiofiles.open(cache_file, 'r') as f:
                data = json.loads(await f.read())
                return ImageQualityResult(**data)
                
        except Exception as e:
            self.logger.debug(f"Cache read failed for {image_path}: {e}")
            return None
    
    async def _cache_result(self, image_path: str, result: ImageQualityResult):
        """Cache analysis result"""
        try:
            cache_file = self._get_cache_path(image_path)
            
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(asdict(result), indent=2))
                
        except Exception as e:
            self.logger.debug(f"Cache write failed for {image_path}: {e}")
    
    def _get_cache_path(self, image_path: str) -> Path:
        """Generate cache file path for image"""
        # Use file path hash as cache key
        path_hash = hashlib.md5(image_path.encode()).hexdigest()
        return self.cache_dir / f"{path_hash}.json"
    
    async def batch_analyze(self, image_paths: List[str], 
                          progress_callback=None) -> List[ImageQualityResult]:
        """Analyze multiple images with progress tracking"""
        results = []
        total = len(image_paths)
        
        for i, path in enumerate(image_paths):
            try:
                result = await self.analyze_image_comprehensive(path)
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, path)
                    
            except Exception as e:
                self.logger.error(f"Failed to analyze {path}: {e}")
                results.append(ImageQualityResult(
                    path=path, quality="error", score=0, dimensions=(0, 0),
                    file_size=0, blur_score=0, noise_score=0, exposure_score=0,
                    contrast_score=0, sharpness_score=0
                ))
        
        return results
    
    def cleanup_cache(self, max_age_days: int = 30):
        """Clean up old cache files"""
        try:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            for cache_file in self.cache_dir.glob("*.json"):
                if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_time:
                    cache_file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")

# Backward compatibility function
async def check_image_quality(image_path: str, threshold: float = 150) -> Tuple[str, float, Tuple[int, int]]:
    """
    Backward compatible function for existing code
    """
    checker = EnhancedImageQualityChecker(use_ai=False)
    result = await checker.analyze_image_comprehensive(image_path, threshold)
    return result.quality, result.score, result.dimensions

# Synchronous version for compatibility
def check_image_quality_sync(image_path: str, threshold: float = 150) -> Tuple[str, float, Tuple[int, int]]:
    """
    Synchronous version of quality check for backward compatibility
    """
    return asyncio.run(check_image_quality(image_path, threshold))