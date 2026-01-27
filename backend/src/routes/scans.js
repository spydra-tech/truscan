const express = require('express');
const crypto = require('crypto');
const { db } = require('../db/connection');
const { authenticateApiKey } = require('../middleware/auth');
const Joi = require('joi');

const router = express.Router();

// Validation schema for scan results
const scanResultSchema = Joi.object({
  application_id: Joi.string().required(),
  findings: Joi.array().items(
    Joi.object({
      rule_id: Joi.string().required(),
      message: Joi.string().required(),
      severity: Joi.string().valid('critical', 'high', 'medium', 'low', 'info').required(),
      category: Joi.alternatives().try(Joi.string(), Joi.valid(null, '')).optional(),
      location: Joi.object({
        file_path: Joi.string().required(),
        start_line: Joi.number().integer().required(),
        start_column: Joi.number().integer().required(),
        end_line: Joi.number().integer().required(),
        end_column: Joi.number().integer().required(),
        snippet: Joi.alternatives().try(Joi.string(), Joi.valid(null, '')).optional(),
      }).required(),
      cwe: Joi.alternatives().try(Joi.string(), Joi.number(), Joi.valid(null, '')).optional(),
      remediation: Joi.alternatives().try(Joi.string(), Joi.valid(null, '')).optional(),
      remediation_source: Joi.string().allow(null, '').optional(),
      source: Joi.alternatives().try(Joi.string(), Joi.valid(null, '')).optional(),
      ai_filtered: Joi.boolean().allow(null).optional(),
      ai_analysis: Joi.object().allow(null).optional(),
      dataflow_path: Joi.array().allow(null).optional(),
      metadata: Joi.object().allow(null).optional(),
    })
  ).required(),
  scanned_files: Joi.array().items(Joi.string()).required(),
  rules_loaded: Joi.array().items(Joi.string()).required(),
  scan_duration_seconds: Joi.number().allow(null).optional(),
  metadata: Joi.object().allow(null).optional(),
});

/**
 * POST /api/v1/scans
 * Store scan results
 */
