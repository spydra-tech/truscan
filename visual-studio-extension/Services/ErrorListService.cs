using System;
using System.Collections.Generic;
using System.Linq;
using LLMSecurityScanner.Models;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio;

namespace LLMSecurityScanner.Services
{
    public class ErrorListService
    {
        private readonly Package _package;
        private ErrorListProvider _errorListProvider;

        public ErrorListService(Package package)
        {
            _package = package;
            ThreadHelper.JoinableTaskFactory.Run(async () =>
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                _errorListProvider = new ErrorListProvider(_package);
            });
        }

        public async System.Threading.Tasks.Task UpdateFindingsAsync(List<Finding> findings)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            if (_errorListProvider == null)
            {
                _errorListProvider = new ErrorListProvider(_package);
            }

            // Clear existing tasks from this provider
            _errorListProvider.Tasks.Clear();

            foreach (var finding in findings)
            {
                var errorCategory = MapSeverityToCategory(finding.Severity);
                var errorPriority = MapSeverityToPriority(finding.Severity);

                var task = new ErrorTask
                {
                    Text = $"[{finding.RuleId}] {finding.Message}",
                    Document = finding.FilePath,
                    Line = Math.Max(0, finding.StartLine - 1), // VS uses 0-based indexing
                    Column = Math.Max(0, finding.StartColumn - 1),
                    ErrorCategory = errorCategory,
                    Priority = errorPriority,
                    Category = TaskCategory.BuildCompile
                };

                // Add custom properties for detailed information
                if (!string.IsNullOrEmpty(finding.Category))
                {
                    task.HelpKeyword = $"LLM:{finding.Category}";
                }
                
                // Store additional info in task text (ErrorTask doesn't have Description property)
                var additionalInfo = new System.Text.StringBuilder();
                additionalInfo.Append($"[{finding.RuleId}] {finding.Message}");
                if (!string.IsNullOrEmpty(finding.CWE))
                {
                    additionalInfo.Append($" | CWE: {finding.CWE}");
                }
                if (!string.IsNullOrEmpty(finding.OWASP))
                {
                    additionalInfo.Append($" | OWASP: {finding.OWASP}");
                }
                if (!string.IsNullOrEmpty(finding.Remediation))
                {
                    // Add remediation as a note in the text (truncate if too long)
                    var remediationPreview = finding.Remediation.Length > 100 
                        ? finding.Remediation.Substring(0, 100) + "..." 
                        : finding.Remediation;
                    additionalInfo.Append($" | Fix: {remediationPreview}");
                }
                
                // Use custom properties to store detailed info
                task.AddCustomProperty("Rule ID", finding.RuleId);
                task.AddCustomProperty("Category", finding.Category ?? "");
                if (!string.IsNullOrEmpty(finding.CWE))
                {
                    task.AddCustomProperty("CWE", finding.CWE);
                }
                if (!string.IsNullOrEmpty(finding.OWASP))
                {
                    task.AddCustomProperty("OWASP", finding.OWASP);
                }
                if (!string.IsNullOrEmpty(finding.Remediation))
                {
                    task.AddCustomProperty("Remediation", finding.Remediation);
                }

                _errorListProvider.Tasks.Add(task);
            }

            _errorListProvider.Refresh();
        }

        private TaskErrorCategory MapSeverityToCategory(string severity)
        {
            switch (severity?.ToLower())
            {
                case "critical":
                case "high":
                    return TaskErrorCategory.Error;
                case "medium":
                    return TaskErrorCategory.Warning;
                case "low":
                case "info":
                default:
                    return TaskErrorCategory.Message;
            }
        }

        private TaskPriority MapSeverityToPriority(string severity)
        {
            switch (severity?.ToLower())
            {
                case "critical":
                    return TaskPriority.High;
                case "high":
                    return TaskPriority.Normal;
                case "medium":
                    return TaskPriority.Low;
                case "low":
                case "info":
                default:
                    return TaskPriority.Low;
            }
        }
    }
}
