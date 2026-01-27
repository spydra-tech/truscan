const express = require('express');
const { db } = require('../db/connection');
const { authenticateApiKey } = require('../middleware/auth');

const router = express.Router();

/**
 * GET /api/v1/applications
 * Get list of applications (for admin use, or current application)
 */
router.get('/', authenticateApiKey, async (req, res) => {
  try {
    // For now, return only the authenticated application
    // In a full implementation, you might want admin endpoints
    const [applications] = await db.query(
      'SELECT application_id, name, description, created_at, updated_at FROM applications WHERE application_id = ?',
      [req.applicationId]
    );

    if (!applications || applications.length === 0) {
      return res.status(404).json({
        error: 'Not found',
        message: 'Application not found',
      });
    }

    res.json({
      application: applications[0],
    });
  } catch (error) {
    console.error('Error fetching application:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch application',
    });
  }
});

/**
 * GET /api/v1/applications/:applicationId
 * Get application details
 */
router.get('/:applicationId', authenticateApiKey, async (req, res) => {
  try {
    const { applicationId } = req.params;

    // Verify access
    if (applicationId !== req.applicationId) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Access denied to this application',
      });
    }

    const [applications] = await db.query(
      'SELECT application_id, name, description, created_at, updated_at FROM applications WHERE application_id = ?',
      [applicationId]
    );

    if (!applications || applications.length === 0) {
      return res.status(404).json({
        error: 'Not found',
        message: 'Application not found',
      });
    }

    // Get statistics
    const [stats] = await db.query(
      `SELECT 
        COUNT(DISTINCT scan_id) as total_scans,
        SUM(findings_count) as total_findings,
        SUM(critical_count) as total_critical,
        SUM(high_count) as total_high,
        MAX(created_at) as last_scan_at
      FROM scans
      WHERE application_id = ?`,
      [applicationId]
    );

    res.json({
      application: applications[0],
      statistics: stats[0] || {
        total_scans: 0,
        total_findings: 0,
        total_critical: 0,
        total_high: 0,
        last_scan_at: null,
      },
    });
  } catch (error) {
    console.error('Error fetching application details:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch application details',
    });
  }
});

/**
 * PUT /api/v1/applications/:applicationId
 * Update application details
 */
router.put('/:applicationId', authenticateApiKey, async (req, res) => {
  try {
    const { applicationId } = req.params;
    const { name, description } = req.body;
    console.log('applicationId', applicationId);
    // Verify access
    if (applicationId !== req.applicationId) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Access denied to this application',
      });
    }

    await db.query(
      'UPDATE applications SET name = ?, description = ? WHERE application_id = ?',
      [name || null, description || null, applicationId]
    );

    res.json({
      success: true,
      message: 'Application updated successfully',
    });
  } catch (error) {
    console.error('Error updating application:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to update application',
    });
  }
});

module.exports = router;
