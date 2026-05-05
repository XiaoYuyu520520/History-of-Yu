import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """Configuration manager for storing default options."""
    
    DEFAULT_CONFIG = {
        "scan": {
            "concurrency": 500,
            "timeout": 1.0,
            "ports": "common",
            "enrich": True
        },
        "output": {
            "format": "console",
            "json_file": "results.json",
            "csv_file": "results.csv"
        },
        "network": {
            "default_subnet": "local"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            home = os.path.expanduser("~")
            self.config_dir = Path(home) / ".wlan_scan"
            self.config_path = self.config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
        
        self.config: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()
    
    def reset(self) -> None:
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    @property
    def concurrency(self) -> int:
        return self.get("scan.concurrency", 500)
    
    @concurrency.setter
    def concurrency(self, value: int):
        self.set("scan.concurrency", value)
    
    @property
    def timeout(self) -> float:
        return self.get("scan.timeout", 1.0)
    
    @timeout.setter
    def timeout(self, value: float):
        self.set("scan.timeout", value)
    
    @property
    def ports(self) -> str:
        return self.get("scan.ports", "common")
    
    @ports.setter
    def ports(self, value: str):
        self.set("scan.ports", value)
    
    @property
    def enrich(self) -> bool:
        return self.get("scan.enrich", True)
    
    @enrich.setter
    def enrich(self, value: bool):
        self.set("scan.enrich", value)
    
    @property
    def output_format(self) -> str:
        return self.get("output.format", "console")
    
    @output_format.setter
    def output_format(self, value: str):
        self.set("output.format", value)
    
    @property
    def json_file(self) -> str:
        return self.get("output.json_file", "results.json")
    
    @json_file.setter
    def json_file(self, value: str):
        self.set("output.json_file", value)
    
    @property
    def csv_file(self) -> str:
        return self.get("output.csv_file", "results.csv")
    
    @csv_file.setter
    def csv_file(self, value: str):
        self.set("output.csv_file", value)
    
    @property
    def default_subnet(self) -> str:
        return self.get("network.default_subnet", "local")
    
    @default_subnet.setter
    def default_subnet(self, value: str):
        self.set("network.default_subnet", value)


config = Config()
