# Check if Python is installed
if (!(Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Output "Python is not installed. Installing Python 3.12..."
    $pythonInstaller = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    Invoke-WebRequest -Uri $pythonInstaller -OutFile "$env:TEMP\python_installer.exe"
    Start-Process -FilePath "$env:TEMP\python_installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
}

# Check if pip is installed
if (!(Get-Command "pip" -ErrorAction SilentlyContinue)) {
    Write-Output "Pip is not installed. Installing pip..."
    python -m ensurepip --upgrade
}

# Install necessary packages
Write-Output "Installing Python packages..."
pip install urllib3 mitmproxy json

Write-Output "VirtualBox setup complete. You can now run retrieve_params."
