"""CSV output writer for saving scan results."""

import csv
from typing import List
from datetime import datetime

from models import Device
from core.logger import get_logger

logger = get_logger(__name__)


class CsvWriter:
    """Writes scan results to CSV file."""
    
    def __init__(self, delimiter: str = ','):
        """Initialize CSV writer.
        
        Args:
            delimiter: CSV delimiter character
        """
        self.delimiter = delimiter
    
    def write_devices(self, devices: List[Device], filepath: str) -> bool:
        """Write devices to CSV file.
        
        Args:
            devices: List of Device objects
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                
                writer.writerow([
                    'IP Address',
                    'MAC Address',
                    'Hostname',
                    'Vendor',
                    'Open Ports',
                    'Is Alive',
                    'Response Time (ms)',
                    'First Seen',
                    'Last Seen'
                ])
                
                for device in devices:
                    writer.writerow([
                        device.ip,
                        device.mac or '',
                        device.hostname or '',
                        device.vendor or '',
                        ','.join(map(str, device.open_ports)),
                        device.is_alive,
                        device.response_time or '',
                        device.first_seen.isoformat() if device.first_seen else '',
                        device.last_seen.isoformat() if device.last_seen else ''
                    ])
            
            logger.info(f"Results saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")
            return False
    
    def append_to_file(self, devices: List[Device], filepath: str) -> bool:
        """Append devices to existing CSV file.
        
        Args:
            devices: List of Device objects
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            file_exists = filepath.exists() if hasattr(filepath, 'exists') else False
            
            with open(filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.delimiter)
                
                if not file_exists:
                    writer.writerow([
                        'IP Address',
                        'MAC Address',
                        'Hostname',
                        'Vendor',
                        'Open Ports',
                        'Is Alive',
                        'Response Time (ms)'
                    ])
                
                for device in devices:
                    writer.writerow([
                        device.ip,
                        device.mac or '',
                        device.hostname or '',
                        device.vendor or '',
                        ','.join(map(str, device.open_ports)),
                        device.is_alive,
                        device.response_time or ''
                    ])
            
            logger.info(f"Results appended to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to append to CSV: {e}")
            return False
