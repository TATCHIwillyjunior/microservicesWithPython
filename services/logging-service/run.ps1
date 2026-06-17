# Logging Service Startup Script (PowerShell)
# Usage: ./run.ps1

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Run the service
Write-Host "Starting logging-service on port 8006..."
flask run --port 8006
