"""Device model for representing network devices."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Device:
    """Represents a network device discovered on the network."""
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    is_alive: bool = True
    response_time: Optional[float] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert device to dictionary."""
        return {
            'ip': self.ip,
            'mac': self.mac,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'open_ports': self.open_ports,
            'is_alive': self.is_alive,
            'response_time_ms': self.response_time,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat()
        }
    
    def __str__(self) -> str:
        ports_str = ','.join(map(str, self.open_ports[:10]))
        if len(self.open_ports) > 10:
            ports_str += f'... (+{len(self.open_ports) - 10} more)'
        
        parts = [f"IP: {self.ip}"]
        if self.mac:
            parts.append(f"MAC: {self.mac}")
        if self.hostname:
            parts.append(f"Hostname: {self.hostname}")
        if self.vendor:
            parts.append(f"Vendor: {self.vendor}")
        if ports_str:
            parts.append(f"Ports: {ports_str}")
        
        return " | ".join(parts)
    
    def __repr__(self) -> str:
        return f"Device(ip='{self.ip}', mac='{self.mac}', hostname='{self.hostname}')"
