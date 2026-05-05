import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class TopicInfo:
    def __init__(self, name: str, msg_type: str):
        self.name = name
        self.msg_type = msg_type
        self.publishers: List[Dict] = []
        self.subscribers: List[Dict] = []
        self.qos_compatible = True
        self.qos_warnings: List[str] = []
        self.data_format: Optional[str] = None
        self.sample_message: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.msg_type,
            "publishers": self.publishers,
            "subscribers": self.subscribers,
            "qos_compatible": self.qos_compatible,
            "qos_warnings": self.qos_warnings,
            "data_format": self.data_format,
            "sample_message": self.sample_message
        }


class Scanner:
    def __init__(self, ros2_bin: str, timeout: int = 5):
        self.ros2_bin = ros2_bin
        self.timeout = timeout
    
    def scan_topics(self) -> List[TopicInfo]:
        topics = self._get_topic_list()
        topic_infos = []
        
        for topic_name, msg_type in topics:
            topic_info = self._get_topic_details(topic_name, msg_type)
            if topic_info:
                topic_infos.append(topic_info)
        
        return topic_infos
    
    def _get_topic_list(self) -> List[tuple]:
        try:
            result = subprocess.run(
                [self.ros2_bin, "topic", "list"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            topics = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('/'):
                        topics.append((line, ''))
            return topics
        except Exception as e:
            print(f"Error listing topics: {e}")
            return []
    
    def _get_topic_details(self, topic_name: str, msg_type: str = None) -> Optional[TopicInfo]:
        try:
            result = subprocess.run(
                [self.ros2_bin, "topic", "info", topic_name, "--verbose"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            topic_info = TopicInfo(topic_name, msg_type or self._extract_type(output))
            
            topic_info.publishers = self._extract_endpoints(output, 'Publisher')
            topic_info.subscribers = self._extract_endpoints(output, 'Subscription')
            
            self._check_qos_compatibility(topic_info)
            
            return topic_info
            
        except Exception as e:
            print(f"Error getting topic details for {topic_name}: {e}")
            return None
    
    def _extract_type(self, output: str) -> str:
        match = re.search(r'Topic type:\s*(.+)', output)
        return match.group(1).strip() if match else 'unknown'
    
    def _extract_endpoints(self, output: str, endpoint_type: str) -> List[Dict]:
        endpoints = []
        blocks = re.split(rf'{endpoint_type} count:', output)
        
        for block in blocks[1:]:
            endpoint = {'node': '', 'qos': {}}
            
            node_match = re.search(rf'Node name:\s*(.+)', block)
            if node_match:
                endpoint['node'] = node_match.group(1).strip()
            
            gid_match = re.search(r'GID:\s*(.+)', block)
            if gid_match:
                endpoint['gid'] = gid_match.group(1).strip()
            
            qos = self._extract_qos(block)
            endpoint['qos'] = qos
            
            endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_qos(self, block: str) -> Dict:
        qos = {}
        
        rel_match = re.search(r'Reliability:\s*(.+)', block)
        if rel_match:
            qos['reliability'] = rel_match.group(1).strip()
        
        dur_match = re.search(r'Durability:\s*(.+)', block)
        if dur_match:
            qos['durability'] = dur_match.group(1).strip()
        
        hist_match = re.search(r'History \(Depth\):\s*(.+)', block)
        if hist_match:
            qos['history'] = hist_match.group(1).strip()
        
        depth_match = re.search(r'Depth:\s*(\d+)', block)
        if depth_match:
            qos['depth'] = int(death_match.group(1))
        
        life_match = re.search(r'Lifespan:\s*(.+)', block)
        if life_match:
            qos['lifespan'] = life_match.group(1).strip()
        
        deadline_match = re.search(r'Deadline:\s*(.+)', block)
        if deadline_match:
            qos['deadline'] = deadline_match.group(1).strip()
        
        live_match = re.search(r'Liveliness:\s*(.+)', block)
        if live_match:
            qos['liveliness'] = live_match.group(1).strip()
        
        return qos
    
    def _check_qos_compatibility(self, topic_info: TopicInfo):
        if not topic_info.publishers or not topic_info.subscribers:
            return
        
        for sub in topic_info.subscribers:
            sub_qos = sub['qos']
            for pub in topic_info.publishers:
                pub_qos = pub['qos']
                
                if pub_qos.get('reliability') == 'BEST_EFFORT' and sub_qos.get('reliability') == 'RELIABLE':
                    topic_info.qos_warnings.append(
                        f"Subscriber wants RELIABLE but Publisher is BEST_EFFORT"
                    )
                    topic_info.qos_compatible = False
                
                if pub_qos.get('durability') == 'TRANSIENT_LOCAL' and sub_qos.get('durability') == 'VOLATILE':
                    topic_info.qos_warnings.append(
                        f"Subscriber wants VOLATILE but Publisher is TRANSIENT_LOCAL"
                    )
                    topic_info.qos_compatible = False


def format_topic_summary(topics: List[TopicInfo]) -> str:
    lines = []
    for i, topic in enumerate(topics, 1):
        pub_count = len(topic.publishers)
        sub_count = len(topic.subscribers)
        
        compat = "✓" if topic.qos_compatible else "⚠"
        
        lines.append(
            f"{i:2d}. {topic.name:<40} [{topic.msg_type.split('/')[-1]:<20}] "
            f"P:{pub_count} S:{sub_count} {compat}"
        )
    
    return '\n'.join(lines)
