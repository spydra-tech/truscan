using System;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace LLMSecurityScanner
{
    /// <summary>
    /// This is the class that implements the package exposed by this assembly.
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [Guid(LLMSecurityScannerPackage.PackageGuidString)]
    [ProvideAutoLoad(UIContextGuids80.SolutionExists, PackageAutoLoadFlags.BackgroundLoad)]
    [InstalledProductRegistration("#110", "#112", "1.0", IconResourceID = 400)]
    public sealed class LLMSecurityScannerPackage : AsyncPackage
    {
        /// <summary>
        /// LLMSecurityScannerPackage GUID string.
        /// </summary>
        public const string PackageGuidString = "A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D";

        private Services.ScannerService _scannerService;
        private Services.ErrorListService _errorListService;

        #region Package Members

        /// <summary>
        /// Initialization of the package; this method is called right after the package is sited, so this is the place
        /// where you can put all the initialization code that rely on services provided by Visual Studio.
        /// </summary>
        protected override async Task InitializeAsync(System.Threading.CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            // When initialized asynchronously, the current thread may be a background thread at this point.
            // Do any initialization that requires the UI thread after switching to the UI thread.
            await this.JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);

            // Initialize services
            _errorListService = new Services.ErrorListService(this);
            _scannerService = new Services.ScannerService(_errorListService);

            // Register commands
            await RegisterCommandsAsync();

            // Start background scanning if enabled
            await StartBackgroundScanningAsync();
        }

        private async Task RegisterCommandsAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            // Initialize command handlers
            await Commands.ScanWorkspaceCommand.InitializeAsync(this, _scannerService);
        }

        private async Task StartBackgroundScanningAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            // Subscribe to document save events
            var documentEvents = await GetServiceAsync(typeof(IVsRunningDocumentTable)) as IVsRunningDocumentTable;
            if (documentEvents != null)
            {
                // TODO: Implement document event handling for auto-scan on save
            }
        }

        #endregion
    }
}
