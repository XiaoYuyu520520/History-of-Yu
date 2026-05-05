"""Scan result model for storing scan results."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from models import Device


@dataclass
class ScanResult:
    """Represents the result of a network scan."""
    subnet: str
    devices: List[Device] = field(default_factory=list)
    scan_time: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    total_hosts_scanned: int = 0
    hosts_alive: int = 0
    scan_type: str = 'full'
    
    def to_dict(self) -> dict:
        """Convert scan result to dictionary."""
        return {
            'subnet': self.subnet,
            'devices': [d.to_dict() for d in self.devices],
            'scan_time': self.scan_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'total_hosts_scanned': self.total_hosts_scanned,
            'hosts_alive': self.hosts_alive,
            'scan_type': self.scan_type
        }
    
    def get_device_by_ip(self, ip: str) -> Optional[Device]:
        """Get a device by IP address."""
        for device in self.devices:
            if device.ip == ip:
                return device
        return None
    
    def get_devices_by_vendor(self, vendor: str) -> List[Device]:
        """Get all devices from a specific vendor."""
        return [d for d in self.devices if d.vendor and vendor.lower() in d.vendor.lower()]
    
    def get_devices_with_port(self, port: int) -> List[Device]:
        """Get all devices with a specific port open."""
        return [d for d in self.devices if port in d.open_ports]
    
    def summary(self) -> str:
        """Get a summary of the scan result."""
        return (
            f"Scan of {self.subnet} completed in {self.duration_seconds:.2f}s\n"
            f"Scanned {self.total_hosts_scanned} hosts, found {self.hosts_alive} alive"
        )
