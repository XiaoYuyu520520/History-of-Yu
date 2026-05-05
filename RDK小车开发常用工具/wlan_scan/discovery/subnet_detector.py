"""Subnet detector for discovering local network subnets."""

import subprocess
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from core.network_utils import NetworkUtils
from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SubnetInfo:
    """Information about a network subnet."""
    network: str
    netmask: str
    cidr: str
    broadcast: str
    interface: str
    gateway: Optional[str] = None


class SubnetDetector:
    """Detects all network subnets on the local machine."""
    
    def __init__(self):
        self.network_utils = NetworkUtils()
    
    def detect_all_subnets(self) -> List[SubnetInfo]:
        """Detect all network subnets on the local machine.
        
        Returns:
            List of SubnetInfo objects
        """
        subnets = []
        
        interfaces = self.network_utils.get_all_interfaces()
        
        for iface in interfaces:
            if not iface.ip_address:
                continue
            
            if not iface.netmask:
                iface.netmask = '255.255.255.0'
            
            network = self.network_utils.calculate_network(
                iface.ip_address, 
                iface.netmask
            )
            broadcast = self.network_utils.calculate_broadcast(
                iface.ip_address, 
                iface.netmask
            )
            
            cidr = self._netmask_to_cidr(iface.netmask)
            
            gateway = self._find_gateway_for_interface(iface.name)
            
            subnet = SubnetInfo(
                network=network,
                netmask=iface.netmask,
                cidr=f"{network}/{cidr}",
                broadcast=broadcast,
                interface=iface.name,
                gateway=gateway
            )
            subnets.append(subnet)
        
        return subnets
    
    def _netmask_to_cidr(self, netmask: str) -> int:
        """Convert netmask to CIDR notation."""
        try:
            parts = netmask.split('.')
            cidr = 0
            for part in parts:
                cidr += bin(int(part)).count('1')
            return cidr
        except:
            return 24
    
    def _find_gateway_for_interface(self, interface_name: str) -> Optional[str]:
        """Find default gateway for a specific interface."""
        try:
            if self.network_utils.is_windows:
                result = subprocess.run(
                    ['route', 'print', '0.0.0.0'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line and interface_name.lower() in line.lower():
                        parts = line.split()
                        if parts:
                            return parts[2]
            else:
                result = subprocess.run(
                    ['ip', 'route', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'default' in line:
                        parts = line.split()
                        if len(parts) >= 3 and parts[0] == 'default':
                            return parts[2]
        except Exception as e:
            logger.debug(f"Failed to find gateway for {interface_name}: {e}")
        
        return None
    
    def get_subnet_cidr(self, subnet: SubnetInfo) -> str:
        """Get CIDR notation for a subnet.
        
        Args:
            subnet: SubnetInfo object
            
        Returns:
            CIDR notation string
        """
        return subnet.cidr
    
    def expand_subnet(self, cidr: str) -> List[str]:
        """Expand a CIDR subnet to list of IP addresses.
        
        Args:
            cidr: CIDR notation (e.g., '192.168.1.0/24')
            
        Returns:
            List of IP addresses
        """
        try:
            import ipaddress
            network = ipaddress.IPv4Network(cidr, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            logger.error(f"Invalid CIDR: {cidr} - {e}")
            return []
    
    def get_local_subnets(self) -> List[str]:
        """Get list of local subnet CIDRs.
        
        Returns:
            List of CIDR notation strings
        """
        subnets = self.detect_all_subnets()
        return [s.cidr for s in subnets]
