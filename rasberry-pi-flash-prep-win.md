# Raspberry Pi Zero 2 W Flash & SSH Setup Instructions (Windows)

**Path Placeholder Note:**
This document uses `{{Project Base Directory}}` as a placeholder for your project's base directory path.

**Example:** If your project is located at `C:\Users\gordon\source\repos\Humidifier-Automation`, then replace all instances of `{{Project Base Directory}}` with that path.

---

This guide documents the complete process for flashing Raspberry Pi OS to an SD card and enabling SSH for remote access using **Windows tools** (Git Bash, PowerShell, Command Prompt).

## Prerequisites

- SD card (16GB+ recommended)
- SD card reader
- Windows PC with internet connection
- Raspberry Pi Zero 2 W

### Recommended Shell Environment

**Git Bash (Recommended)** - Installed with Git for Windows
- All Windows commands (wmic, diskpart) work directly
- Unix-style commands and paths supported
- Best compatibility for this guide
- **Note**: `dd` may or may not be available depending on your Git Bash installation

**Alternative: PowerShell or Command Prompt**
- All Windows disk commands work natively
- Some commands may need different syntax (provided below)

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

**Step 1: Identify the physical SD card**
```bash
# Find removable drives (shows physical device)
wmic diskdrive where "MediaType='Removable Media'" get Model,Size,Status
```

**Step 2: Find the drive letter for the SD card**
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

**Pro tip for drive letter identification**:
```bash
# Before inserting SD card, run:
wmic logicaldisk get caption

# After inserting SD card, run the same command
# The new drive letter that appears is your SD card
```

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
   echo "test" > F:\test.txt
   # Verify file contents
   type F:\test.txt
   ```
   If contents don't match or file is corrupted → Card hardware is actually failing

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

## Step 1: Download Raspberry Pi OS Image

### 1.1 Create Directory Structure
```bash
mkdir -p "{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09"
```
**Command explanation:**
- `mkdir` = Create directories
- `-p` = Create parent directories as needed, don't error if directory exists
- `"path"` = Directory path in quotes to handle spaces in path names

### 1.2 Download Latest Image
Download the latest Raspberry Pi OS Lite (ARM64) image:
```bash
curl -L -o "{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09\2025-05-13-raspios-bookworm-arm64-lite.img.xz" "https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/2025-05-13-raspios-bookworm-arm64-lite.img.xz"
```
**Command explanation:**
- `curl` = Command-line tool for transferring data from servers
- `-L` = Follow HTTP redirects if the server responds with a redirect
- `-o "filename"` = Save the downloaded file with this specific filename
- `"url"` = The source URL to download from

### 1.3 Extract Image
```bash
cd "{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09"
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

**Method 1: Raspberry Pi Imager (Recommended)**
1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
2. Run Raspberry Pi Imager
3. Click "Choose OS" → "Use custom" → Select your downloaded `.img` file
4. Click "Choose Storage" → Select your SD card
5. Click "Write" and wait for completion

