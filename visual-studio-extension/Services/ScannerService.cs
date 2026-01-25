using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using LLMSecurityScanner.Models;
using Microsoft.VisualStudio.Shell;
using Newtonsoft.Json;

namespace LLMSecurityScanner.Services
{
    public class ScannerService
    {
        private readonly ErrorListService _errorListService;
        private string _pythonPath = "python3";
        private string _rulesDirectory = "";

        public ScannerService(ErrorListService errorListService)
        {
            _errorListService = errorListService;
        }

        public async Task<ScanResponse> ScanFileAsync(string filePath)
        {
            return await ScanPathAsync(filePath);
        }

        public async Task<ScanResponse> ScanWorkspaceAsync(string workspacePath)
        {
            return await ScanPathAsync(workspacePath);
        }

        private async Task<ScanResponse> ScanPathAsync(string path)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            try
            {
                // Build command arguments
                var args = new StringBuilder();
                args.Append("-m llm_scan.runner ");
                args.Append($"\"{path}\" ");
                args.Append("--format json ");

                if (!string.IsNullOrEmpty(_rulesDirectory))
                {
                    args.Append($"--rules \"{_rulesDirectory}\" ");
                }

                var processStartInfo = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = args.ToString(),
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8
                };

                using (var process = new Process { StartInfo = processStartInfo })
                {
                    var outputBuilder = new StringBuilder();
                    var errorBuilder = new StringBuilder();

                    process.OutputDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            outputBuilder.AppendLine(e.Data);
                        }
                    };

                    process.ErrorDataReceived += (sender, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                        {
                            errorBuilder.AppendLine(e.Data);
                        }
                    };

                    process.Start();
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();

                    await Task.Run(() => process.WaitForExit(30000)); // 30 second timeout

                    if (!process.HasExited)
                    {
                        process.Kill();
                        return new ScanResponse
                        {
                            Success = false,
                            Error = "Scanner process timed out after 30 seconds"
                        };
                    }

                    var output = outputBuilder.ToString();
                    var error = errorBuilder.ToString();

                    // Parse JSON output
                    var jsonStart = output.IndexOf('{');
                    var jsonEnd = output.LastIndexOf('}') + 1;

                    if (jsonStart != -1 && jsonEnd > 0)
                    {
                        var jsonStr = output.Substring(jsonStart, jsonEnd - jsonStart);
                        var result = JsonConvert.DeserializeObject<ScanResult>(jsonStr);

                        // Update error list
                        await _errorListService.UpdateFindingsAsync(result?.Findings ?? new System.Collections.Generic.List<Finding>());

                        return new ScanResponse
                        {
                            Success = true,
                            Result = result
                        };
                    }
                    else
                    {
                        return new ScanResponse
                        {
                            Success = false,
                            Error = $"No valid JSON output from scanner. Error: {error}"
                        };
                    }
                }
            }
            catch (Exception ex)
            {
                return new ScanResponse
                {
                    Success = false,
                    Error = $"Scanner error: {ex.Message}"
                };
            }
        }

        public void SetPythonPath(string pythonPath)
        {
            _pythonPath = pythonPath;
        }

        public void SetRulesDirectory(string rulesDirectory)
        {
            _rulesDirectory = rulesDirectory;
        }
    }
}
