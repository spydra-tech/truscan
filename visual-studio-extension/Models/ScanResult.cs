using System.Collections.Generic;

namespace LLMSecurityScanner.Models
{
    public class ScanResult
    {
        public List<Finding> Findings { get; set; } = new List<Finding>();
        public List<string> ScannedFiles { get; set; } = new List<string>();
        public List<string> RulesLoaded { get; set; } = new List<string>();
        public double ScanDurationSeconds { get; set; }
    }

    public class ScanResponse
    {
        public bool Success { get; set; }
        public ScanResult Result { get; set; }
        public string Error { get; set; }
    }
}
