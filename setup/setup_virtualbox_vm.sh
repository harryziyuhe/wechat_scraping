#!/bin/bash

# Define Variables
VBOX_VERSION="6.1.26"
VM_NAME="WindowsVM"
REPO_DIR=$(dirname $(dirname "$0"))  # Automatically set repository directory as one level up from the script
ISO_URL="https://software-download.microsoft.com/db/Win10_21H1_English_x64.iso"  # Windows 10 ISO URL (example)
ISO_FILE="$REPO_DIR/Windows10.iso"
SHARED_FOLDER="$REPO_DIR"

# Function to display information for Windows users
inform_windows_users() {
    echo "###################################################################"
    echo "You are using Windows. Please follow these steps to set up VirtualBox:"
    echo "1. Download and install VirtualBox from: https://www.virtualbox.org/wiki/Downloads"
    echo "2. Download a Windows ISO from: https://www.microsoft.com/en-us/software-download/windows10"
    echo "3. Set up a shared folder with this repository directory."
    echo "4. Manually run the Windows VM and continue setup inside it."
    echo "###################################################################"
    exit 0
}

# Function to install VirtualBox on Linux
install_virtualbox_linux() {
    echo "Installing VirtualBox on Linux..."
    sudo apt-get update
    sudo apt-get install -y virtualbox
}

# Function to install VirtualBox on macOS
install_virtualbox_macos() {
    echo "Installing VirtualBox on macOS..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found, installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install --cask virtualbox
}

# Function to download Windows ISO
download_windows_iso() {
    if [[ ! -f "$ISO_FILE" ]]; then
        echo "Downloading Windows ISO..."
        curl -o "$ISO_FILE" "$ISO_URL"
        echo "Windows ISO downloaded at $ISO_FILE."
    else
        echo "Windows ISO already exists at $ISO_FILE."
    fi
}

# Function to set up the VirtualBox VM
setup_virtualbox_vm() {
    echo "Creating VirtualBox VM..."

    # Create the VM
    VBoxManage createvm --name $VM_NAME --ostype "Windows10_64" --register

    # Configure the VM
    VBoxManage modifyvm $VM_NAME --memory 4096 --vram 128 --cpus 2 --nic1 nat --audio none --usb on --usbehci on

    # Create and attach storage
    VM_FOLDER="$HOME/VirtualBox VMs/$VM_NAME"
    VM_DISK="$VM_FOLDER/$VM_NAME.vdi"
    VBoxManage createmedium disk --filename $VM_DISK --size 50000
    VBoxManage storagectl $VM_NAME --name "SATA Controller" --add sata --controller IntelAhci
    VBoxManage storageattach $VM_NAME --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium $VM_DISK

    # Attach Windows ISO
    VBoxManage storageattach $VM_NAME --storagectl "SATA Controller" --port 1 --device 0 --type dvddrive --medium $ISO_FILE

    # Setup boot order
    VBoxManage modifyvm $VM_NAME --boot1 dvd --boot2 disk

    # Add shared folder
    VBoxManage sharedfolder add $VM_NAME --name "shared_folder" --hostpath "$SHARED_FOLDER" --automount

    echo "VirtualBox VM created and configured."
}

# Main function to be called by the entry point
main() {
    OS="$(uname -s)"
    case "$OS" in
        Linux)
            install_virtualbox_linux
            ;;
        Darwin)
            install_virtualbox_macos
            ;;
        CYGWIN*|MINGW*|MSYS*|win32)
            inform_windows_users
            ;;
        *)
            echo "Unsupported operating system. Please install VirtualBox manually."
            exit 1
            ;;
    esac

    # Download Windows ISO
    download_windows_iso

    # Set up VirtualBox VM
    setup_virtualbox_vm
}

# If the script is run directly, call the main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
