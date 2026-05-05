"""Port scanner for scanning ports on network devices."""

import socket
import concurrent.futures
import time
from typing import List, Set, Optional, Dict

from core.logger import get_logger
from core.network_utils import NetworkUtils

logger = get_logger(__name__)


class PortScanner:
    """Scans ports on network devices."""
    
    COMMON_PORTS = {
        20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'TELNET', 25: 'SMTP',
        53: 'DNS', 80: 'HTTP', 110: 'POP3', 119: 'NNTP', 123: 'NTP',
        135: 'RPC', 139: 'NETBIOS', 143: 'IMAP', 161: 'SNMP', 194: 'IRC',
        443: 'HTTPS', 445: 'SMB', 465: 'SMTPS', 514: 'SYSLOG', 587: 'SMTP',
        993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL', 1434: 'MSSQL-UDP',
        1521: 'ORACLE', 3306: 'MYSQL', 3389: 'RDP', 5432: 'POSTGRESQL',
        5900: 'VNC', 6379: 'REDIS', 8080: 'HTTP-PROXY', 8443: 'HTTPS-ALT',
        27017: 'MONGODB', 5000: 'FLASK', 8000: 'HTTP-ALT', 9200: 'ELASTIC'
    }
    
    def __init__(self, concurrency: int = 500, timeout: float = 0.5):
        """Initialize port scanner.
        
        Args:
            concurrency: Number of concurrent port scans
            timeout: Timeout for each port connection
        """
        self.concurrency = concurrency
        self.timeout = timeout
        self.network_utils = NetworkUtils()
        self._scanned_ports = 0
    
    def scan_ports(self, ip: str, ports: Optional[List[int]] = None,
                   show_progress: bool = True) -> List[int]:
        """Scan ports on a specific host.
        
        Args:
            ip: IP address to scan
            ports: List of ports to scan, None for common ports
            show_progress: Whether to show progress
            
        Returns:
            List of open ports
        """
        if ports is None:
            ports = list(self.COMMON_PORTS.keys())
        
        if ports == list(range(0, 65536)):
            ports = self._generate_all_ports()
        
        logger.debug(f"Scanning {len(ports)} ports on {ip}")
        
        self._scanned_ports = 0
        open_ports = []
        
        port_chunks = self._chunk_list(ports, 1000)
        
        for chunk in port_chunks:
            chunk_open = self._scan_port_chunk(ip, chunk, show_progress)
            open_ports.extend(chunk_open)
        
        logger.debug(f"Found {len(open_ports)} open ports on {ip}")
        return sorted(open_ports)
    
    def _generate_all_ports(self) -> List[int]:
        """Generate list of all ports (0-65535)."""
        return list(range(0, 65536))
    
    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """Split list into chunks."""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    def _scan_port_chunk(self, ip: str, ports: List[int], 
                         show_progress: bool) -> List[int]:
        """Scan a chunk of ports."""
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.concurrency
        ) as executor:
            futures = {
                executor.submit(self._check_port, ip, port): port
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(futures):
                port = futures[future]
                try:
                    if future.result():
                        open_ports.append(port)
                        logger.debug(f"Port {port} is open on {ip}")
                except Exception as e:
                    logger.debug(f"Error scanning port {port}: {e}")
                
                self._scanned_ports += 1
        
        return open_ports
    
    def _check_port(self, ip: str, port: int) -> bool:
        """Check if a single port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def scan_common_ports(self, ip: str) -> List[int]:
        """Scan only common ports on a host.
        
        Args:
            ip: IP address to scan
            
        Returns:
            List of open common ports
        """
        return self.scan_ports(ip, list(self.COMMON_PORTS.keys()), show_progress=False)
    
    def get_service_name(self, port: int) -> str:
        """Get the service name for a port number.
        
        Args:
            port: Port number
            
        Returns:
            Service name or 'unknown'
        """
        return self.COMMON_PORTS.get(port, 'unknown')
    
    def scan_range(self, start_ip: str, end_ip: str, 
                   ports: Optional[List[int]] = None) -> Dict[str, List[int]]:
        """Scan a range of IP addresses for open ports.
        
        Args:
            start_ip: Starting IP address
            end_ip: Ending IP address
            ports: List of ports to scan
            
        Returns:
            Dictionary mapping IP to open ports
        """
        from core.network_utils import NetworkUtils
        
        utils = NetworkUtils()
        start_int = utils.ip_to_int(start_ip)
        end_int = utils.ip_to_int(end_ip)
        
        ips = [utils.int_to_ip(i) for i in range(start_int, end_int + 1)]
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(self.concurrency, 50)
        ) as executor:
            futures = {
                executor.submit(self.scan_ports, ip, ports, False): ip
                for ip in ips
            }
            
            for future in concurrent.futures.as_completed(futures):
                ip = futures[future]
                try:
                    open_ports = future.result()
                    if open_ports:
                        results[ip] = open_ports
                except Exception as e:
                    logger.debug(f"Error scanning {ip}: {e}")
        
        return results
