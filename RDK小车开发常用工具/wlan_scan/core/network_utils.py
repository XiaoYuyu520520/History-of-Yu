"""Cross-platform network utilities for detecting interfaces and network information."""

import platform
import socket
import struct
import ipaddress
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NetworkInterface:
    """Represents a network interface."""
    name: str
    ip_address: str
    netmask: str
    broadcast: Optional[str] = None
    mac_address: Optional[str] = None
    is_up: bool = True


class NetworkUtils:
    """Cross-platform network utilities."""
    
    def __init__(self):
        self._platform = platform.system().lower()
        self._interfaces_cache: Optional[List[NetworkInterface]] = None
    
    @property
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._platform == 'windows'
    
    @property
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self._platform == 'linux'
    
    @property
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self._platform == 'darwin'
    
    def get_all_interfaces(self) -> List[NetworkInterface]:
        """Get all network interfaces with their information.
        
        Returns:
            List of NetworkInterface objects
        """
        if self._interfaces_cache is not None:
            return self._interfaces_cache
        
        interfaces = []
        
        if PSUTIL_AVAILABLE:
            interfaces = self._get_interfaces_psutil()
        else:
            interfaces = self._get_interfaces_socket()
        
        self._interfaces_cache = interfaces
        return interfaces
    
    def _get_interfaces_psutil(self) -> List[NetworkInterface]:
        """Get interfaces using psutil (cross-platform)."""
        interfaces = []
        
        try:
            for iface_name, addrs in psutil.net_if_addrs().items():
                iface = NetworkInterface(
                    name=iface_name,
                    ip_address='',
                    netmask='',
                    is_up=iface_name in psutil.net_if_stats()
                )
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        iface.ip_address = addr.address
                        iface.netmask = addr.netmask
                        iface.broadcast = getattr(addr, 'broadcast', None)
                    elif addr.family == psutil.AF_LINK:
                        iface.mac_address = addr.address
                
                if iface.ip_address:
                    interfaces.append(iface)
        except Exception as e:
            logger.warning(f"Failed to get interfaces with psutil: {e}")
            interfaces = self._get_interfaces_socket()
        
        return interfaces
    
    def _get_interfaces_socket(self) -> List[NetworkInterface]:
        """Get interfaces using socket (fallback method)."""
        interfaces = []
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            if self.is_windows:
                interfaces = self._get_windows_interfaces()
            else:
                interfaces = self._get_linux_interfaces()
            
            if not interfaces:
                interfaces.append(NetworkInterface(
                    name='default',
                    ip_address=local_ip,
                    netmask='255.255.255.0'
                ))
        except Exception as e:
            logger.error(f"Failed to get interfaces: {e}")
        
        return interfaces
    
    def _get_windows_interfaces(self) -> List[NetworkInterface]:
        """Get Windows network interfaces using ipconfig."""
        import subprocess
        
        interfaces = []
        
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            current_iface = None
            for line in lines:
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if '适配器' in key or 'adapter' in key.lower():
                        if current_iface and current_iface.ip_address:
                            interfaces.append(current_iface)
                        current_iface = NetworkInterface(
                            name=value.split(' ')[0],
                            ip_address='',
                            netmask='',
                            is_up=True
                        )
                    elif 'IPv4' in key and current_iface:
                        current_iface.ip_address = value.split(':')[-1].strip()
                    elif '子网掩码' in key or 'Subnet Mask' in key:
                        if current_iface:
                            current_iface.netmask = value
            
            if current_iface and current_iface.ip_address:
                interfaces.append(current_iface)
        except Exception as e:
            logger.warning(f"Failed to get Windows interfaces: {e}")
        
        return interfaces
    
    def _get_linux_interfaces(self) -> List[NetworkInterface]:
        """Get Linux network interfaces from /proc/net/if_inet6 or ip command."""
        import subprocess
        
        interfaces = []
        
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show'],
                capture_output=True,
                text=True
            )
            
            current_iface = None
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        if current_iface and current_iface.ip_address:
                            interfaces.append(current_iface)
                        
                        iface_name = parts[1].strip()
                        current_iface = NetworkInterface(
                            name=iface_name,
                            ip_address='',
                            netmask='',
                            is_up='state UP' in line
                        )
                
                elif line.strip().startswith('inet '):
                    parts = line.strip().split()
                    if len(parts) >= 2 and current_iface:
                        ip = parts[1].split('/')
                        current_iface.ip_address = ip[0]
                        if len(ip) > 1:
                            cidr = int(ip[1])
                            current_iface.netmask = self._cidr_to_netmask(cidr)
            
            if current_iface and current_iface.ip_address:
                interfaces.append(current_iface)
        except Exception as e:
            logger.warning(f"Failed to get Linux interfaces: {e}")
        
        return interfaces
    
    def _cidr_to_netmask(self, cidr: int) -> str:
        """Convert CIDR notation to netmask string."""
        mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
        return socket.inet_ntoa(struct.pack('>I', mask))
    
    def get_interface_ip(self, interface_name: str) -> Optional[str]:
        """Get IP address of a specific interface.
        
        Args:
            interface_name: Name of the network interface
            
        Returns:
            IP address string or None
        """
        interfaces = self.get_all_interfaces()
        for iface in interfaces:
            if iface.name == interface_name:
                return iface.ip_address
        return None
    
    def get_interface_netmask(self, interface_name: str) -> Optional[str]:
        """Get netmask of a specific interface.
        
        Args:
            interface_name: Name of the network interface
            
        Returns:
            Netmask string or None
        """
        interfaces = self.get_all_interfaces()
        for iface in interfaces:
            if iface.name == interface_name:
                return iface.netmask
        return None
    
    def get_interface_broadcast(self, interface_name: str) -> Optional[str]:
        """Get broadcast address of a specific interface.
        
        Args:
            interface_name: Name of the network interface
            
        Returns:
            Broadcast address string or None
        """
        interfaces = self.get_all_interfaces()
        for iface in interfaces:
            if iface.name == interface_name:
                return iface.broadcast
        return None
    
    def ip_to_int(self, ip: str) -> int:
        """Convert IP address string to integer."""
        return int(ipaddress.IPv4Address(ip))
    
    def int_to_ip(self, ip_int: int) -> str:
        """Convert integer to IP address string."""
        return str(ipaddress.IPv4Address(ip_int))
    
    def calculate_network(self, ip: str, netmask: str) -> str:
        """Calculate network address from IP and netmask.
        
        Args:
            ip: IP address
            netmask: Subnet mask
            
        Returns:
            Network address
        """
        ip_int = self.ip_to_int(ip)
        mask_int = self.ip_to_int(netmask)
        network_int = ip_int & mask_int
        return self.int_to_ip(network_int)
    
    def calculate_broadcast(self, ip: str, netmask: str) -> str:
        """Calculate broadcast address from IP and netmask.
        
        Args:
            ip: IP address
            netmask: Subnet mask
            
        Returns:
            Broadcast address
        """
        ip_int = self.ip_to_int(ip)
        mask_int = self.ip_to_int(netmask)
        broadcast_int = ip_int | (~mask_int & 0xFFFFFFFF)
        return self.int_to_ip(broadcast_int)
    
    def get_subnet_hosts(self, network: str, netmask: str) -> List[str]:
        """Get list of all host IPs in a subnet.
        
        Args:
            network: Network address
            netmask: Subnet mask
            
        Returns:
            List of IP addresses
        """
        network_int = self.ip_to_int(network)
        broadcast_int = self.ip_to_int(self.calculate_broadcast(network, netmask))
        
        return [self.int_to_ip(i) for i in range(network_int + 1, broadcast_int)]
    
    def parse_cidr(self, cidr: str) -> Tuple[str, str]:
        """Parse CIDR notation to network and netmask.
        
        Args:
            cidr: CIDR notation (e.g., '192.168.1.0/24')
            
        Returns:
            Tuple of (network, netmask)
        """
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
            return (str(network.network_address), str(network.netmask))
        except ValueError as e:
            raise ValueError(f"Invalid CIDR notation: {cidr}") from e
    
    def is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IP address."""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ValueError:
            return False
    
    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is a private address."""
        try:
            return ipaddress.IPv4Address(ip).is_private
        except ValueError:
            return False
