# Raspberry Pi Zero 2 W Flash & SSH Setup Instructions (Linux/WSL)

**Path Placeholder Note:**
This document uses `{{Project Base Directory}}` as a placeholder for your project's base directory path.

**Example:** If your project is located at `/home/user/projects/Humidifier-Automation` or `/mnt/c/Users/gordon/source/repos/Humidifier-Automation` (WSL), then replace all instances of `{{Project Base Directory}}` with that path.

---

This guide documents the complete process for flashing Raspberry Pi OS to an SD card and enabling SSH for remote access using **Linux/WSL environments** (native bash, Ubuntu on WSL).

## Prerequisites

- SD card (16GB+ recommended)
- SD card reader
- Linux system or Windows with WSL2
- Raspberry Pi Zero 2 W

### Environment Setup

**Native Linux** - Full support for all operations
- All commands work directly
- SD cards auto-mount typically in `/media/` or `/mnt/`

**WSL (Windows Subsystem for Linux)** - Hybrid approach
- Most file operations work natively
- SD card access via `/mnt/` paths
- Some disk operations may need Windows tools

## SD Card Selection and Troubleshooting

### SD Card Requirements and Recommendations

#### Minimum Requirements for Raspberry Pi
- **Capacity**: 16GB minimum, 32GB recommended
- **Speed Class**: Class 10 (U1) minimum for basic operation
- **Interface**: microSD with SD adapter for most card readers

#### SD Card Types by Use Case

**Basic Projects (GPIO control, sensors, minimal logging)**:
- **Standard Class 10 cards**: SanDisk Ultra, Samsung EVO Select
- **Capacity**: 16-32GB sufficient
- **Write cycles**: Standard (~3,000 write/erase cycles)

**Data Logging and IoT Applications**:
- **High Endurance cards**: SanDisk MAX Endurance, Samsung Endurance PRO
- **Capacity**: 32-128GB recommended
- **Write cycles**: High endurance (~100,000 write/erase cycles)
- **Optimized for**: Continuous data writing, sensor logging

**Video Recording/Security Cameras**:
- **Video-specific cards**: SanDisk Extreme PRO, Transcend High Endurance
- **Speed Class**: V30 (30MB/s sustained write) minimum
- **Capacity**: 64-256GB for extended recording
- **Features**: Optimized for continuous video recording, temperature resistance

**Development and Frequent Updates**:
- **Premium cards**: SanDisk Extreme PRO, Lexar Professional
- **Speed Class**: U3/V30 for faster OS operations
- **Capacity**: 64GB+ for multiple OS images and development tools

### SD Card Failure Detection and Diagnosis

#### Common Symptoms of SD Card Failure
1. **Boot failures**: Pi power LED blinks in patterns, no network connection
2. **Corruption errors**: File system errors, missing files after reboot
3. **Write failures**: Cannot create files, updates fail to save
4. **Performance degradation**: Very slow file operations, timeouts
5. **Intermittent issues**: Random crashes, inconsistent behavior

#### Diagnostic Commands for SD Card Health

**Step 1: Identify SD card device** *(Native Linux)*
```bash
# List all block devices
lsblk

# Show detailed device information
sudo fdisk -l

# Look for removable devices
cat /proc/partitions
```

**Step 1: Identify SD card device** *(WSL)*
```bash
# WSL cannot directly see block devices
# Use Windows commands from WSL:
powershell.exe "wmic diskdrive where \"MediaType='Removable Media'\" get Model,Size,Status"

# Or check mounted drives
ls /mnt/
# Should show available Windows drive letters: c d e f g ...
```

**Step 2: Check SD card mount point**
```bash
# Native Linux - find where SD card is mounted
mount | grep /media
mount | grep /mnt

# WSL - SD cards accessible via Windows drive letters
ls /mnt/e/  # Replace 'e' with your SD card drive letter
```

#### SD Card Failure Resolution

