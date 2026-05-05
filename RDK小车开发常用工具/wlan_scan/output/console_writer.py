"""Console output writer for displaying scan results."""

from typing import List
import sys

from models import Device
from core.logger import get_logger

logger = get_logger(__name__)

try:
    from colorama import Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class ConsoleWriter:
    """Writes scan results to console with formatting."""
    
    def __init__(self, use_colors: bool = True):
        """Initialize console writer.
        
        Args:
            use_colors: Whether to use colored output
        """
        self.use_colors = use_colors and COLORAMA_AVAILABLE
    
    def write_devices(self, devices: List[Device]) -> None:
        """Write devices to console.
        
        Args:
            devices: List of Device objects
        """
        if not devices:
            print("No devices found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(devices)} device(s)")
        print(f"{'='*80}\n")
        
        for i, device in enumerate(devices, 1):
            self._write_device(device, i)
            print()
    
    def _write_device(self, device: Device, index: int = None) -> None:
        """Write a single device to console."""
        if index is not None:
            prefix = f"[{index}] "
        else:
            prefix = ""
        
        ip_color = Fore.CYAN if self.use_colors else ""
        mac_color = Fore.YELLOW if self.use_colors else ""
        hostname_color = Fore.GREEN if self.use_colors else ""
        vendor_color = Fore.MAGENTA if self.use_colors else ""
        port_color = Fore.RED if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""
        
        print(f"{prefix}{ip_color}IP Address:{reset} {device.ip}")
        
        if device.mac:
            print(f"       {mac_color}MAC Address:{reset} {device.mac}")
        
        if device.hostname:
            print(f"       {hostname_color}Hostname:{reset} {device.hostname}")
        
        if device.vendor:
            print(f"       {vendor_color}Vendor:{reset} {device.vendor}")
        
        if device.response_time is not None:
            print(f"       Response Time: {device.response_time:.2f}ms")
        
        if device.open_ports:
            ports_str = self._format_ports(device.open_ports)
            print(f"       {port_color}Open Ports:{reset} {ports_str}")
    
    def _format_ports(self, ports: List[int], max_display: int = 20) -> str:
        """Format ports for display."""
        if not ports:
            return "None"
        
        if len(ports) <= max_display:
            return ', '.join(map(str, ports))
        
        displayed = ports[:max_display]
        remaining = len(ports) - max_display
        return ', '.join(map(str, displayed)) + f", ... (+{remaining} more)"
    
    def write_summary(self, devices: List[Device], subnet: str) -> None:
        """Write scan summary."""
        print(f"\n{'='*80}")
        print(f"Scan Summary for {subnet}")
        print(f"{'='*80}")
        print(f"Total devices found: {len(devices)}")
        
        vendors = {}
        for device in devices:
            if device.vendor:
                vendors[device.vendor] = vendors.get(device.vendor, 0) + 1
        
        if vendors:
            print("\nVendors:")
            for vendor, count in sorted(vendors.items(), key=lambda x: -x[1]):
                print(f"  - {vendor}: {count}")
        
        all_ports = {}
        for device in devices:
            for port in device.open_ports:
                all_ports[port] = all_ports.get(port, 0) + 1
        
        if all_ports:
            print("\nMost common open ports:")
            for port, count in sorted(all_ports.items(), key=lambda x: -x[1])[:10]:
                print(f"  - {port}: {count} hosts")
        
        print(f"{'='*80}\n")
    
    def write_gateway(self, gateway) -> None:
        """Write gateway information."""
        if not gateway:
            print("No gateway found.")
            return
        
        print(f"\n{'='*80}")
        print("Gateway Information")
        print(f"{'='*80}")
        print(f"IP Address: {gateway.ip_address}")
        print(f"Interface: {gateway.interface}")
        print(f"Can reach internet: {gateway.can_reach_internet}")
        if gateway.latency_ms:
            print(f"Latency: {gateway.latency_ms:.2f}ms")
        print(f"{'='*80}\n")
