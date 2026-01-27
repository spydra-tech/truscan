const crypto = require('crypto');
const { db } = require('./connection');

async function seed() {
  try {
    console.log('Starting database seeding...');

    // Create a sample application
    const applicationId = 'demo-app-001';
    const [apps] = await db.query(
      'SELECT id FROM applications WHERE application_id = ?',
      [applicationId]
    );

    if (!apps || apps.length === 0) {
      await db.query(
        'INSERT INTO applications (application_id, name, description) VALUES (?, ?, ?)',
        [
          applicationId,
          'Demo Application',
          'A sample application for testing the LLM Security Scanner',
        ]
      );
      console.log('✓ Created demo application');
    } else {
      console.log('✓ Demo application already exists');
    }

    // Create a sample API key
    const apiKey = `sk_${crypto.randomBytes(32).toString('hex')}`;
    const [keys] = await db.query(
      'SELECT id FROM api_keys WHERE api_key = ?',
      [apiKey]
    );

    if (!keys || keys.length === 0) {
      await db.query(
        'INSERT INTO api_keys (api_key, application_id, name) VALUES (?, ?, ?)',
        [apiKey, applicationId, 'Demo API Key']
      );
      console.log('✓ Created demo API key');
      console.log(`\n📝 Demo API Key: ${apiKey}`);
      console.log('⚠️  Save this API key - it will not be shown again!');
    } else {
      console.log('✓ Demo API key already exists');
    }

    console.log('✓ Database seeding completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('✗ Seeding failed:', error);
    process.exit(1);
  }
}

seed();