**For suspected failed cards**:

1. **Basic Read/Write Test**:
   ```bash
   # Native Linux (replace /dev/sdX with your SD card device)
   sudo dd if=/dev/sdX of=/dev/null bs=4M count=100 status=progress
   
   # WSL (test via Windows drive letter)
   dd if=/mnt/e/test-file of=/dev/null bs=1M count=100 status=progress
   ```

2. **File System Check**:
   ```bash
   # Native Linux - check FAT32 partition
   sudo fsck.fat -r /dev/sdX1  # Replace X with your device letter
   
   # Native Linux - check ext4 partition  
   sudo fsck.ext4 /dev/sdX2
   
   # WSL - limited file system checking
   # Use Windows tools for full disk operations
   ```

3. **Complete Disk Wipe and Repartition** *(Native Linux)*:
   ```bash
   # WARNING: This will destroy all data on the SD card!
   # Verify device first with lsblk
   
   # Unmount all partitions
   sudo umount /dev/sdX*
   
   # Wipe partition table
   sudo dd if=/dev/zero of=/dev/sdX bs=1M count=100
   
   # Create new partition table
   sudo fdisk /dev/sdX
   # In fdisk: o (create DOS partition table), n (new partition), w (write)
   
   # Format as FAT32
   sudo mkfs.fat -F32 /dev/sdX1
   ```

### SD Card Best Practices

#### Purchase and Storage
- **Buy from reputable sources** - avoid counterfeit cards from unknown sellers
- **Store properly** - keep in anti-static cases, avoid extreme temperatures
- **Keep spares** - have backup cards for critical projects

#### Usage Patterns
- **Minimize unnecessary writes** - configure logs to tmpfs for high-frequency data
- **Use proper shutdown** - always `sudo shutdown -h now`, never just pull power
- **Regular backups** - backup working configurations before major changes
- **Monitor health** - check for file system errors periodically

#### Performance Optimization
```bash
# Reduce SD card wear - move logs to RAM (after SSH setup)
sudo nano /etc/fstab
# Add line: tmpfs /var/log tmpfs defaults,noatime 0 0
```

## Step 1: Download Raspberry Pi OS Image

### 1.1 Create Directory Structure
```bash
mkdir -p "{{Project Base Directory}}/drive-images/raspberry-pi/2025-08-09"
```
**Command explanation:**
- `mkdir` = Create directories
- `-p` = Create parent directories as needed, don't error if directory exists
- `"path"` = Directory path in quotes to handle spaces in path names

### 1.2 Download Latest Image
Download the latest Raspberry Pi OS Lite (ARM64) image:
```bash
curl -L -o "{{Project Base Directory}}/drive-images/raspberry-pi/2025-08-09/2025-05-13-raspios-bookworm-arm64-lite.img.xz" "https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/2025-05-13-raspios-bookworm-arm64-lite.img.xz"
```
**Command explanation:**
- `curl` = Command-line tool for transferring data from servers
- `-L` = Follow HTTP redirects if the server responds with a redirect
- `-o "filename"` = Save the downloaded file with this specific filename
- `"url"` = The source URL to download from

### 1.3 Extract Image
```bash
cd "{{Project Base Directory}}/drive-images/raspberry-pi/2025-08-09"
xz -d "2025-05-13-raspios-bookworm-arm64-lite.img.xz"
```
**Command explanation:**
- `cd "path"` = Change directory to the specified path
- `xz` = XZ compression/decompression utility
- `-d` = Decompress the file (extract)
- `"filename.xz"` = The compressed file to extract (removes .xz extension)

## Step 2: Flash SD Card

### 2.1 Identify SD Card Device
**Native Linux:**
```bash
# List devices before inserting SD card
lsblk

# Insert SD card, then list again to see new device
lsblk
# Look for new device, usually /dev/sdX (where X is a letter)

# Verify it's removable and correct size
sudo fdisk -l /dev/sdX  # Replace X with your device
```

