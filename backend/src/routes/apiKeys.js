const express = require('express');
const crypto = require('crypto');
const { db } = require('../db/connection');
const { authenticateApiKey } = require('../middleware/auth');

const router = express.Router();

/**
 * POST /api/v1/api-keys
 * Create a new API key for the authenticated application
 */
router.post('/', authenticateApiKey, async (req, res) => {
  try {
    const { name, expires_in_days } = req.body;

    // Generate API key
    const apiKey = `sk_${crypto.randomBytes(32).toString('hex')}`;

    // Calculate expiration date
    let expiresAt = null;
    if (expires_in_days) {
      const expirationDate = new Date();
      expirationDate.setDate(expirationDate.getDate() + parseInt(expires_in_days));
      expiresAt = expirationDate.toISOString().slice(0, 19).replace('T', ' ');
    }

    // Insert API key
    await db.query(
      'INSERT INTO api_keys (api_key, application_id, name, expires_at) VALUES (?, ?, ?, ?)',
      [apiKey, req.applicationId, name || null, expiresAt]
    );

    res.status(201).json({
      success: true,
      api_key: apiKey,
      message: 'API key created successfully',
      expires_at: expiresAt,
      warning: 'Store this API key securely. It will not be shown again.',
    });
  } catch (error) {
    console.error('Error creating API key:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to create API key',
    });
  }
});

/**
 * GET /api/v1/api-keys
 * List API keys for the authenticated application
 */
router.get('/', authenticateApiKey, async (req, res) => {
  try {
    const apiKeys = await db.query(
      `SELECT 
        id, 
        CONCAT(SUBSTRING(api_key, 1, 12), '...', SUBSTRING(api_key, -4)) as masked_key,
        name,
        is_active,
        last_used_at,
        created_at,
        expires_at
      FROM api_keys
      WHERE application_id = ?
      ORDER BY created_at DESC`,
      [req.applicationId]
    );

    res.json({
      api_keys: apiKeys,
    });
  } catch (error) {
    console.error('Error fetching API keys:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch API keys',
    });
  }
});

/**
 * DELETE /api/v1/api-keys/:keyId
 * Revoke an API key
 */
router.delete('/:keyId', authenticateApiKey, async (req, res) => {
  try {
    const { keyId } = req.params;

    // Verify the API key belongs to the authenticated application
    const [keys] = await db.query(
      'SELECT id FROM api_keys WHERE id = ? AND application_id = ?',
      [keyId, req.applicationId]
    );

    if (!keys || keys.length === 0) {
      return res.status(404).json({
        error: 'Not found',
        message: 'API key not found',
      });
    }

    // Deactivate instead of deleting (for audit trail)
    await db.query(
      'UPDATE api_keys SET is_active = FALSE WHERE id = ?',
      [keyId]
    );

    res.json({
      success: true,
      message: 'API key revoked successfully',
    });
  } catch (error) {
    console.error('Error revoking API key:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to revoke API key',
    });
  }
});

module.exports = router;
