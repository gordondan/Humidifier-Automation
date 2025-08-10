# Raspberry Pi Zero 2 W Flash & SSH Setup Instructions

This guide documents the complete process for flashing Raspberry Pi OS to an SD card and enabling SSH for remote access.

## Prerequisites

- SD card (16GB+ recommended)
- SD card reader
- Windows PC with internet connection
- Raspberry Pi Zero 2 W

### Shell Environment Requirements

**This guide assumes you are using a bash-compatible shell on Windows. You have several options:**

1. **Git Bash** - **Recommended for this guide**
   - Installed with Git for Windows
   - All Windows commands (wmic, diskpart, dd) work directly
   - Path format: `/c/Users/gordon/source/repos/...`
   - Best compatibility with Windows disk operations

2. **Windows Subsystem for Linux (WSL)** - **Good for development, limited for disk ops**
   - Install WSL2 with Ubuntu: `wsl --install`
   - **Limitation**: Cannot access Windows disk management commands (wmic, diskpart)
   - **Limitation**: SD cards don't auto-mount in WSL
   - Path format: `/mnt/c/Users/gordon/source/repos/...`
   - **For this guide**: Use WSL for file operations, but run disk commands in PowerShell/CMD

3. **PowerShell/Command Prompt**
   - All Windows disk commands work natively
   - Some bash-style commands need adaptation
   - Path format: `C:\Users\gordon\source\repos\...`

## Command Environment Guide

**Commands that MUST run in Windows (PowerShell/CMD/Git Bash - NOT WSL):**
- `wmic` commands (disk identification)
- `diskpart` (disk partitioning) 
- `dd` (image flashing to SD cards)
- SD card file operations (`echo. > E:\ssh`, creating files on drive letters)

**Commands that work in any environment:**
- `mkdir`, `cd`, `ls`, `cp` (file operations)
- `curl` (downloads)
- `ping`, `ssh` (network operations)

**WSL-specific notes:**
- SD cards don't auto-mount in `/mnt/` by default
- You can manually mount them or use `/mnt/e/` paths directly
- Some Windows disk commands (wmic, diskpart) must run in Windows shells
- File operations on SD cards work once paths are correct

### WSL SD Card Access

**Option 1: Direct path access (easiest)**
```bash
# WSL can access Windows drives directly via /mnt/ paths
touch /mnt/e/ssh
ls /mnt/e/
```