**WSL:**
```bash
# WSL users should use Windows diskpart or tools
# SD card will appear as Windows drive letter (e.g., /mnt/e/)
ls /mnt/
```

### 2.2 Flash Image to SD Card

**Native Linux:**
```bash
# Unmount SD card partitions first
sudo umount /dev/sdX*  # Replace X with your device

# Flash image (WARNING: destroys all data on SD card!)
sudo dd if="{{Project Base Directory}}/drive-images/raspberry-pi/2025-08-09/2025-05-13-raspios-bookworm-arm64-lite.img" of=/dev/sdX bs=4M status=progress conv=fsync
```

**WSL:**
```bash
# WSL has limited direct disk access
# Recommended: Use Windows tools like Raspberry Pi Imager, Balena Etcher, or Win32DiskImager
# From WSL, launch Windows tools:
powershell.exe "Start-Process 'https://www.raspberrypi.org/software/' # Download Pi Imager"

# Or use diskpart via WSL (see Windows guide for detailed diskpart steps):
powershell.exe "diskpart"
```

**Command explanation:**
- `dd` = Disk duplicator - low-level copying utility
- `if="path"` = Input file - the source image file to copy from
- `of=/dev/sdX` = Output file - the SD card device
- `bs=4M` = Block size - copy 4 megabytes at a time for better performance
- `status=progress` = Show copying progress information
- `conv=fsync` = Force synchronous writes (ensure data is written before completing)

### 2.3 Sync and Remount
```bash
# Force write completion
sync

# Wait a moment, then remount to access boot partition
sudo partprobe /dev/sdX  # Native Linux
# or
sudo mount /dev/sdX1 /mnt  # Mount boot partition
```

## Step 3: Enable SSH

### 3.1 Find Boot Partition

**Native Linux:**
```bash
# Boot partition usually auto-mounts to /media/ or /mnt/
ls /media/$USER/  # Check user media directory
ls /mnt/          # Check system mount directory

# Or manually mount
sudo mkdir -p /mnt/pi-boot
sudo mount /dev/sdX1 /mnt/pi-boot  # Replace X with your device
```

**WSL:**
```bash
# Boot partition accessible via Windows drive letter
ls /mnt/e/  # Replace 'e' with your SD card drive letter

# If drive letter not visible, create mount point
sudo mkdir -p /mnt/e
```

### 3.2 Create SSH Enable File

**Native Linux:**
```bash
# Create SSH enable file on boot partition
# Method 1: If auto-mounted to /media
sudo touch /media/$USER/bootfs/ssh

# Method 2: If manually mounted
sudo touch /mnt/pi-boot/ssh

# Method 3: Find actual mount point first
mount | grep boot  # Find where boot partition is mounted
sudo touch /path/to/boot/partition/ssh  # Use actual path from above
```

**WSL:**
```bash
# Create SSH enable file via WSL path
touch /mnt/e/ssh  # Replace 'e' with your drive letter
```

**Command explanation:**
- `touch` = Create an empty file or update timestamp of existing file
- Path varies depending on where boot partition is mounted

### 3.3 Configure WiFi (Required for Pi Zero 2 W)
**IMPORTANT**: Pi Zero 2 W needs WiFi configuration to connect to your network.

**Native Linux:**
```bash
# Create WiFi configuration file on boot partition
sudo tee /media/$USER/boot/wpa_supplicant.conf << 'EOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
EOF
```

**WSL:**
```bash
# Create WiFi configuration file using WSL paths
cat > /mnt/e/wpa_supplicant.conf << 'EOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
EOF
```

**Alternative method for Native Linux:**
```bash
# Using sudo with heredoc
sudo sh -c 'cat > /mnt/pi-boot/wpa_supplicant.conf << EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
EOF'
```

