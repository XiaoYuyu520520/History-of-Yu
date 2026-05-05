"""Gateway finder for discovering internet exit points."""

import subprocess
import socket
import requests
import re
from typing import Optional, List, Dict
from dataclasses import dataclass

from core.network_utils import NetworkUtils
from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GatewayInfo:
    """Information about a network gateway."""
    ip_address: str
    interface: str
    is_default: bool
    can_reach_internet: bool
    latency_ms: Optional[float] = None


class GatewayFinder:
    """Finds network gateways and tests internet connectivity."""
    
    def __init__(self):
        self.network_utils = NetworkUtils()
        self._test_urls = [
            'http://www.google.com',
            'http://www.cloudflare.com',
            'http://www.baidu.com'
        ]
    
    def find_default_gateway(self) -> Optional[GatewayInfo]:
        """Find the default gateway on the current network.
        
        Returns:
            GatewayInfo object or None
        """
        gateway_ip = None
        interface_name = None
        
        try:
            if self.network_utils.is_windows:
                gateway_ip, interface_name = self._find_gateway_windows()
            else:
                gateway_ip, interface_name = self._find_gateway_linux()
        except Exception as e:
            logger.error(f"Failed to find default gateway: {e}")
        
        if not gateway_ip:
            return None
        
        can_reach = self.test_internet_connectivity(gateway_ip)
        latency = self._ping_gateway(gateway_ip)
        
        return GatewayInfo(
            ip_address=gateway_ip,
            interface=interface_name or 'unknown',
            is_default=True,
            can_reach_internet=can_reach,
            latency_ms=latency
        )
    
    def _find_gateway_windows(self) -> tuple:
        """Find gateway on Windows."""
        try:
            result = subprocess.run(
                ['route', 'print', '0.0.0.0'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if '0.0.0.0' in line and not line.startswith('='):
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2], parts[-1] if len(parts) > 3 else 'unknown'
        except Exception as e:
            logger.debug(f"Windows route failed: {e}")
        
        return None, None
    
    def _find_gateway_linux(self) -> tuple:
        """Find gateway on Linux."""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout.strip()
            if output:
                parts = output.split()
                if 'default' in parts:
                    idx = parts.index('default')
                    if len(parts) > idx + 2:
                        gateway = parts[idx + 2]
                        interface = parts[-1] if len(parts) > idx + 3 else 'unknown'
                        return gateway, interface
        except Exception as e:
            logger.debug(f"Linux ip route failed: {e}")
        
        return None, None
    
    def _ping_gateway(self, gateway_ip: str, timeout: int = 2) -> Optional[float]:
        """Ping gateway to measure latency."""
        try:
            if self.network_utils.is_windows:
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), gateway_ip],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1
                )
                for line in result.stdout.split('\n'):
                    if 'time=' in line.lower() or 'ms' in line:
                        match = re.search(r'time[=<](\d+)ms', line, re.IGNORECASE)
                        if match:
                            return float(match.group(1))
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), gateway_ip],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1
                )
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        match = re.search(r'time=([\d.]+)', line)
                        if match:
                            return float(match.group(1))
        except Exception as e:
            logger.debug(f"Ping to {gateway_ip} failed: {e}")
        
        return None
    
    def test_internet_connectivity(self, gateway_ip: Optional[str] = None) -> bool:
        """Test if we can reach the internet.
        
        Args:
            gateway_ip: Optional gateway IP to test through
            
        Returns:
            True if internet is reachable
        """
        for url in self._test_urls:
            try:
                response = requests.get(
                    url, 
                    timeout=3, 
                    allow_redirects=False,
                    proxies={'http': None, 'https': None}
                )
                if response.status_code < 500:
                    return True
            except Exception:
                continue
        
        return False
    
    def find_internet_exit(self) -> Optional[GatewayInfo]:
        """Find the best internet exit point (gateway with internet access).
        
        Returns:
            GatewayInfo with internet access or None
        """
        gateway = self.find_default_gateway()
        
        if not gateway:
            logger.warning("No default gateway found")
            return None
        
        if gateway.can_reach_internet:
            logger.info(f"Found internet gateway: {gateway.ip_address}")
            return gateway
        
        logger.warning(f"Gateway {gateway.ip_address} cannot reach internet")
        return gateway
    
    def find_all_gateways(self) -> List[GatewayInfo]:
        """Find all potential gateways on all interfaces.
        
        Returns:
            List of GatewayInfo objects
        """
        gateways = []
        interfaces = self.network_utils.get_all_interfaces()
        
        for iface in interfaces:
            if not iface.ip_address:
                continue
            
            gateway = self._probe_gateway_for_subnet(
                iface.ip_address, 
                iface.netmask
            )
            if gateway:
                gateways.append(gateway)
        
        default = self.find_default_gateway()
        if default and default not in gateways:
            gateways.insert(0, default)
        
        return gateways
    
    def _probe_gateway_for_subnet(self, ip: str, netmask: str) -> Optional[GatewayInfo]:
        """Probe for gateway in a specific subnet."""
        network = self.network_utils.calculate_network(ip, netmask)
        
        gateway_candidates = [
            network.rsplit('.', 1)[0] + '.1',
            network.rsplit('.', 1)[0] + '.254',
            ip.rsplit('.', 1)[0] + '.1',
        ]
        
        for gateway_ip in gateway_candidates:
            if gateway_ip == ip:
                continue
            
            can_reach = self._check_gateway_reachable(gateway_ip)
            if can_reach:
                latency = self._ping_gateway(gateway_ip)
                return GatewayInfo(
                    ip_address=gateway_ip,
                    interface='unknown',
                    is_default=False,
                    can_reach_internet=self.test_internet_connectivity(gateway_ip),
                    latency_ms=latency
                )
        
        return None
    
    def _check_gateway_reachable(self, ip: str, timeout: int = 1) -> bool:
        """Check if an IP is reachable."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 80))
            sock.close()
            return result == 0
        except Exception:
            return False
