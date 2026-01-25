using System;

namespace LLMSecurityScanner.Models
{
    public class Finding
    {
        public string RuleId { get; set; }
        public string Message { get; set; }
        public string Severity { get; set; }
        public string Category { get; set; }
        public string FilePath { get; set; }
        public int StartLine { get; set; }
        public int StartColumn { get; set; }
        public int EndLine { get; set; }
        public int EndColumn { get; set; }
        public string Snippet { get; set; }
        public string CWE { get; set; }
        public string Remediation { get; set; }
        public string OWASP { get; set; }
    }
}