**Command explanations:**
- `tee` = Write input to both stdout and file (works with sudo)
- `cat > file << 'EOF'` = Here document - input multiple lines until 'EOF'
- `sudo sh -c` = Execute shell command with sudo privileges

**Replace with your actual WiFi details:**
- `YourWiFiNetworkName` = Your WiFi network name (SSID)
- `YourWiFiPassword` = Your WiFi password

### 3.4 Verify Files Created
```bash
# Native Linux
ls -la /media/$USER/boot/ | grep -E "(ssh|wpa_supplicant)"
# or
ls -la /mnt/pi-boot/ | grep -E "(ssh|wpa_supplicant)"

# WSL
ls -la /mnt/e/ | grep -E "(ssh|wpa_supplicant)"
```

You should see both an `ssh` file and `wpa_supplicant.conf` file.

### 3.5 Safely Unmount
```bash
# Native Linux - properly unmount before removing
sudo umount /dev/sdX*  # Replace X with your device
# or
sudo umount /mnt/pi-boot

# WSL - eject via Windows
powershell.exe "eject E:"  # Replace E with your drive letter
```

## Step 4: Create Backup Images

### 4.1 Backup Original Image
```bash
cp "2025-05-13-raspios-bookworm-arm64-lite.img" "2025-05-13-raspios-bookworm-arm64-lite-ORIGINAL.img"
```

### 4.2 Create SSH-Enabled Image Backup
**Native Linux:**
```bash
# Create backup from SD card
sudo dd if=/dev/sdX of="2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img" bs=4M count=658 status=progress
```

**WSL:**
```bash
# Recommended: Use Win32DiskImager from Windows
# Launch Win32DiskImager GUI from WSL:
powershell.exe "Start-Process 'C:\\Program Files\\Win32DiskImager\\Win32DiskImager.exe'"

# Then use "Read" mode to create backup image
# Or see Windows guide for detailed backup steps using Windows tools
```

## Step 5: Boot Pi and Find IP Address

### 5.1 Setup Process Overview
**You only need ONE SD card - here's the complete workflow:**

**Preparation phase** (SD card in your computer):
1. Flash Pi OS image to SD card (Step 2)
2. Create SSH enable file on boot partition (Step 3.2) 
3. Create WiFi configuration file (Step 3.3)
4. Safely unmount SD card from computer

**Pi boot phase** (SD card in the Pi):
1. Remove SD card from computer card reader
2. Insert the **same SD card** into Raspberry Pi Zero 2 W
3. Connect Pi to power via micro USB cable
4. Pi will auto-connect to WiFi using your configuration
5. Wait 2-3 minutes for first boot and network connection

**Important**: The SD card moves FROM your computer TO the Pi. You don't need two cards!

### 5.2 Boot the Pi
1. **Safely unmount SD card** from computer
2. **Insert the same SD card** into Raspberry Pi Zero 2 W
3. **Connect power**: Use micro USB cable to power the Pi
4. **Wait for network connection**: 2-3 minutes for first boot and WiFi connection
5. **Pi will connect automatically** using the WiFi settings you created

### 5.3 Find Your Network Range
```bash
# Check your computer's network configuration
ip route | grep default  # Find your gateway
ip addr show              # Show your IP address

# Alternative
hostname -I    # Show your IP address
route -n       # Show routing table
```

### 5.4 Scan for Pi on Network
```bash
# Use nmap to scan for devices (install if needed)
sudo apt install nmap  # If not already installed

# Scan local network (adjust range as needed)
nmap -sn 192.168.1.0/24

# Look for Raspberry Pi devices
nmap -sn 192.168.1.0/24 | grep -B 2 -A 2 "Raspberry\|Pi"
```
**Command explanation:**
- `nmap` = Network mapping tool for network discovery and security auditing
- `-sn` = Ping scan (no port scan) - just check if hosts are alive
- `192.168.1.0/24` = Network range to scan (all IPs from 192.168.1.1 to 192.168.1.254)
- `grep -B 2 -A 2` = Show 2 lines before and after matching lines
- `"Raspberry\|Pi"` = Match lines containing either "Raspberry" or "Pi"

