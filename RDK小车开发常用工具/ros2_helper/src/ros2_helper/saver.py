import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ScanResult:
    def __init__(self, topics: List[Any], scan_time: datetime = None):
        self.scan_time = scan_time or datetime.now()
        self.topics = topics
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_time": self.scan_time.isoformat(),
            "topic_count": len(self.topics),
            "topics": [t.to_dict() if hasattr(t, 'to_dict') else t for t in self.topics]
        }


class ResultSaver:
    def __init__(self, save_dir: str = None):
        self.save_dir = Path(save_dir or os.path.expanduser("~/ros2_scans"))
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, result: ScanResult, formats: List[str] = None) -> Dict[str, str]:
        if formats is None:
            formats = ['json', 'yaml']
        
        saved_files = {}
        timestamp = result.scan_time.strftime("%Y%m%d_%H%M%S")
        
        if 'json' in formats:
            json_path = self.save_dir / f"ros2_scan_{timestamp}.json"
            self._save_json(result, json_path)
            saved_files['json'] = str(json_path)
        
        if 'yaml' in formats:
            yaml_path = self.save_dir / f"ros2_scan_{timestamp}.yaml"
            self._save_yaml(result, yaml_path)
            saved_files['yaml'] = str(yaml_path)
        
        return saved_files
    
    def _save_json(self, result: ScanResult, path: Path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _save_yaml(self, result: ScanResult, path: Path):
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(result.to_dict(), f, default_flow_style=False, allow_unicode=True)
    
    def list_saved(self) -> List[Dict[str, str]]:
        files = []
        for f in sorted(self.save_dir.glob("ros2_scan_*.json")):
            files.append({
                'name': f.name,
                'path': str(f),
                'time': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return files


def save_scan_result(topics: List[Any], save_dir: str = None, formats: List[str] = None) -> Dict[str, str]:
    saver = ResultSaver(save_dir)
    result = ScanResult(topics)
    return saver.save(result, formats)
