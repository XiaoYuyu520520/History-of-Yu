import os
import yaml
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG = {
    "ros2": {
        "distro": "jazzy",
        "base_path": "/opt/ros",
        "ros2_bin": "/opt/ros/jazzy/bin/ros2"
    },
    "scan": {
        "timeout": 5,
        "msg_parse_timeout": 5,
        "refresh_interval": 2,
        "max_display": 20,
        "strict_mode": False
    },
    "ui": {
        "theme": "default"
    },
    "output": {
        "default_format": "both",
        "save_dir": "~/ros2_scans"
    }
}


class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        home = Path.home()
        config_dir = home / ".ros2_helper"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                return self._merge_config(DEFAULT_CONFIG, user_config)
        return DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        result = default.copy()
        if user:
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_config(result[key], value)
                else:
                    result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_ros2_bin(self) -> str:
        ros2_config = self.config.get('ros2', {})
        base_path = ros2_config.get('base_path', '/opt/ros')
        distro = ros2_config.get('distro', 'jazzy')
        custom_bin = ros2_config.get('ros2_bin')
        
        if custom_bin:
            return custom_bin
        return f"{base_path}/{distro}/bin/ros2"
    
    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    @property
    def config_dict(self) -> Dict[str, Any]:
        return self.config


def create_default_config():
    home = Path.home()
    config_path = home / ".ros2_helper" / "config.yaml"
    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        print(f"Default config created at: {config_path}")
    return str(config_path)
