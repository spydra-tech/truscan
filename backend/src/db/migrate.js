const fs = require('fs');
const path = require('path');
const { db } = require('./connection');

async function migrate() {
  try {
    console.log('Starting database migration...');

    // Read schema file
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');

    // Split by semicolon and execute each statement
    const statements = schema
      .split(';')
      .map((s) => s.trim())
      .filter((s) => s.length > 0 && !s.startsWith('--'));

    for (const statement of statements) {
      try {
        await db.query(statement);
        console.log('✓ Executed:', statement.substring(0, 50) + '...');
      } catch (error) {
        // Ignore "table already exists" errors
        if (error.code !== 'ER_TABLE_EXISTS_ERROR' && error.code !== 'ER_DUP_FIELDNAME') {
          console.error('✗ Error executing statement:', error.message);
          throw error;
        }
      }
    }

    console.log('✓ Database migration completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('✗ Migration failed:', error);
    process.exit(1);
  }
}

migrate();
