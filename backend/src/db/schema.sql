-- LLM Security Scanner Database Schema

-- Create database (run this manually if needed)
-- CREATE DATABASE IF NOT EXISTS llm_scan_db;
-- USE llm_scan_db;

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_application_id (application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
  id INT AUTO_INCREMENT PRIMARY KEY,
  api_key VARCHAR(255) UNIQUE NOT NULL,
  application_id VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  last_used_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NULL,
  FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
  INDEX idx_api_key (api_key),
  INDEX idx_application_id (application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scans table
CREATE TABLE IF NOT EXISTS scans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id VARCHAR(255) NOT NULL,
  scan_id VARCHAR(255) UNIQUE NOT NULL,
  status ENUM('pending', 'completed', 'failed') DEFAULT 'completed',
  scanned_files_count INT DEFAULT 0,
  rules_loaded_count INT DEFAULT 0,
  findings_count INT DEFAULT 0,
  critical_count INT DEFAULT 0,
  high_count INT DEFAULT 0,
  medium_count INT DEFAULT 0,
  low_count INT DEFAULT 0,
  info_count INT DEFAULT 0,
  scan_duration_seconds DECIMAL(10, 3),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE CASCADE,
  INDEX idx_application_id (application_id),
  INDEX idx_scan_id (scan_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Findings table
CREATE TABLE IF NOT EXISTS findings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  scan_id VARCHAR(255) NOT NULL,
  rule_id VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  severity ENUM('critical', 'high', 'medium', 'low', 'info') NOT NULL,
  category VARCHAR(100),
  file_path VARCHAR(1000) NOT NULL,
  start_line INT NOT NULL,
  start_column INT NOT NULL,
  end_line INT NOT NULL,
  end_column INT NOT NULL,
  snippet TEXT,
  cwe VARCHAR(50),
  remediation TEXT,
  source VARCHAR(50) DEFAULT 'semgrep',
  ai_filtered BOOLEAN DEFAULT FALSE,
  ai_analysis JSON,
  dataflow_path JSON,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE,
  INDEX idx_scan_id (scan_id),
  INDEX idx_rule_id (rule_id),
  INDEX idx_severity (severity),
  INDEX idx_file_path (file_path(255)),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scanned Files table (for tracking which files were scanned)
CREATE TABLE IF NOT EXISTS scanned_files (
  id INT AUTO_INCREMENT PRIMARY KEY,
  scan_id VARCHAR(255) NOT NULL,
  file_path VARCHAR(1000) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE,
  INDEX idx_scan_id (scan_id),
  INDEX idx_file_path (file_path(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rules Loaded table (for tracking which rules were used)
CREATE TABLE IF NOT EXISTS rules_loaded (
  id INT AUTO_INCREMENT PRIMARY KEY,
  scan_id VARCHAR(255) NOT NULL,
  rule_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE,
  INDEX idx_scan_id (scan_id),
  INDEX idx_rule_id (rule_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
