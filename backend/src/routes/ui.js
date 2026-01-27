const express = require('express');
const path = require('path');
const { db } = require('../db/connection');
const { authenticateApiKey } = require('../middleware/auth');

const router = express.Router();

// Serve static UI files
router.use(express.static(path.join(__dirname, '../../public')));

/**
 * GET /ui
 * Dashboard page
 */
router.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../../public/index.html'));
});

/**
 * GET /ui/scans/:scanId
 * Scan details page
 */
router.get('/scans/:scanId', (req, res) => {
  res.sendFile(path.join(__dirname, '../../public/scan-details.html'));
});

/**
 * GET /ui/api/dashboard
 * Get dashboard statistics (requires API key)
 */
router.get('/api/dashboard', authenticateApiKey, async (req, res) => {
  try {
    // Get application statistics
    const stats = await db.query(
      `SELECT 
        COALESCE(COUNT(DISTINCT scan_id), 0) as total_scans,
        COALESCE(SUM(findings_count), 0) as total_findings,
        COALESCE(SUM(critical_count), 0) as total_critical,
        COALESCE(SUM(high_count), 0) as total_high,
        COALESCE(SUM(medium_count), 0) as total_medium,
        COALESCE(SUM(low_count), 0) as total_low,
        COALESCE(SUM(info_count), 0) as total_info,
        MAX(created_at) as last_scan_at
      FROM scans
      WHERE application_id = ?`,
      [req.applicationId]
    );

    // Get recent scans
    const recentScans = await db.query(
      `SELECT 
        scan_id, status, findings_count, critical_count, high_count,
        scan_duration_seconds, created_at
      FROM scans
      WHERE application_id = ?
      ORDER BY created_at DESC
      LIMIT 10`,
      [req.applicationId]
    );

    // Get findings with AI analysis count
    const aiStats = await db.query(
      `SELECT 
        COALESCE(COUNT(*), 0) as findings_with_ai,
        COALESCE(COUNT(CASE WHEN ai_filtered = TRUE THEN 1 END), 0) as ai_filtered_count,
        AVG(JSON_EXTRACT(ai_analysis, '$.confidence')) as avg_confidence
      FROM findings f
      JOIN scans s ON f.scan_id = s.scan_id
      WHERE s.application_id = ? AND f.ai_analysis IS NOT NULL`,
      [req.applicationId]
    );

    res.json({
      application_id: req.applicationId,
      statistics: stats[0] || {
        total_scans: 0,
        total_findings: 0,
        total_critical: 0,
        total_high: 0,
        total_medium: 0,
        total_low: 0,
        total_info: 0,
        last_scan_at: null,
      },
      ai_statistics: aiStats[0] || {
        findings_with_ai: 0,
        ai_filtered_count: 0,
        avg_confidence: null,
      },
      recent_scans: recentScans || [],
    });
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch dashboard data',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /ui/api/scans
 * Get all scans for UI (requires API key)
 */
router.get('/api/scans', authenticateApiKey, async (req, res) => {
  try {
    const { page = 1, limit = 50, severity, status } = req.query;
    const pageNum = Math.max(1, parseInt(page) || 1);
    const limitNum = Math.max(1, Math.min(100, parseInt(limit) || 50)); // Max 100 per page
    const offset = (pageNum - 1) * limitNum;

    let query = `
      SELECT 
        scan_id, status, scanned_files_count, rules_loaded_count,
        findings_count, critical_count, high_count, medium_count, low_count, info_count,
        scan_duration_seconds, created_at
      FROM scans
      WHERE application_id = ?
    `;
    const params = [req.applicationId];

    if (status) {
      query += ' AND status = ?';
      params.push(status);
    }

    // LIMIT and OFFSET must be embedded in SQL string, not placeholders
    query += ` ORDER BY created_at DESC LIMIT ${limitNum} OFFSET ${offset}`;

    const scans = await db.query(query, params);

    // Get total count
    const countResult = await db.query(
      'SELECT COUNT(*) as total FROM scans WHERE application_id = ?',
      [req.applicationId]
    );
    const total = countResult[0]?.total || 0;

    res.json({
      scans,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total,
        total_pages: Math.ceil(total / limitNum),
      },
    });
  } catch (error) {
    console.error('Error fetching scans:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch scans',
    });
  }
});

/**
 * GET /ui/api/scans/:scanId
 * Get detailed scan data for UI (requires API key)
 */
router.get('/api/scans/:scanId', authenticateApiKey, async (req, res) => {
  try {
    const { scanId } = req.params;

    // Get scan details
    const scans = await db.query(
      'SELECT * FROM scans WHERE scan_id = ? AND application_id = ?',
      [scanId, req.applicationId]
    );

    if (!scans || scans.length === 0) {
      return res.status(404).json({
        error: 'Not found',
        message: 'Scan not found',
      });
    }

    const scan = scans[0];

    // Get findings with AI analysis
    const findings = await db.query(
      `SELECT 
        id, rule_id, message, severity, category,
        file_path, start_line, start_column, end_line, end_column,
        snippet, cwe, remediation, source, ai_filtered,
        ai_analysis, dataflow_path, metadata, created_at
      FROM findings
      WHERE scan_id = ?
      ORDER BY 
        FIELD(severity, 'critical', 'high', 'medium', 'low', 'info'),
        file_path, start_line`,
      [scanId]
    );

    // Get scanned files
    const scannedFiles = await db.query(
      'SELECT file_path FROM scanned_files WHERE scan_id = ? ORDER BY file_path',
      [scanId]
    );

    // Get rules loaded
    const rulesLoaded = await db.query(
      'SELECT rule_id FROM rules_loaded WHERE scan_id = ? ORDER BY rule_id',
      [scanId]
    );

    // Parse JSON fields (MySQL2 may return JSON columns as objects or strings)
    if (scan.metadata) {
      scan.metadata = typeof scan.metadata === 'string' ? JSON.parse(scan.metadata) : scan.metadata;
    }
    
    findings.forEach((finding) => {
      if (finding.ai_analysis) {
        finding.ai_analysis = typeof finding.ai_analysis === 'string' 
          ? JSON.parse(finding.ai_analysis) 
          : finding.ai_analysis;
      }
      if (finding.dataflow_path) {
        finding.dataflow_path = typeof finding.dataflow_path === 'string'
          ? JSON.parse(finding.dataflow_path)
          : finding.dataflow_path;
      }
      if (finding.metadata) {
        finding.metadata = typeof finding.metadata === 'string'
          ? JSON.parse(finding.metadata)
          : finding.metadata;
      }
    });

    res.json({
      scan: {
        ...scan,
        scanned_files: scannedFiles.map((f) => f.file_path),
        rules_loaded: rulesLoaded.map((r) => r.rule_id),
        findings,
      },
    });
  } catch (error) {
    console.error('Error fetching scan details:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to fetch scan details',
    });
  }
});

module.exports = router;