**Option 2: Manual mounting (if direct access doesn't work)**
```bash
# Create mount point
sudo mkdir -p /mnt/sdcard

# Mount the SD card (replace /dev/sde1 with actual device)
sudo mount -t drvfs E: /mnt/sdcard

# Now you can access it
touch /mnt/sdcard/ssh
ls /mnt/sdcard/
```

**Option 3: Check what's available**
```bash
# See what drives are accessible
ls /mnt/
# Should show: c d e (and others)

# If your SD card drive letter doesn't appear:
sudo mkdir /mnt/e
```

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

**Check SD card before flashing**:

**Step 1: Identify the physical SD card** *(Run in PowerShell/CMD/Git Bash - NOT WSL)*
```bash
# Find removable drives (this shows the physical device)
wmic diskdrive where "MediaType='Removable Media'" get Model,Size,Status
```

**Step 2: Find the drive letter for the SD card** *(Run in PowerShell/CMD/Git Bash - NOT WSL)*
```bash
# List all logical drives with their sizes
wmic logicaldisk get size,freespace,caption
```

**Understanding the size differences:**
- **Physical drive size** (from diskdrive): Total capacity of the SD card (e.g., 15,924,142,080 bytes = ~15GB)
- **Logical drive size** (from logicaldisk): Formatted partition size on the card (smaller due to formatting overhead)

**Step 3: Match drive letter to your SD card**
Look for the logical drive that:
1. **Appeared after inserting your SD card** (compare before/after insertion)
2. **Has a size that makes sense for your card** (e.g., ~250MB for Pi boot partition, or full card size if not yet flashed)
3. **Is removable** (try safely ejecting it - only removable drives will show eject option)

**Pro tip for drive letter identification** *(Run in PowerShell/CMD/Git Bash)*:
```bash
# Before inserting SD card, run:
wmic logicaldisk get caption

# After inserting SD card, run the same command
# The new drive letter that appears is your SD card
```

**Alternative methods if WMIC doesn't work:**
```bash
# Method 1: PowerShell drive identification (run directly in PowerShell)
Get-WmiObject -Class Win32_DiskDrive | Where-Object {$_.MediaType -eq 'Removable Media'} | Select-Object Model, Status, Size

# Method 2: Use diskpart for detailed drive info (run as Administrator)
echo "list disk" | diskpart
```

**Verify SD card integrity after flashing**:
```bash
# Basic read test - verify the image can be read back
dd if=\\.\F: of=/dev/null bs=4M count=100 status=progress
```
**Command explanation:**
- `dd` = Disk duplicator for low-level operations
- `if=\\.\F:` = Input from SD card (Windows device format)
- `of=/dev/null` = Output to null (discard data, just test reading)
- `bs=4M` = Read 4MB blocks
- `count=100` = Test first 400MB for quick verification
- `status=progress` = Show read progress

#### SD Card Failure Resolution

**For suspected failed cards**:

1. **Quick Format Test**:
   ```bash
   # Format as FAT32 to test basic write capability
   powershell -Command "Format-Volume -DriveLetter F -FileSystem FAT32 -Force"
   ```
   If format fails → Try diskpart method below before assuming card failure

2. **Advanced Recovery with Diskpart** *(Most Effective Method)*:

   **When to use diskpart**:
   - Windows shows wrong card capacity (e.g., 2GB instead of 16GB)
   - Multiple strange drive letters appear from one SD card
   - Standard format fails with "device not ready" errors
   - Card has corrupted partition table from previous Pi installations

   **Step-by-step diskpart recovery**:
   
   ⚠️ **CRITICAL SAFETY WARNING**: Diskpart can wipe any drive. Double-check disk numbers!

   ```bash
   # Step 1: Identify your SD card safely
   wmic diskdrive get Index,Model,Size,MediaType
   # Note which Index number is your SD card (usually highest number, removable media)
   
   # Step 2: Verify by removing/reinserting card
   # Remove SD card, run command again - your card's Index should disappear
   # Reinsert SD card, run command again - your card's Index should reappear
   
   # Step 3: Run diskpart (requires Administrator privileges)
   diskpart
   ```

   **In diskpart console**:
   ```
   DISKPART> list disk
   # Verify your SD card shows with correct size
   # Example output:
   #   Disk 0    Online    953 GB     0 B        (your main drive - DON'T TOUCH)
   #   Disk 1    Online     14 GB     0 B        (your SD card)
   
   DISKPART> select disk 1
   # REPLACE "1" with your actual SD card disk number!
   # Should show: "Disk 1 is now the selected disk."
   
   DISKPART> clean
   # Removes all partitions and formatting
   
   DISKPART> create partition primary
   # Creates new primary partition using full disk
   
   DISKPART> active
   # Marks partition as active (bootable)
   
   DISKPART> format fs=fat32 quick
   # Formats as FAT32 file system
   
   DISKPART> assign
   # Assigns a drive letter automatically
   
   DISKPART> exit
   ```

   **Expected results**:
   - Card should now show full capacity in Windows Explorer
   - Single drive letter instead of multiple fragments
   - Ready for Pi OS flashing

   **Command explanations**:
   - `list disk` = Show all physical drives with their disk numbers
   - `select disk X` = Choose which disk to operate on (CRITICAL to get right!)
   - `clean` = Completely wipe all partitions and boot sectors
   - `create partition primary` = Create one partition using entire disk
   - `active` = Mark partition as bootable
   - `format fs=fat32 quick` = Format with FAT32 file system
   - `assign` = Let Windows assign a drive letter automatically

3. **Write/Read Verification** (after diskpart recovery):
   ```bash
   # Create test file on recovered card
   echo "test" > /f/test.txt
   # Verify file contents
   cat /f/test.txt
   ```
   If contents don't match or file is corrupted → Card hardware is actually failing

4. **Multiple Format Cycles** (last resort):
   - Some cards can be recovered with multiple format cycles
   - Try 2-3 format cycles if other methods fail
   - **Warning**: This is temporary at best - replace card soon

#### When to Replace SD Cards

**Immediate replacement needed**:
- Cannot format or partition the card
- Repeated boot failures with multiple known-good images
- File system corruption occurs frequently
- Card becomes read-only unexpectedly

**Plan replacement soon**:
- Slower than expected performance (>5x slower than rated speed)
- Occasional file corruption or write errors
- Card is >2-3 years old with heavy use
- Starting to show warning signs but still functional

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

### Emergency Recovery Procedures

#### Card Partially Responsive
1. **Immediate backup** - clone entire card before attempting fixes:
   ```bash
   dd if=\\.\F: of="emergency-backup-$(date +%Y%m%d).img" bs=4M status=progress
   ```

2. **File system check** (Linux/WSL only):
   ```bash
   sudo fsck.fat -r /dev/sdX1  # Replace X with actual device
   ```

#### Complete Card Failure During Project
1. **Keep emergency backup image ready** - always maintain recent working image
2. **Flash to new card immediately**:
   ```bash
   dd if="last-known-good-backup.img" of=\\.\F: bs=4M status=progress
   ```
3. **Update system** and recreate recent changes from notes

## Step 1: Download Raspberry Pi OS Image

### 1.1 Create Directory Structure
```bash
mkdir -p "C:\Users\gordon\source\repos\Humidifiers\drive-images\raspberry-pi\2025-08-09"
```
**Command explanation:**
- `mkdir` = Create directories
- `-p` = Create parent directories as needed, don't error if directory exists
- `"path"` = Directory path in quotes to handle spaces in path names

### 1.2 Download Latest Image
Download the latest Raspberry Pi OS Lite (ARM64) image:
```bash
curl -L -o "C:\Users\gordon\source\repos\Humidifiers\drive-images\raspberry-pi\2025-08-09\2025-05-13-raspios-bookworm-arm64-lite.img.xz" "https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/2025-05-13-raspios-bookworm-arm64-lite.img.xz"
```
**Command explanation:**
- `curl` = Command-line tool for transferring data from servers
- `-L` = Follow HTTP redirects if the server responds with a redirect
- `-o "filename"` = Save the downloaded file with this specific filename
- `"url"` = The source URL to download from

### 1.3 Extract Image
```bash
cd "C:\Users\gordon\source\repos\Humidifiers\drive-images\raspberry-pi\2025-08-09"
xz -d "2025-05-13-raspios-bookworm-arm64-lite.img.xz"
```
**Command explanation:**
- `cd "path"` = Change directory to the specified path
- `xz` = XZ compression/decompression utility
- `-d` = Decompress the file (extract)
- `"filename.xz"` = The compressed file to extract (removes .xz extension)

## Step 2: Flash SD Card

### 2.1 Format SD Card (Optional)
If needed, format the SD card as FAT32:
```bash
powershell -Command "Format-Volume -DriveLetter F -FileSystem FAT32 -Force"
```
**Command explanation:**
- `powershell -Command` = Execute a PowerShell command from bash
- `Format-Volume` = PowerShell cmdlet to format storage volumes
- `-DriveLetter F` = Specify which drive to format (replace F with your SD card's drive letter)
- `-FileSystem FAT32` = Format as FAT32 file system
- `-Force` = Skip confirmation prompts and force the operation

### 2.2 Flash Image to SD Card
**⚠️ Warning: This will erase all data on the SD card!**
```bash
dd if="C:\Users\gordon\source\repos\Humidifiers\drive-images\raspberry-pi\2025-08-09\2025-05-13-raspios-bookworm-arm64-lite.img" of=\\.\F: bs=4M status=progress
```
**Command explanation:**
- `dd` = Disk duplicator - low-level copying utility
- `if="path"` = Input file - the source image file to copy from
- `of=\\.\F:` = Output file - Windows device path format for drive F:
- `bs=4M` = Block size - copy 4 megabytes at a time for better performance
- `status=progress` = Show copying progress information

Replace `F:` with your actual SD card drive letter.

## Step 3: Enable SSH

### 3.1 Identify Boot Partition Drive Letter
After flashing, Windows will automatically mount the Pi's boot partition. **The drive letter can vary** (D:, E:, G:, etc.) depending on your system.

**Find the correct drive letter:**
```bash
wmic logicaldisk get size,freespace,caption
```
**Command explanation:**
- `wmic` = Windows Management Instrumentation Command-line utility
- `logicaldisk` = Query information about logical disk drives
- `get` = Retrieve specific properties
- `size,freespace,caption` = Show drive size, available space, and drive letter

Look for a small drive (~250MB) that appeared after flashing. This is the boot partition.

### 3.2 Create SSH Enable File
Create an empty `ssh` file on the boot partition (replace `E:` with your actual drive letter):

**Method 1: Windows Command Prompt/PowerShell** *(Recommended)*
```cmd
# Using echo (works in CMD and PowerShell)
echo. > E:\ssh
```

**Method 2: PowerShell**
```powershell
New-Item -Path "E:\ssh" -ItemType File
```

**Method 3: Git Bash** *(Unix-style paths work in Git Bash)*
```bash
touch /e/ssh
```

**Method 4: WSL Users**
```bash
# Option A: Direct path access (try this first)
touch /mnt/e/ssh

# Option B: If drive not auto-mounted, create mount point first
sudo mkdir -p /mnt/e
touch /mnt/e/ssh

# Option C: Manual mount (if above don't work)
sudo mkdir -p /mnt/sdcard
sudo mount -t drvfs E: /mnt/sdcard
touch /mnt/sdcard/ssh

# Verify file was created
ls -la /mnt/e/ | grep ssh
```

**Command explanations:**
- `echo.` = Output an empty line to create file
- `>` = Redirect output to create a file
- `New-Item` = PowerShell cmdlet to create new items (files/folders)
- `-Path` = Specify the location and name
- `-ItemType File` = Create a file (not a directory)
- `touch` = Unix/Linux command (only works in Git Bash on Windows)

### 3.3 Configure WiFi (Required for Pi Zero 2 W)
**IMPORTANT**: Pi Zero 2 W needs WiFi configuration to connect to your network. Create a `wpa_supplicant.conf` file on the boot partition:

**Method 1: Windows Command Prompt/PowerShell** *(Recommended)*
```cmd
# Create WiFi configuration file (replace E: with your drive letter)
(
echo country=US
echo ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
echo update_config=1
echo.
echo network={
echo     ssid="YourWiFiNetworkName"
echo     psk="YourWiFiPassword"
echo }
) > E:\wpa_supplicant.conf
```

**Method 2: PowerShell**
```powershell
$wifiConfig = @"
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
"@

$wifiConfig | Out-File -FilePath "E:\wpa_supplicant.conf" -Encoding ASCII
```

**Method 3: Git Bash** *(Unix-style here document)*
```bash
# Create WiFi configuration file (replace E: with your drive letter)
cat > /e/wpa_supplicant.conf << 'EOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
EOF
```

**Method 4: WSL Users**
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

# If /mnt/e/ doesn't exist, create mount point first:
# sudo mkdir -p /mnt/e

# Or use manual mount:
# sudo mount -t drvfs E: /mnt/sdcard
# cat > /mnt/sdcard/wpa_supplicant.conf << 'EOF'
# [content as above]
# EOF
```

**Command explanations:**
- `echo` = Output text to console
- `>` = Redirect all output to create a file  
- `echo.` = Output a blank line
- `cat` = Display or concatenate files (Git Bash only)
- `<< 'EOF'` = Here document - input multiple lines until 'EOF' (Git Bash only)
- `Out-File` = PowerShell cmdlet to write to file

**Replace with your actual WiFi details:**
- `YourWiFiNetworkName` = Your WiFi network name (SSID)
- `YourWiFiPassword` = Your WiFi password

**Alternative using PowerShell:**
```powershell
$wifiConfig = @"
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiNetworkName"
    psk="YourWiFiPassword"
}
"@

$wifiConfig | Out-File -FilePath "E:\wpa_supplicant.conf" -Encoding ASCII
```

### 3.4 Verify SSH File
Check that the file was created (replace `E:` with your drive letter):
```bash
ls E:\
```
**Command explanation:**
- `ls` = List directory contents
- `E:\` = Windows-style path to list contents of drive E:

You should see an `ssh` file and `wpa_supplicant.conf` file in the listing along with other boot files like `config.txt` and various `.dtb` files.

## Step 4: Create Backup Images

### 4.1 Backup Original Image
```bash
cp "2025-05-13-raspios-bookworm-arm64-lite.img" "2025-05-13-raspios-bookworm-arm64-lite-ORIGINAL.img"
```
**Command explanation:**
- `cp` = Copy files or directories
- `"source"` = The original file to copy from
- `"destination"` = The new filename for the copy

### 4.2 Create SSH-Enabled Image Backup
```bash
dd if=\\.\F: of="2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img" bs=4M count=658 status=progress
```
**Command explanation:**
- `dd` = Disk duplicator - low-level copying utility
- `if=\\.\F:` = Input file - read from SD card drive F: (Windows device format)
- `of="filename"` = Output file - save to this image file
- `bs=4M` = Block size - process 4 megabytes at a time
- `count=658` = Copy only 658 blocks (limits backup to ~2.6GB for Pi OS)
- `status=progress` = Show copying progress information

## Step 5: Boot Pi and Find IP Address

### 5.1 Setup Process Overview
**You only need ONE SD card - here's the complete workflow:**

**Preparation phase** (SD card in your computer):
1. Flash Pi OS image to SD card (Step 2)
2. Create SSH enable file on boot partition (Step 3.2) 
3. Create WiFi configuration file (Step 3.3)
4. Safely eject SD card from computer

**Pi boot phase** (SD card in the Pi):
1. Remove SD card from computer card reader
2. Insert the **same SD card** into Raspberry Pi Zero 2 W
3. Connect Pi to power via micro USB cable
4. Pi will auto-connect to WiFi using your configuration
5. Wait 2-3 minutes for first boot and network connection

**Important**: The SD card moves FROM your computer TO the Pi. You don't need two cards!

**Network Connection Options:**
- **WiFi**: Pi will auto-connect if WiFi credentials are configured in `wpa_supplicant.conf`
- **USB-Ethernet**: Use a USB-to-Ethernet adapter if available
- **USB Gadget Mode**: Advanced - Pi Zero can act as USB network device

### 5.2 Boot the Pi
1. **Safely eject SD card** from computer (right-click → Eject)
2. **Insert the same SD card** into Raspberry Pi Zero 2 W
3. **Connect power**: Use micro USB cable to power the Pi
4. **Wait for network connection**: 2-3 minutes for first boot and WiFi connection
5. **Pi will connect automatically** using the WiFi settings you created

### 5.2 Find Router IP Address
Get your computer's network configuration:
```bash
ipconfig
```
**Command explanation:**
- `ipconfig` = Display network adapter configuration on Windows
- Look for "Default Gateway" - this is your router's IP (e.g., 192.168.1.1)

### 5.3 Access Router Admin Page
Open your router's admin interface in a web browser:
- For Google Fiber routers: `http://192.168.86.1` or `http://192.168.1.1`
- Generic: `http://192.168.1.1` or `http://192.168.0.1`

Look for "Connected Devices" or similar to find your Pi's IP address.

### 5.4 Alternative: Use ARP Table
Check your computer's ARP table to find devices on your network:
```bash
arp -a | findstr "192.168.1"
```
**Command explanation:**
- `arp` = Display and modify ARP (Address Resolution Protocol) table
- `-a` = Show all ARP entries for all interfaces
- `|` = Pipe output to another command
- `findstr "192.168.1"` = Windows grep equivalent - find lines containing "192.168.1"

This shows all devices your computer has recently communicated with on the 192.168.1.x network.

### 5.5 Alternative: Network Scanning
Quick ping scan (replace range as needed):
```bash
for i in {1..10}; do ping -c 1 -W 1 192.168.1.$i 2>/dev/null | grep "1 received" && echo "192.168.1.$i is up"; done
```
**Command explanation:**
- `for i in {1..10}` = Loop variable i from 1 to 10
- `do...done` = Execute commands within the loop
- `ping` = Send network ping packets
- `-c 1` = Send only 1 ping packet
- `-W 1` = Wait 1 second for response
- `192.168.1.$i` = IP address with variable substitution
- `2>/dev/null` = Redirect error messages to null (suppress errors)
- `|` = Pipe output to next command
- `grep "1 received"` = Filter for successful ping responses
- `&&` = Execute next command only if previous succeeded
- `echo` = Print message showing which IP is responding

### 5.6 Try Common Pi Hostnames
```bash
ping raspberrypi.local
ping raspberrypi
```
**Command explanation:**
- `ping` = Send network ping packets
- `raspberrypi.local` = mDNS hostname (multicast DNS for local discovery)
- `raspberrypi` = Standard hostname without domain suffix

## Step 6: SSH Connection

### 6.1 Test Pi Connectivity
Once you have the Pi's IP address (e.g., 192.168.1.176):
```bash
ping -n 3 192.168.1.176
```
**Command explanation:**
- `ping` = Send network ping packets to test connectivity
- `-n 3` = Send exactly 3 ping packets (Windows format)
- `192.168.1.176` = Target IP address to ping

**Note**: Use `ping 192.168.1.176` (just the IP), NOT `ping pi@192.168.1.176`. The `pi@` part is only for SSH connections.

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
**Command explanation:**
- `passwd` = Change user password command
- System will prompt for current password, then new password twice

#### 6.3.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
```
**Command explanation:**
- `sudo` = Execute command with administrator privileges
- `apt update` = Refresh package repository information
- `&&` = Execute next command only if previous succeeded
- `apt upgrade -y` = Install available package upgrades
- `-y` = Automatically answer "yes" to upgrade prompts

#### 6.3.3 Additional Configuration
Configure system as needed for your specific project requirements.

## Troubleshooting

### Network and Connectivity Issues

#### Most Common: WiFi Configuration Missing
**Issue**: "I have SD card in reader AND Pi plugged in, but can't ping the Pi"

**Root Cause**: The Pi Zero 2 W connects via WiFi, not through the USB cable to your computer. The USB cable only provides power.

**Solution Steps**:
1. Ensure you created `wpa_supplicant.conf` with your WiFi credentials
2. Verify the SD card is IN THE PI, not in your computer
3. Wait 2-3 minutes for Pi to boot and connect to WiFi
4. Find the Pi's IP using ARP table or router admin page

#### Can't Find Pi on Network
**Symptoms**: Pi seems to boot but doesn't appear on network

**Solutions in order of likelihood**:
1. **Missing WiFi configuration** - create `wpa_supplicant.conf` file
2. **Wrong network range** - try different IP ranges (192.168.0.x vs 192.168.1.x)
3. **WiFi band compatibility** - ensure network is 2.4GHz (Pi Zero 2 W may not support 5GHz)
4. **Network restrictions** - check if WiFi network has MAC address filtering enabled
5. **Hardware indicators** - verify Pi power LED is solid (not blinking)
6. **Credential errors** - double-check WiFi network name and password are correct

**Diagnostic Commands**:
```bash
# Check router admin page for connected devices
# Access via browser: http://192.168.1.1 (or your router IP)

# Check ARP table for recently connected devices
arp -a | findstr "192.168.1"
```

#### Pi Not Getting IP Address
**Advanced Troubleshooting**:
1. **WiFi Configuration**: Verify `wpa_supplicant.conf` exists with correct credentials
2. **Network Band**: Check WiFi network is 2.4GHz compatible
3. **Direct Configuration**: Connect monitor/keyboard for direct configuration
4. **Network Security**: Check for MAC address filtering or network isolation

### SSH and Authentication Issues

#### SSH Connection Refused
**Possible Causes and Solutions**:
- **SSH not enabled**: Verify `ssh` file exists on boot partition
- **Pi not booted**: Check Pi has powered on and connected to network
- **Timing**: Wait longer - first boot takes 2-3 minutes
- **File corruption**: Try re-flashing SD card with SSH file

#### Wrong Credentials
**Issue**: Authentication failures during SSH login

**Solutions**:
- **Default credentials**: Username `pi`, password `raspberry`
- **Previously changed**: If password was changed before, you may need to re-flash SD card
- **Typing errors**: Ensure correct case and spelling

### SD Card Hardware Issues

#### SD Card Size Limitations and Compatibility

**Raspberry Pi SD Card Support**:
- **Maximum supported**: 2TB (theoretical, limited by SDHC/SDXC standards)
- **Practical recommendation**: 512GB or smaller for best compatibility
- **File system**: Pi boot requires FAT32 for boot partition (32GB limit for native Windows formatting)

**Size-Specific Issues**:
- **Cards >32GB**: May need manual formatting to FAT32 for Windows compatibility
- **Cards >128GB**: Some older Pi models may have compatibility issues
- **Cards >512GB**: Diminishing returns for most projects, higher failure risk

**Formatting Large Cards for Pi Compatibility**:
```bash
# For cards >32GB that need FAT32 boot partition (use diskpart as Administrator)
diskpart
```

**In diskpart console** (see detailed diskpart instructions in "SD Card Failure Resolution" section):
```
list disk
select disk X    (where X is your SD card - verify carefully!)
clean
create partition primary
active
format fs=fat32 quick
assign
exit
```

**⚠️ Safety reminder**: Always verify disk number with `wmic diskdrive get Index,Model,Size,MediaType` first!

#### Performance vs Capacity Trade-offs

**16-32GB Cards**:
- **Pros**: Faster random access, lower cost, less data loss risk
- **Cons**: Limited storage for media/logs
- **Best for**: Basic IoT, sensors, control systems

**64-128GB Cards**:
- **Pros**: Good balance of performance and storage
- **Cons**: Higher cost, longer backup times
- **Best for**: Data logging, development, moderate media storage

**256GB+ Cards**:
- **Pros**: Massive storage for media/logs
- **Cons**: Slower random access, higher failure impact, expensive
- **Best for**: Security cameras, extensive data logging, media servers

#### Counterfeit Card Detection

**Common signs of counterfeit cards**:
- **Unusually low prices** from unknown sellers
- **Performance doesn't match specifications**
- **Inconsistent branding or labeling errors**

**Testing for counterfeits**:
```bash
# Test actual capacity (this will take a long time for large cards)
# Use with caution - this will fill the entire card
dd if=/dev/urandom of=/f/test-file bs=1M count=30000 status=progress
```
**Warning**: This test writes 30GB of random data. Adjust `count` for your card size.

**Quick verification tools** (Windows):
- **H2testw**: Free tool to verify actual card capacity
- **FakeFlashTest**: Another verification utility
- **Command**: Download from official sources only

### Command and File System Issues

#### Incorrect Ping Command
**Issue**: `ping pi@192.168.1.176` fails

**Explanation**: The `pi@` format is only for SSH connections, not ping
**Correct Command**: `ping 192.168.1.176` (IP address only)

#### Boot Partition Drive Letter Issues
**Issue**: `touch /d/ssh` fails with "No such file or directory"

**Root Cause**: Windows assigns different drive letters depending on existing drives
**Solution Process**:
1. Run diagnostic command:
   ```bash
   wmic logicaldisk get size,freespace,caption
   ```
2. Look for a ~250MB drive that appeared after flashing
3. Use the correct drive letter (E:, G:, etc.) instead of assuming D:

#### Touch Command Not Working
**Issue**: `touch` command fails in some environments

**Alternative Solutions**:
```bash
# Method 1: Using echo
echo. > E:\ssh

# Method 2: Using PowerShell
powershell -Command "New-Item -Path 'E:\ssh' -ItemType File"
```

## Network Configuration Examples

### Example Network Setup (Your Current Setup)
```
Router IP: 192.168.1.1
Your PC IP: 192.168.1.100
Pi IP: 192.168.1.176 (auto-assigned by DHCP)
```

### Common Router Default IPs
- Google Nest WiFi: `192.168.86.1`
- Most routers: `192.168.1.1`
- Some routers: `192.168.0.1`
- Linksys: `192.168.1.1`
- Netgear: `192.168.1.1`

## Files Created

After following this guide, you should have:

```
drive-images/raspberry-pi/2025-08-09/
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