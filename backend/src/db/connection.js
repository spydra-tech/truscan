const mysql = require('mysql2/promise');
require('dotenv').config();

const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 3306,
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'llm_scan_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 0,
};

// Create connection pool
const pool = mysql.createPool(dbConfig);

// Export a promise-based query function
const db = {
  query: async (sql, params) => {
    try {
      const [results] = await pool.execute(sql, params);
      return results;
    } catch (error) {
      console.error('Database query error:', error);
      throw error;
    }
  },
  // Use regular query (not prepared statement) for transaction commands
  queryRaw: async (sql) => {
    try {
      const [results] = await pool.query(sql);
      return results;
    } catch (error) {
      console.error('Database query error:', error);
      throw error;
    }
  },
  execute: async (sql, params) => {
    try {
      const [results] = await pool.execute(sql, params);
      return results;
    } catch (error) {
      console.error('Database execute error:', error);
      throw error;
    }
  },
  end: async () => {
    await pool.end();
  },
};

module.exports = { db, pool };
