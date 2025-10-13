# PowerShell installation script for Windows

Write-Host "Retro Media Processing Tools - Installation Script" -ForegroundColor Green
Write-Host ""

# Check if UV is installed
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "UV is not installed. Installing UV..." -ForegroundColor Yellow
    
    # Install UV using PowerShell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Verify installation
    $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvInstalled) {
        Write-Host "Failed to install UV. Please install it manually." -ForegroundColor Red
        exit 1
    }
    Write-Host "UV installed successfully!" -ForegroundColor Green
} else {
    Write-Host "UV is already installed." -ForegroundColor Green
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
uv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
uv pip install -r requirements.txt

# Check if FFmpeg is installed
$ffmpegInstalled = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegInstalled) {
    Write-Host "FFmpeg is not installed. For full video support with audio, please install FFmpeg:" -ForegroundColor Yellow
    Write-Host "  1. Download from https://ffmpeg.org/download.html"
    Write-Host "  2. Extract the archive"
    Write-Host "  3. Add the bin folder to your system PATH"
    Write-Host ""
}

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start using the tools:"
Write-Host "1. Activate the virtual environment (if not already activated):"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "2. Run the main script:"
Write-Host "   python main.py"
Write-Host ""
Write-Host "Enjoy the Retro Media Processing Tools!" -ForegroundColor Green