**Method 2: Balena Etcher (Alternative GUI)**
1. Download [Balena Etcher](https://balena.io/etcher)
2. Select your `.img` file
3. Select your SD card
4. Click "Flash!"

**Method 3: Win32 Disk Imager (Windows Native)**
1. Download [Win32 Disk Imager](https://win32diskimager.org/)
2. Select your `.img` file
3. Choose your SD card drive letter
4. Click "Write"

**Method 4: Command Line (Git Bash with dd)**
```bash
# Only works if dd is available in Git Bash
dd if="{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09\2025-05-13-raspios-bookworm-arm64-lite.img" of=/dev/sdf bs=4M status=progress
```
**Note**: Replace `/dev/sdf` with your actual SD card device in Git Bash

**Method 5: PowerShell with Win32DiskImager CLI**
```powershell
# If Win32DiskImager CLI is installed
& "C:\Program Files\Win32DiskImager\Win32DiskImager.exe" -d "F:" -f "{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09\2025-05-13-raspios-bookworm-arm64-lite.img"
```

**Recommended approach**: Use Raspberry Pi Imager (Method 1) as it's specifically designed for this task and handles all the technical details automatically.

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

**Method 1: Windows Command/Git Bash** *(Recommended)*
```bash
# Using echo (works in CMD, PowerShell, and Git Bash)
echo. > E:\ssh
```

**Method 2: PowerShell**
```powershell
New-Item -Path "E:\ssh" -ItemType File
```

**Method 3: Git Bash Unix-style**
```bash
touch /e/ssh
```

**Command explanations:**
- `echo.` = Output an empty line to create file
- `>` = Redirect output to create a file
- `New-Item` = PowerShell cmdlet to create new items (files/folders)
- `-Path` = Specify the location and name
- `-ItemType File` = Create a file (not a directory)
- `touch` = Unix/Linux command (works in Git Bash)

### 3.3 Configure WiFi (Required for Pi Zero 2 W)
**IMPORTANT**: Pi Zero 2 W needs WiFi configuration to connect to your network. Create a `wpa_supplicant.conf` file on the boot partition:

**Method 1: Windows Command Prompt** *(Recommended)*
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

**Method 3: Git Bash**
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

**Replace with your actual WiFi details:**
- `YourWiFiNetworkName` = Your WiFi network name (SSID)
- `YourWiFiPassword` = Your WiFi password

### 3.4 Verify SSH File
Check that the files were created (replace `E:` with your drive letter):
```bash
dir E:\
```
**Command explanation:**
- `dir` = List directory contents (Windows command)
- `E:\` = Drive to list contents of

You should see an `ssh` file and `wpa_supplicant.conf` file in the listing along with other boot files like `config.txt` and various `.dtb` files.

## Step 4: Create Backup Images

### 4.1 Backup Original Image
```bash
copy "2025-05-13-raspios-bookworm-arm64-lite.img" "2025-05-13-raspios-bookworm-arm64-lite-ORIGINAL.img"
```
**Command explanation:**
- `copy` = Windows command to copy files
- `"source"` = The original file to copy from
- `"destination"` = The new filename for the copy

### 4.2 Create SSH-Enabled Image Backup

**Method 1: Win32 Disk Imager (Recommended)**
1. Open Win32 Disk Imager
2. Click "Read" (not Write!)
3. Select output filename: `2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img`
4. Choose your SD card drive letter
5. Click "Read" to create backup image

**Method 2: PowerShell with Win32DiskImager CLI**
```powershell
# Read/backup from SD card to image file
& "C:\Program Files\Win32DiskImager\Win32DiskImager.exe" -d "F:" -f "2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img" -r
```

**Method 3: Git Bash with dd (if available)**
```bash
# Only if dd is available in your Git Bash environment
dd if=/dev/sdf of="2025-05-13-raspios-bookworm-arm64-lite-SSH-ENABLED.img" bs=4M count=658 status=progress
```

**Command explanations:**
- **Win32DiskImager `-r`** = Read mode (create image from disk)
- **`-d "F:"`** = Source drive letter
- **`-f "filename"`** = Output image filename

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

### 5.2 Boot the Pi
1. **Safely eject SD card** from computer (right-click → Eject)
2. **Insert the same SD card** into Raspberry Pi Zero 2 W
3. **Connect power**: Use micro USB cable to power the Pi
4. **Wait for network connection**: 2-3 minutes for first boot and WiFi connection
5. **Pi will connect automatically** using the WiFi settings you created

### 5.3 Find Router IP Address
Get your computer's network configuration:
```bash
ipconfig
```
**Command explanation:**
- `ipconfig` = Display network adapter configuration on Windows
- Look for "Default Gateway" - this is your router's IP (e.g., 192.168.1.1)

### 5.4 Use ARP Table
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

### 5.5 Try Common Pi Hostnames
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

### Windows-Specific Issues

#### SD Card Not Recognized
**Solutions**:
```bash
# Check if Windows sees the SD card
wmic logicaldisk get caption,size,freespace

# Try different USB port or card reader
# Check Device Manager for USB/Storage devices
```

#### Drive Letter Issues
**Issue**: SD card gets different drive letters after flashing

**Solution**: Always verify drive letter before creating SSH/WiFi files:
```bash
wmic logicaldisk where "size<500000000" get caption,size
```

#### Permission Denied Errors
**Solutions**:
- **Run as Administrator**: Right-click Command Prompt/PowerShell → "Run as Administrator"
- **Check antivirus**: Temporarily disable real-time protection
- **File in use**: Close any programs that might be accessing the SD card

## Files Created

After following this guide, you should have:

```
{{Project Base Directory}}\drive-images\raspberry-pi\2025-08-09\
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
*Windows Environment: Git Bash, PowerShell, Command Prompt*