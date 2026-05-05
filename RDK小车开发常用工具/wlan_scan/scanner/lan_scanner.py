"""LAN scanner for discovering devices on local networks."""

import socket
import subprocess
import concurrent.futures
import time
from typing import List, Optional, Dict, Set
from dataclasses import dataclass, field

from core.network_utils import NetworkUtils
from core.logger import get_logger
from models import Device

logger = get_logger(__name__)


class LanScanner:
    """Scans local area networks for active devices."""
    
    def __init__(self, concurrency: int = 500, timeout: float = 1.0):
        """Initialize LAN scanner.
        
        Args:
            concurrency: Number of concurrent scans
            timeout: Timeout for each host check in seconds
        """
        self.concurrency = concurrency
        self.timeout = timeout
        self.network_utils = NetworkUtils()
        self._scanned_count = 0
        self._found_count = 0
    
    def scan_network(self, cidr: str, show_progress: bool = True) -> List[Device]:
        """Scan all hosts in a network range.
        
        Args:
            cidr: Network in CIDR notation (e.g., '192.168.1.0/24')
            show_progress: Whether to show progress
            
        Returns:
            List of discovered Device objects
        """
        hosts = self._expand_cidr(cidr)
        if not hosts:
            logger.error(f"Invalid CIDR or no hosts: {cidr}")
            return []
        
        logger.info(f"Scanning {len(hosts)} hosts in {cidr}...")
        
        self._scanned_count = 0
        self._found_count = 0
        devices = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.concurrency
        ) as executor:
            futures = {
                executor.submit(self._check_host, ip): ip 
                for ip in hosts
            }
            
            for future in concurrent.futures.as_completed(futures):
                ip = futures[future]
                try:
                    result = future.result()
                    self._scanned_count += 1
                    
                    if show_progress and self._scanned_count % 50 == 0:
                        print(f"\r  Scanned: {self._scanned_count}/{len(hosts)}, Found: {self._found_count}", 
                              end='', flush=True)
                    
                    if result:
                        self._found_count += 1
                        devices.append(result)
                except Exception as e:
                    logger.debug(f"Error scanning {ip}: {e}")
        
        if show_progress:
            print(f"\r  Scanned: {self._scanned_count}/{len(hosts)}, Found: {self._found_count}")
        
        logger.info(f"Scan complete. Found {len(devices)} active hosts.")
        return devices
    
    def scan_local_network(self, show_progress: bool = True) -> List[Device]:
        """Scan all local network subnets.
        
        Args:
            show_progress: Whether to show progress
            
        Returns:
            List of discovered Device objects
        """
        from discovery import SubnetDetector
        
        detector = SubnetDetector()
        subnets = detector.detect_all_subnets()
        
        if not subnets:
            logger.warning("No local subnets found")
            return []
        
        logger.info(f"Found {len(subnets)} network interface(s)")
        
        all_devices = []
        skip_interfaces = ['lo', 'docker0', 'lo0']
        
        for subnet in subnets:
            if subnet.interface in skip_interfaces:
                logger.info(f"Skipping interface {subnet.interface}")
                continue
            
            if subnet.network.startswith('127.'):
                logger.info(f"Skipping loopback interface {subnet.interface}")
                continue
            
            logger.info(f"Scanning {subnet.cidr} on interface {subnet.interface}")
            devices = self.scan_network(subnet.cidr, show_progress)
            all_devices.extend(devices)
        
        return all_devices
    
    def _expand_cidr(self, cidr: str) -> List[str]:
        """Expand CIDR to list of IP addresses."""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(cidr, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            logger.error(f"Invalid CIDR {cidr}: {e}")
            return []
    
    def _check_host(self, ip: str) -> Optional[Device]:
        """Check if a host is alive and gather basic info.
        
        Args:
            ip: IP address to check
            
        Returns:
            Device object if host is alive, None otherwise
        """
        is_alive = False
        response_time = None
        
        start_time = time.time()
        
        if self._ping_host(ip):
            is_alive = True
            response_time = (time.time() - start_time) * 1000
        
        if not is_alive:
            if self._tcp_check_host(ip):
                is_alive = True
                response_time = (time.time() - start_time) * 1000
        
        if not is_alive:
            return None
        
        device = Device(
            ip=ip,
            is_alive=True,
            response_time=response_time
        )
        
        return device
    
    def _ping_host(self, ip: str) -> bool:
        """Ping a host to check if it's alive."""
        try:
            if self.network_utils.is_windows:
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(int(self.timeout * 1000)), ip],
                    capture_output=True,
                    timeout=self.timeout + 1
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(int(self.timeout)), ip],
                    capture_output=True,
                    timeout=self.timeout + 1
                )
            
            return result.returncode == 0
        except Exception:
            return False
    
    def _tcp_check_host(self, ip: str) -> bool:
        """Check if host is reachable via TCP on common ports."""
        common_ports = [80, 443, 22, 445, 139, 3389]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            except Exception:
                continue
        
        return False
    
    def ping_host(self, ip: str) -> bool:
        """Ping a single host.
        
        Args:
            ip: IP address
            
        Returns:
            True if host is reachable
        """
        return self._ping_host(ip) or self._tcp_check_host(ip)
