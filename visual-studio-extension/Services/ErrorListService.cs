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

                // Build comprehensive text with all key information
                var taskText = new System.Text.StringBuilder();
                taskText.Append($"[{finding.RuleId}] {finding.Message}");
                
                if (!string.IsNullOrEmpty(finding.CWE))
                {
                    taskText.Append($" | CWE: {finding.CWE}");
                }
                if (!string.IsNullOrEmpty(finding.OWASP))
                {
                    taskText.Append($" | OWASP: {finding.OWASP}");
                }
                if (!string.IsNullOrEmpty(finding.Category))
                {
                    taskText.Append($" | Category: {finding.Category}");
                }

                var task = new ErrorTask
                {
                    Text = taskText.ToString(),
                    Document = finding.FilePath,
                    Line = Math.Max(0, finding.StartLine - 1), // VS uses 0-based indexing
                    Column = Math.Max(0, finding.StartColumn - 1),
                    ErrorCategory = errorCategory,
                    Priority = errorPriority,
                    Category = TaskCategory.BuildCompile
                };

                // Use HelpKeyword to store remediation (can be viewed in Error List details)
                if (!string.IsNullOrEmpty(finding.Remediation))
                {
                    // Store remediation in HelpKeyword (visible in Error List)
                    var remediationText = finding.Remediation.Length > 500 
                        ? finding.Remediation.Substring(0, 500) + "..." 
                        : finding.Remediation;
                    task.HelpKeyword = $"Remediation: {remediationText}";
                }
                else if (!string.IsNullOrEmpty(finding.Category))
                {
                    task.HelpKeyword = $"LLM:{finding.Category}";
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
