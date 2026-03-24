#!/bin/bash
# ============================================================
# WiFi Hotspot Setup Script for Raspberry Pi
# Creates a WiFi hotspot for direct phone connection
# ============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
SSID="AttendancePi"
PASSWORD="attendance123"
HOTSPOT_IP="192.168.4.1"

echo -e "${BLUE}"
echo "============================================================"
echo "  📶 WiFi Hotspot Setup for Attendance System"
echo "============================================================"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo ./setup_hotspot.sh${NC}"
    exit 1
fi

# Ask for custom SSID and password
echo -e "${YELLOW}Enter WiFi hotspot settings (or press Enter for defaults):${NC}"
echo ""
read -p "WiFi Name (default: $SSID): " custom_ssid
read -p "Password (default: $PASSWORD): " custom_password

if [ -n "$custom_ssid" ]; then
    SSID="$custom_ssid"
fi

if [ -n "$custom_password" ]; then
    PASSWORD="$custom_password"
fi

echo ""
echo -e "${BLUE}Setting up hotspot with:${NC}"
echo "  SSID: $SSID"
echo "  Password: $PASSWORD"
echo ""

# Check if NetworkManager is available
if command -v nmcli &> /dev/null; then
    echo -e "${GREEN}Using NetworkManager method (recommended)...${NC}"
    
    # Stop any existing hotspot
    nmcli connection delete Hotspot 2>/dev/null
    
    # Create hotspot
    nmcli device wifi hotspot ssid "$SSID" password "$PASSWORD"
    
    # Make it permanent
    nmcli connection modify Hotspot connection.autoconnect yes
    
    echo ""
    echo -e "${GREEN}✅ Hotspot created successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Connect to:${NC}"
    echo "  WiFi: $SSID"
    echo "  Password: $PASSWORD"
    echo "  Web UI: http://$HOTSPOT_IP:5000"
    
else
    echo -e "${YELLOW}NetworkManager not found. Using hostapd method...${NC}"
    
    # Install required packages
    echo "Installing hostapd and dnsmasq..."
    apt update
    apt install -y hostapd dnsmasq
    
    # Stop services
    systemctl stop hostapd
    systemctl stop dnsmasq
    
    # Backup and configure dhcpcd
    if [ ! -f /etc/dhcpcd.conf.backup ]; then
        cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
    fi
    
    # Check if already configured
    if ! grep -q "interface wlan0" /etc/dhcpcd.conf; then
        echo "" >> /etc/dhcpcd.conf
        echo "# WiFi Hotspot Configuration" >> /etc/dhcpcd.conf
        echo "interface wlan0" >> /etc/dhcpcd.conf
        echo "    static ip_address=$HOTSPOT_IP/24" >> /etc/dhcpcd.conf
        echo "    nohook wpa_supplicant" >> /etc/dhcpcd.conf
    fi
    
    # Configure dnsmasq
    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null
    cat > /etc/dnsmasq.conf << EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.50,255.255.255.0,24h
address=/attendance.local/$HOTSPOT_IP
EOF
    
    # Configure hostapd
    cat > /etc/hostapd/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=$SSID
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    
    # Point hostapd to config
    sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
    
    # Enable IP forwarding (optional, for internet sharing)
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    
    # Unmask and enable services
    systemctl unmask hostapd
    systemctl enable hostapd
    systemctl enable dnsmasq
    
    echo ""
    echo -e "${GREEN}✅ Hotspot configured successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Please reboot your Raspberry Pi:${NC}"
    echo "  sudo reboot"
    echo ""
    echo -e "${YELLOW}After reboot, connect to:${NC}"
    echo "  WiFi: $SSID"
    echo "  Password: $PASSWORD"
    echo "  Web UI: http://$HOTSPOT_IP:5000"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Setup complete!${NC}"
echo -e "${BLUE}============================================================${NC}"
