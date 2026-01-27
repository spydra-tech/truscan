const { db } = require('../db/connection');

/**
 * Middleware to authenticate API requests using API key
 */
async function authenticateApiKey(req, res, next) {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Missing or invalid Authorization header. Use: Bearer <api_key>',
      });
    }

    const apiKey = authHeader.substring(7); // Remove 'Bearer ' prefix
    console.log('apiKey', apiKey);
    // Validate API key in database
    const [apiKeyRecord] = await db.query(
      `SELECT api_key, application_id, is_active, expires_at 
       FROM api_keys 
       WHERE api_key = ? AND is_active = TRUE`,
      [apiKey]
    );

    console.log('apiKeyRecord', apiKeyRecord);

    if (!apiKeyRecord || apiKeyRecord.length === 0) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid or inactive API key',
      });
    }

    const keyData = apiKeyRecord;
    console.log('keyData', keyData);
    // Check if API key has expired
    if (keyData.expires_at && new Date(keyData.expires_at) < new Date()) {
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'API key has expired',
      });
    }

    // Update last_used_at
    await db.query(
      'UPDATE api_keys SET last_used_at = NOW() WHERE api_key = ?',
      [apiKey]
    );

    // Attach application_id to request for use in routes
    req.applicationId = keyData.application_id;
    req.apiKey = apiKey;
    console.log('req.applicationId', req.applicationId);
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: 'Authentication failed',
    });
  }
}

module.exports = { authenticateApiKey };
