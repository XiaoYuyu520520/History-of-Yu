"""JSON output writer for saving scan results."""

import json
import os
from typing import List
from datetime import datetime

from models import Device, ScanResult
from core.logger import get_logger

logger = get_logger(__name__)


class JsonWriter:
    """Writes scan results to JSON file."""
    
    def __init__(self, indent: int = 2):
        """Initialize JSON writer.
        
        Args:
            indent: JSON indentation spaces
        """
        self.indent = indent
    
    def write_devices(self, devices: List[Device], filepath: str) -> bool:
        """Write devices to JSON file.
        
        Args:
            devices: List of Device objects
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            data = {
                'scan_time': datetime.now().isoformat(),
                'total_devices': len(devices),
                'devices': [device.to_dict() for device in devices]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=False)
            
            logger.info(f"Results saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON: {e}")
            return False
    
    def write_scan_result(self, scan_result: ScanResult, filepath: str) -> bool:
        """Write ScanResult to JSON file.
        
        Args:
            scan_result: ScanResult object
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scan_result.to_dict(), f, indent=self.indent, ensure_ascii=False)
            
            logger.info(f"Results saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON: {e}")
            return False
    
    def append_to_file(self, devices: List[Device], filepath: str) -> bool:
        """Append devices to existing JSON file.
        
        Args:
            devices: List of Device objects
            filepath: Output file path
            
        Returns:
            True if successful
        """
        try:
            existing_data = []
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f).get('devices', [])
            
            new_devices = [device.to_dict() for device in devices]
            all_devices = existing_data + new_devices
            
            data = {
                'scan_time': datetime.now().isoformat(),
                'total_devices': len(all_devices),
                'devices': all_devices
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=False)
            
            logger.info(f"Results appended to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to append to JSON: {e}")
            return False
