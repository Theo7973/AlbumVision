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
  namedPlaceholders: true,
});
cd 

(async () => {
  try {
    const [rows] = await pool.query('SELECT NOW() AS now');
    console.log(`  Connected! MySQL time is ${rows[0].now}`);
  } catch (err) {
    console.error('  DB error:', err.message);
  } finally {
    await pool.end();       
  }
})();