### 5.5 Check ARP Table
```bash
# View ARP table for recently contacted devices
arp -a

# Filter for your network range
arp -a | grep "192.168.1"
```

### 5.6 Try Common Pi Hostnames
```bash
ping raspberrypi.local
ping raspberrypi

# Use avahi/mDNS discovery
avahi-browse -at | grep -i raspberry
```

## Step 6: SSH Connection

### 6.1 Test Pi Connectivity
Once you have the Pi's IP address (e.g., 192.168.1.176):
```bash
ping -c 3 192.168.1.176
```
**Command explanation:**
- `ping` = Send network ping packets to test connectivity
- `-c 3` = Send exactly 3 ping packets (Linux format)
- `192.168.1.176` = Target IP address to ping

### 6.2 Connect via SSH
```bash
ssh pi@192.168.1.176
```
**Command explanation:**
- `ssh` = Secure Shell - encrypted remote connection protocol
- `pi` = Username to log in with
- `@` = Separator between username and hostname/IP
- `192.168.1.176` = IP address of the Raspberry Pi

**Default credentials:**
- Username: `pi`
- Password: `raspberry`

### 6.3 First Login Security
After first SSH login, immediately:

#### 6.3.1 Change Default Password
```bash
passwd
```

#### 6.3.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

#### 6.3.3 Additional Configuration
Configure system as needed for your specific project requirements.

## Troubleshooting

### Network and Connectivity Issues

#### Most Common: WiFi Configuration Missing
**Issue**: Pi boots but doesn't appear on network

**Solutions**:
1. **Verify WiFi file exists**: Check that `wpa_supplicant.conf` was created on boot partition
2. **Check WiFi credentials**: Ensure SSID and password are correct
3. **Network compatibility**: Ensure WiFi network is 2.4GHz (Pi Zero 2 W limitation)
4. **Monitor Pi LED**: Solid green = booting successful, blinking patterns = errors

### SSH Connection Issues

#### SSH Connection Refused
**Solutions**:
- **Verify SSH file**: Ensure empty `ssh` file exists on boot partition
- **Wait longer**: First boot can take 2-3 minutes
- **Check network**: Ensure Pi connected to WiFi
- **Try different network**: Some networks have client isolation

#### Authentication Issues
**Solutions**:
- **Default credentials**: Username `pi`, password `raspberry`
- **Fresh flash**: If password was previously changed, reflash SD card

### SD Card Access Issues (WSL)

#### Cannot Access SD Card
**Solutions**:
```bash
# Check available mounts
ls /mnt/

# Create mount point if missing
sudo mkdir -p /mnt/e

# Check Windows drive assignment
powershell.exe "Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, MediaType, Size"
```

## Files Created

After following this guide, you should have:

```
{{Project Base Directory}}/drive-images/raspberry-pi/2025-08-09/
├── 2025-05-13-raspios-bookworm-arm64-lite-ORIGINAL.img    # Original backup
├── 2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img # SSH-enabled backup
└── 2025-05-13-raspios-bookworm-arm64-lite.img            # Working copy
```

## Security Notes

- **Always change the default password** after first login
- Consider disabling password authentication and using SSH keys
- Keep the system updated with `sudo apt update && sudo apt upgrade`
- Consider changing the default `pi` username for better security

## Next Steps

Once SSH is working:
1. Copy relay test scripts to the Pi
2. Install required Python packages
3. Run relay self-test program
4. Configure Pi as needed for your project

---

*Last updated: 2025-08-09*  
*Tested with: Raspberry Pi Zero 2 W, Raspberry Pi OS Lite (2025-05-13)*
*Linux Environment: Native Linux, WSL2 Ubuntu*