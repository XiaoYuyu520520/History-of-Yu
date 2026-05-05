"""Device information module for retrieving device details."""

import socket
import subprocess
import re
from typing import Optional, Dict
import platform

from core.logger import get_logger
from core.network_utils import NetworkUtils

logger = get_logger(__name__)


class DeviceInfo:
    """Retrieves detailed information about network devices."""
    
    OUI_VENDORS = {
        '000000': 'Xerox',
        '000C29': 'VMware',
        '001A2B': 'Cisco',
        '001C42': 'Parallels',
        '002248': 'Microsoft',
        '0025AE': 'Microsoft',
        '005056': 'VMware',
        '080027': 'VirtualBox',
        '0C8D98': 'Apple',
        '14109F': 'Apple',
        '18AF8F': 'Apple',
        '1C1B68': 'Dell',
        '20689D': 'Liteon',
        '247B84': 'Dell',
        '2C33BE': 'Hon Hai',
        '34CDBE': 'Dell',
        '3C5AB4': 'Google',
        '485073': 'Google',
        '4CEDFB': 'Google',
        '54271E': 'Apple',
        '60A4B7': 'Google',
        '64F2FB': 'Apple',
        '7C0507': 'TP-Link',
        '7C1DD9': 'Apple',
        '8425DB': 'Google',
        '846878': 'TP-Link',
        '8C8590': 'Apple',
        '982D3C': 'Apple',
        'A0999F': 'Apple',
        'A4F1E8': 'Dell',
        'A86ABF': 'Google',
        'AC3C0B': 'Apple',
        'B4F1DA': 'Apple',
        'BC52B5': 'Apple',
        'C0C522': 'Hon Hai',
        'C86000': 'Intel',
        'D023DB': 'Apple',
        'D09B05': 'Dell',
        'D0C5D3': 'Apple',
        'DC53A6': 'Apple',
        'E006E5': 'Apple',
        'E4E749': 'Apple',
        'E8B1FC': 'Apple',
        'F02F74': 'Apple',
        'F0DCE2': 'Apple',
        'F4F5D8': 'Google',
    }
    
    def __init__(self):
        self.network_utils = NetworkUtils()
    
    def get_mac_address(self, ip: str) -> Optional[str]:
        """Get MAC address of a device using ARP.
        
        Args:
            ip: IP address of the device
            
        Returns:
            MAC address string or None
        """
        try:
            if self.network_utils.is_windows:
                result = subprocess.run(
                    ['arp', '-a', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                for line in result.stdout.split('\n'):
                    if ip in line:
                        match = re.search(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', line)
                        if match:
                            return match.group(0).replace('-', ':').upper()
            else:
                result = subprocess.run(
                    ['arp', '-n', ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            mac = parts[2]
                            if ':' in mac or '-' in mac:
                                return mac.replace('-', ':').upper()
            
            return None
        except Exception as e:
            logger.debug(f"Failed to get MAC for {ip}: {e}")
            return None
    
    def get_hostname(self, ip: str, timeout: float = 2.0) -> Optional[str]:
        """Get hostname of a device using reverse DNS.
        
        Args:
            ip: IP address of the device
            timeout: Timeout for DNS lookup
            
        Returns:
            Hostname string or None
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror, socket.timeout):
            pass
        
        if not self.network_utils.is_windows:
            try:
                result = subprocess.run(
                    ['nslookup', ip],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1
                )
                
                for line in result.stdout.split('\n'):
                    if 'name =' in line or 'Name:' in line:
                        match = re.search(r'(?:name\s*=\s*|Name:\s*)([^\s.]+)', line)
                        if match:
                            return match.group(1)
            except Exception:
                pass
        
        return None
    
    def get_vendor(self, mac: str) -> Optional[str]:
        """Get vendor name from MAC address OUI.
        
        Args:
            mac: MAC address string
            
        Returns:
            Vendor name or None
        """
        if not mac:
            return None
        
        mac_clean = mac.replace(':', '').replace('-', '').upper()
        
        if len(mac_clean) < 6:
            return None
        
        oui = mac_clean[:6]
        
        return self.OUI_VENDORS.get(oui, 'Unknown')
    
    def get_device_info(self, ip: str) -> Dict[str, any]:
        """Get all available device information.
        
        Args:
            ip: IP address of the device
            
        Returns:
            Dictionary with device information
        """
        info = {
            'ip': ip,
            'mac': None,
            'hostname': None,
            'vendor': None
        }
        
        mac = self.get_mac_address(ip)
        if mac:
            info['mac'] = mac
            info['vendor'] = self.get_vendor(mac)
        
        hostname = self.get_hostname(ip)
        if hostname:
            info['hostname'] = hostname
        
        return info
    
    def enrich_device(self, device) -> None:
        """Enrich a Device object with additional information.
        
        Args:
            device: Device object to enrich
        """
        if not device.mac:
            device.mac = self.get_mac_address(device.ip)
        
        if device.mac and not device.vendor:
            device.vendor = self.get_vendor(device.mac)
        
        if not device.hostname:
            device.hostname = self.get_hostname(device.ip)
    
    def update_oui_database(self, url: str = 'https://standards-oui.ieee.org/oui.txt') -> None:
        """Update OUI vendor database from IEEE.
        
        Args:
            url: URL to download OUI database
        """
        try:
            import requests
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            for line in response.text.split('\n'):
                if '(hex)' in line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        oui = parts[0].replace('-', '').upper()
                        vendor = parts[2].strip()
                        self.OUI_VENDORS[oui] = vendor
            
            logger.info(f"Updated OUI database with {len(self.OUI_VENDORS)} entries")
        except Exception as e:
            logger.warning(f"Failed to update OUI database: {e}")
