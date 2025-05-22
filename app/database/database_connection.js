import mysql from 'mysql2/promise';
import * as dotenv from 'dotenv';
dotenv.config();

const pool = mysql.createPool({
  host:     process.env.DB_HOST || '127.0.0.1',
  port:     Number(process.env.DB_PORT) || 3306,
  user:     process.env.DB_USER || 'albumvision_app',
  password: process.env.DB_PASS || 'AVp@ss_2025!',
  database: process.env.DB_NAME || 'albumvision',
  waitForConnections: true,
  connectionLimit: 10,
});

try {
  // Create table if it doesn't exist
  await pool.query(`
    CREATE TABLE IF NOT EXISTS test_entries (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(255),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // Insert sample data
  const [insertResult] = await pool.query(
    'INSERT INTO test_entries (name) VALUES (?)',
    ['Test Entry ' + new Date().toISOString()]
  );
  console.log(`✅ Inserted! New ID: ${insertResult.insertId}`);

  // Retrieve data to verify
  const [rows] = await pool.query('SELECT * FROM test_entries ORDER BY created_at DESC LIMIT 5');
  console.log('📦 Latest entries:', rows);
} catch (err) {
  console.error('❌ DB error:', err.message);
} finally {
  await pool.end();
}
