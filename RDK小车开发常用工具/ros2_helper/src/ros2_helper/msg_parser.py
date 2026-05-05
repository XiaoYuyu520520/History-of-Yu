import subprocess
import json
import yaml
import re
from typing import Dict, Any, Optional, List
from datetime import datetime


DATA_FORMAT_PATTERNS = {
    'image/compressed': [
        'sensor_msgs/msg/CompressedImage',
        'sensor_msgs/msg/Image',
        'sensor_msgs/msg/CameraInfo'
    ],
    'imu': [
        'sensor_msgs/msg/Imu',
        'sensor_msgs/msg/MagneticField'
    ],
    'radar/lidar': [
        'sensor_msgs/msg/LaserScan',
        'sensor_msgs/msg/PointCloud2',
        'sensor_msgs/msg/PointCloud',
        'sensor_msgs/msg/Range'
    ],
    'odometry': [
        'nav_msgs/msg/Odometry',
        'nav_msgs/msg/MapMetaData',
        'nav_msgs/msg/OccupancyGrid'
    ],
    'twist': [
        'geometry_msgs/msg/Twist',
        'geometry_msgs/msg/TwistStamped',
        'geometry_msgs/msg/Vector3'
    ],
    'pose': [
        'geometry_msgs/msg/Pose',
        'geometry_msgs/msg/PoseStamped',
        'geometry_msgs/msg/PoseWithCovariance'
    ],
    'joint': [
        'sensor_msgs/msg/JointState',
        'control_msgs/msg/JointTrajectory'
    ],
    'battery': [
        'sensor_msgs/msg/BatteryState',
        'diagnostic_msgs/msg/DiagnosticStatus'
    ],
    'laser': [
        'sensor_msgs/msg/LaserScan'
    ],
    'scan': [
        'sensor_msgs/msg/PointCloud2'
    ]
}


class MsgParser:
    def __init__(self, ros2_bin: str, timeout: int = 5):
        self.ros2_bin = ros2_bin
        self.timeout = timeout
    
    def infer_data_format(self, msg_type: str) -> str:
        msg_type = msg_type.strip()
        
        for format_type, types in DATA_FORMAT_PATTERNS.items():
            if any(t in msg_type for t in types):
                return format_type
        
        return 'unknown'
    
    def get_sample_message(self, topic_name: str, msg_type: str) -> Optional[Dict]:
        try:
            result = subprocess.run(
                [self.ros2_bin, "topic", "echo", topic_name, "--msg-type", msg_type, "--once"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return self._parse_message(result.stdout.strip(), msg_type)
            
        except subprocess.TimeoutExpired:
            return {"error": "timeout", "message": "获取消息超时"}
        except Exception as e:
            return {"error": "parse_error", "message": str(e)}
        
        return None
    
    def _parse_message(self, raw: str, msg_type: str) -> Dict:
        try:
            if raw.startswith('{'):
                data = json.loads(raw)
                return self._analyze_content(data, msg_type)
            else:
                return self._parse_yaml_like(raw, msg_type)
        except Exception as e:
            return {"raw": raw[:500], "parse_error": str(e)}
    
    def _parse_yaml_like(self, raw: str, msg_type: str) -> Dict:
        lines = raw.split('\n')
        data = {}
        current_key = None
        current_list = None
        
        for line in lines:
            if ':' in line:
                key = line.split(':')[0].strip()
                value = line.split(':', 1)[1].strip()
                
                if value:
                    try:
                        if value.isdigit():
                            data[key] = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            data[key] = float(value)
                        else:
                            data[key] = value
                    except:
                        data[key] = value
                else:
                    current_key = key
                    current_list = []
                    data[key] = current_list
            elif current_list is not None and line.strip():
                current_list.append(line.strip())
        
        return self._analyze_content(data, msg_type)
    
    def _analyze_content(self, data: Dict, msg_type: str) -> Dict:
        result = {
            "msg_type": msg_type,
            "data_format": self.infer_data_format(msg_type),
            "sample": {}
        }
        
        if "error" in data:
            result["error"] = data["error"]
            return result
        
        important_fields = self._extract_important_fields(data, msg_type)
        result["sample"] = important_fields
        result["fields"] = list(data.keys()) if isinstance(data, dict) else []
        
        if result["data_format"] == "unknown":
            result["data_format"] = self._detect_json_yaml(data)
        
        return result
    
    def _extract_important_fields(self, data: Dict, msg_type: str) -> Dict:
        important = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['data', 'header', 'pose', 'orientation', 'position', 'velocity', 
                          'angular', 'linear', 'ranges', 'intensities', 'image']:
                    if isinstance(value, dict):
                        important[key] = {k: v for k, v in list(value.items())[:5]}
                    else:
                        important[key] = value
                elif isinstance(value, list) and len(value) > 0:
                    if all(isinstance(x, (int, float)) for x in value[:10]):
                        important[key] = f"[{len(value)} items]"
        
        return important
    
    def _detect_json_yaml(self, data: Dict) -> str:
        if not data:
            return "unknown"
        
        sample = json.dumps(data)[:100]
        
        try:
            json.loads(json.dumps(data))
            return "json"
        except:
            pass
        
        return "binary/struct"
    
    def format_msg_info(self, topic_info) -> str:
        lines = []
        
        lines.append(f"话题名称: {topic_info.name}")
        lines.append(f"消息类型: {topic_info.msg_type}")
        lines.append(f"数据格式: {topic_info.data_format or 'unknown'}")
        
        if topic_info.sample_message:
            msg = topic_info.sample_message
            if 'error' in msg:
                lines.append(f"\n消息解析: {msg.get('error')} - {msg.get('message', '')}")
            else:
                lines.append("\n示例消息:")
                sample = msg.get('sample', {})
                for key, value in sample.items():
                    if isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for k, v in value.items():
                            lines.append(f"    {k}: {v}")
                    else:
                        lines.append(f"  {key}: {value}")
        
        return '\n'.join(lines)


def create_msg_parser(ros2_bin: str, timeout: int = 5) -> MsgParser:
    return MsgParser(ros2_bin, timeout)