router.post('/', authenticateApiKey, async (req, res) => {
  try {
    // Debug: Log incoming request to check if AI analysis is present
    if (req.body.findings && req.body.findings.length > 0) {
      const findingsWithAi = req.body.findings.filter(f => f.ai_analysis);
      console.log(`Incoming request: ${req.body.findings.length} total findings, ${findingsWithAi.length} with AI analysis`);
      if (findingsWithAi.length > 0) {
        const sampleFinding = findingsWithAi[0];
        console.log('Sample finding with AI - keys:', Object.keys(sampleFinding));
        console.log('AI analysis type:', typeof sampleFinding.ai_analysis);
        console.log('AI analysis value:', JSON.stringify(sampleFinding.ai_analysis).substring(0, 300));
      } else {
        // Check if any findings have the field but it's null/empty
        const findingsWithAiField = req.body.findings.filter(f => 'ai_analysis' in f);
        console.log(`Findings with ai_analysis field (may be null): ${findingsWithAiField.length}`);
      }
    }

    // Preprocess findings to normalize optional string fields
    if (req.body.findings && Array.isArray(req.body.findings)) {
      req.body.findings = req.body.findings.map(finding => {
        // Convert cwe to string if it's a number
        if (finding.cwe !== null && finding.cwe !== undefined && typeof finding.cwe !== 'string') {
          finding.cwe = String(finding.cwe);
        }
        // Normalize other optional string fields
        if (finding.category !== null && finding.category !== undefined && typeof finding.category !== 'string') {
          finding.category = String(finding.category);
        }
        if (finding.remediation !== null && finding.remediation !== undefined && typeof finding.remediation !== 'string') {
          finding.remediation = String(finding.remediation);
        }
        if (finding.source !== null && finding.source !== undefined && typeof finding.source !== 'string') {
          finding.source = String(finding.source);
        }
        // Normalize location.snippet
        if (finding.location && finding.location.snippet !== null && finding.location.snippet !== undefined && typeof finding.location.snippet !== 'string') {
          finding.location.snippet = String(finding.location.snippet);
        }
        // Log AI analysis for debugging
        if (finding.ai_analysis) {
          console.log(`Finding ${finding.rule_id} has AI analysis:`, JSON.stringify(finding.ai_analysis).substring(0, 200));
        }
        return finding;
      });
    }

    // Validate request body with lenient options
    // Note: stripUnknown: false to preserve ai_analysis field
    const { error, value } = scanResultSchema.validate(req.body, {
      abortEarly: false,
      stripUnknown: false, // Don't strip unknown fields to preserve ai_analysis
      convert: true, // Try to convert types when possible
    });
    if (error) {
      return res.status(400).json({
        error: 'Validation error',
        details: error.details.map((d) => d.message),
      });
    }

    const {
      application_id,
      findings,
      scanned_files,
      rules_loaded,
      scan_duration_seconds,
      metadata,
    } = value;

    // Debug: Check AI analysis in validated data
    const findingsWithAi = findings.filter(f => {
      const hasAi = f.ai_analysis && typeof f.ai_analysis === 'object' && Object.keys(f.ai_analysis).length > 0;
      return hasAi;
    });
    console.log(`After validation: ${findings.length} total findings, ${findingsWithAi.length} with AI analysis`);
    if (findingsWithAi.length > 0) {
      console.log('Sample AI analysis:', JSON.stringify(findingsWithAi[0].ai_analysis).substring(0, 300));
      console.log('Sample finding keys:', Object.keys(findingsWithAi[0]));
    } else {
      // Check what's actually in the findings
      console.log('No findings with AI analysis found. Checking first finding structure:');
      if (findings.length > 0) {
        console.log('First finding keys:', Object.keys(findings[0]));
        console.log('First finding ai_analysis:', findings[0].ai_analysis);
        console.log('First finding ai_filtered:', findings[0].ai_filtered);
      }
    }

    // Verify application_id matches the authenticated API key's application
    if (application_id !== req.applicationId) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Application ID does not match the API key',
      });
    }

    // Ensure application exists
    const [appCheck] = await db.query(
      'SELECT id FROM applications WHERE application_id = ?',
      [application_id]
    );

    if (!appCheck || appCheck.length === 0) {
      // Create application if it doesn't exist
      await db.query(
        'INSERT INTO applications (application_id, name) VALUES (?, ?)',
        [application_id, application_id]
      );
    }

    // Generate scan ID
    const scanId = crypto.randomUUID();

    // Count findings by severity
    const severityCounts = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
    };

    findings.forEach((finding) => {
      const severity = finding.severity.toLowerCase();
      if (severityCounts.hasOwnProperty(severity)) {
        severityCounts[severity]++;
      }
    });

    // Start transaction (use queryRaw for transaction commands)
    await db.queryRaw('START TRANSACTION');

    try {
      // Insert scan record
      await db.query(
        `INSERT INTO scans (
          application_id, scan_id, status, scanned_files_count, rules_loaded_count,
          findings_count, critical_count, high_count, medium_count, low_count, info_count,
          scan_duration_seconds, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          application_id,
          scanId,
          'completed',
          scanned_files.length,
          rules_loaded.length,
          findings.length,
          severityCounts.critical,
          severityCounts.high,
          severityCounts.medium,
          severityCounts.low,
          severityCounts.info,
          scan_duration_seconds || 0,
          metadata ? JSON.stringify(metadata) : null,
        ]
      );

      // Insert findings
      let aiAnalysisCount = 0;
      for (const finding of findings) {
        // Check if AI analysis exists - be more lenient
        let aiAnalysisJson = null;
        if (finding.ai_analysis) {
          try {
            // Check if it's already a string (shouldn't be, but handle it)
            if (typeof finding.ai_analysis === 'string') {
              aiAnalysisJson = finding.ai_analysis;
            } else if (typeof finding.ai_analysis === 'object') {
              // Check if it has any meaningful content
              const keys = Object.keys(finding.ai_analysis);
              if (keys.length > 0) {
                aiAnalysisJson = JSON.stringify(finding.ai_analysis);
                aiAnalysisCount++;
                console.log(`Saving AI analysis for ${finding.rule_id}:`, aiAnalysisJson.substring(0, 150));
              }
            }
          } catch (error) {
            console.error(`Error stringifying AI analysis for ${finding.rule_id}:`, error);
          }
        }

        const aiFilteredValue = finding.ai_filtered === true || finding.ai_filtered === 'true' || finding.ai_filtered === 1;

        await db.query(
          `INSERT INTO findings (
            scan_id, rule_id, message, severity, category,
            file_path, start_line, start_column, end_line, end_column,
            snippet, cwe, remediation, source, ai_filtered,
            ai_analysis, dataflow_path, metadata
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            scanId,
            finding.rule_id,
            finding.message,
            finding.severity,
            finding.category || null,
            finding.location.file_path,
            finding.location.start_line,
            finding.location.start_column,
            finding.location.end_line,
            finding.location.end_column,
            finding.location.snippet || null,
            finding.cwe || null,
            finding.remediation || null,
            finding.source || 'semgrep',
            aiFilteredValue,
            aiAnalysisJson,
            finding.dataflow_path ? JSON.stringify(finding.dataflow_path) : null,
            finding.metadata ? JSON.stringify(finding.metadata) : null,
          ]
        );
      }

      console.log(`Inserted ${findings.length} findings, ${aiAnalysisCount} with AI analysis`);
      
      // Debug: Verify what was actually inserted
      if (aiAnalysisCount > 0) {
        const insertedAi = await db.query(
          'SELECT COUNT(*) as count FROM findings WHERE scan_id = ? AND ai_analysis IS NOT NULL',
          [scanId]
        );
        const count = insertedAi[0]?.count || 0;
        console.log(`Verified in DB: ${count} findings with AI analysis for scan ${scanId}`);
        
        if (count === 0) {
          console.error('⚠️ WARNING: AI analysis was processed but not saved to database!');
          // Check what's actually in the database
          const sampleFinding = await db.query(
            'SELECT rule_id, ai_analysis, ai_filtered FROM findings WHERE scan_id = ? LIMIT 1',
            [scanId]
          );
          if (sampleFinding.length > 0) {
            console.log('Sample finding from DB:', {
              rule_id: sampleFinding[0].rule_id,
              ai_analysis: sampleFinding[0].ai_analysis,
              ai_filtered: sampleFinding[0].ai_filtered
            });
          }
        }
      }

      // Insert scanned files
      for (const filePath of scanned_files) {
        await db.query(
          'INSERT INTO scanned_files (scan_id, file_path) VALUES (?, ?)',
          [scanId, filePath]
        );
      }

      // Insert rules loaded
      for (const ruleId of rules_loaded) {
        await db.query(
          'INSERT INTO rules_loaded (scan_id, rule_id) VALUES (?, ?)',
          [scanId, ruleId]
        );
      }

      // Commit transaction (use queryRaw for transaction commands)
      await db.queryRaw('COMMIT');

      res.status(201).json({
        success: true,
        scan_id: scanId,
        message: 'Scan results stored successfully',
        summary: {
          findings_count: findings.length,
          scanned_files_count: scanned_files.length,
          rules_loaded_count: rules_loaded.length,
          severity_breakdown: severityCounts,
        },
      });
    } catch (error) {
      await db.queryRaw('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('Error storing scan results:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'Failed to store scan results',
      ...(process.env.NODE_ENV === 'development' && { details: error.message }),
    });
  }
});

/**
 * GET /api/v1/scans
 * Get list of scans for the authenticated application
 */
router.get('/', authenticateApiKey, async (req, res) => {
  try {
    const { page = 1, limit = 20, severity, status } = req.query;
    const pageNum = Math.max(1, parseInt(page) || 1);
    const limitNum = Math.max(1, Math.min(100, parseInt(limit) || 20)); // Max 100 per page
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
    const [countResult] = await db.query(
      'SELECT COUNT(*) as total FROM scans WHERE application_id = ?',
      [req.applicationId]
    );
    const total = countResult[0].total;

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
 * GET /api/v1/scans/:scanId
 * Get detailed scan results
 */
router.get('/:scanId', authenticateApiKey, async (req, res) => {
  try {
    const { scanId } = req.params;

    // Get scan details
    const [scans] = await db.query(
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

    // Get findings
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
      'SELECT file_path FROM scanned_files WHERE scan_id = ?',
      [scanId]
    );

    // Get rules loaded
    const rulesLoaded = await db.query(
      'SELECT rule_id FROM rules_loaded WHERE scan_id = ?',
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
