using System;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using System.Windows;
using Task = System.Threading.Tasks.Task;

namespace LLMSecurityScanner.Commands
{
    /// <summary>
    /// Command handler for scanning workspace with LLM Security Scanner
    /// </summary>
    internal sealed class ScanWorkspaceCommand
    {
        public const int CommandId = 0x0100;
        public static readonly Guid CommandSet = new Guid("A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5E");

        private readonly AsyncPackage _package;
        private readonly Services.ScannerService _scannerService;

        private ScanWorkspaceCommand(AsyncPackage package, Services.ScannerService scannerService)
        {
            _package = package ?? throw new ArgumentNullException(nameof(package));
            _scannerService = scannerService ?? throw new ArgumentNullException(nameof(scannerService));
        }

        public static ScanWorkspaceCommand Instance { get; private set; }

        private Microsoft.VisualStudio.Shell.IAsyncServiceProvider ServiceProvider => _package;

        public static async Task InitializeAsync(AsyncPackage package, Services.ScannerService scannerService)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync(package.DisposalToken);

            var commandService = await package.GetServiceAsync(typeof(Microsoft.VisualStudio.OLE.Interop.IMSOleCommandTarget)) as Microsoft.VisualStudio.OLE.Interop.IMSOleCommandTarget;
            Instance = new ScanWorkspaceCommand(package, scannerService);
        }

        public async Task ExecuteAsync()
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            try
            {
                var solution = await ServiceProvider.GetServiceAsync(typeof(SVsSolution)) as IVsSolution;
                if (solution == null)
                {
                    MessageBox.Show("No solution is currently open.", "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Information);
                    return;
                }

                solution.GetSolutionInfo(out string solutionDirectory, out string solutionFile, out string userOptsFile);
                if (string.IsNullOrEmpty(solutionDirectory))
                {
                    MessageBox.Show("Unable to determine solution directory.", "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // Show status bar message
                var statusBar = await ServiceProvider.GetServiceAsync(typeof(SVsStatusbar)) as IVsStatusbar;
                statusBar?.SetText("Scanning workspace with LLM Security Scanner...");

                // Run scan asynchronously
                await Task.Run(async () =>
                {
                    var result = await _scannerService.ScanWorkspaceAsync(solutionDirectory);

                    await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (result.Success)
                    {
                        var count = result.Result?.Findings?.Count ?? 0;
                        statusBar?.SetText($"Scan complete: {count} finding(s) found");
                        if (count > 0)
                        {
                            MessageBox.Show($"Scan complete!\n\nFound {count} security finding(s).\n\nCheck the Error List for details.", 
                                "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Information);
                        }
                        else
                        {
                            MessageBox.Show("Scan complete! No security issues found.", 
                                "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Information);
                        }
                    }
                    else
                    {
                        statusBar?.SetText($"Scan failed: {result.Error}");
                        MessageBox.Show($"Scan failed:\n\n{result.Error}", 
                            "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                });
            }
            catch (Exception ex)
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                MessageBox.Show($"Error during scan: {ex.Message}", 
                    "LLM Security Scanner", MessageBoxButton.OK, MessageBoxImage.Error);
                System.Diagnostics.Debug.WriteLine($"Scan error: {ex.Message}\n{ex.StackTrace}");
            }
        }
    }
}
