from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class QoSProfile:
    reliability: str = "RELIABLE"
    durability: str = "VOLATILE"
    history: str = "KEEP_LAST"
    depth: int = 10
    lifespan: str = "Infinite"
    deadline: str = "Infinite"
    liveliness: str = "AUTOMATIC"
    liveliness_lease: str = "Infinite"


class QoSParser:
    RELIABILITY_MAP = {
        "RELIABLE": "可靠传输",
        "BEST_EFFORT": "尽力而为"
    }
    
    DURABILITY_MAP = {
        "VOLATILE": "易失",
        "TRANSIENT_LOCAL": "瞬时本地",
        "TRANSIENT": "瞬时",
        "PERSISTENT": "持久"
    }
    
    HISTORY_MAP = {
        "KEEP_LAST": "保留最近",
        "KEEP_ALL": "保留全部"
    }
    
    LIVELINESS_MAP = {
        "AUTOMATIC": "自动",
        "MANUAL_BY_NODE": "手动按节点",
        "MANUAL_BY_TOPIC": "手动按话题"
    }
    
    @staticmethod
    def parse_qos(qos_dict: Dict) -> QoSProfile:
        return QoSProfile(
            reliability=qos_dict.get('reliability', 'RELIABLE'),
            durability=qos_dict.get('durability', 'VOLATILE'),
            history=qos_dict.get('history', 'KEEP_LAST'),
            depth=qos_dict.get('depth', 10),
            lifespan=qos_dict.get('lifespan', 'Infinite'),
            deadline=qos_dict.get('deadline', 'Infinite'),
            liveliness=qos_dict.get('liveliness', 'AUTOMATIC'),
            liveliness_lease=qos_dict.get('liveliness_lease', 'Infinite')
        )
    
    @staticmethod
    def format_qos(qos: QoSProfile) -> str:
        lines = [
            f"  可靠性 (Reliability): {qos.reliability} ({QoSParser.RELIABILITY_MAP.get(qos.reliability, '')})",
            f"  持久性 (Durability): {qos.durability} ({QoSParser.DURABILITY_MAP.get(qos.durability, '')})",
            f"  历史记录 (History): {qos.history} ({QoSParser.HISTORY_MAP.get(qos.history, '')})",
            f"  队列深度 (Depth): {qos.depth}",
            f"  生命周期 (Lifespan): {qos.lifespan}",
            f"  截止时间 (Deadline): {qos.deadline}",
            f"  活性 (Liveliness): {qos.liveliness} ({QoSParser.LIVELINESS_MAP.get(qos.liveliness, '')})",
            f"  活性租约: {qos.liveliness_lease}"
        ]
        return '\n'.join(lines)
    
    @staticmethod
    def compare_qos(pub_qos: Dict, sub_qos: Dict) -> List[str]:
        warnings = []
        
        if pub_qos.get('reliability') == 'BEST_EFFORT' and sub_qos.get('reliability') == 'RELIABLE':
            warnings.append("⚠ 发布者(BEST_EFFORT) 与 订阅者(RELIABLE) 可靠性不兼容")
        
        if pub_qos.get('durability') == 'TRANSIENT_LOCAL' and sub_qos.get('durability') == 'VOLATILE':
            warnings.append("⚠ 发布者(TRANSIENT_LOCAL) 与 订阅者(VOLATILE) 持久性不兼容")
        
        if pub_qos.get('durability') == 'TRANSIENT' and sub_qos.get('durability') == 'VOLATILE':
            warnings.append("⚠ 发布者(TRANSIENT) 与 订阅者(VOLATILE) 持久性不兼容")
        
        return warnings
    
    @staticmethod
    def get_qos_summary(topic_info) -> str:
        lines = []
        
        if topic_info.publishers:
            lines.append("发布者 (Publishers):")
            for i, pub in enumerate(topic_info.publishers, 1):
                lines.append(f"  [{i}] 节点: {pub.get('node', 'N/A')}")
                qos = pub.get('qos', {})
                lines.append(f"      可靠性: {qos.get('reliability', 'N/A')}")
                lines.append(f"      持久性: {qos.get('durability', 'N/A')}")
                lines.append(f"      队列深度: {qos.get('depth', 'N/A')}")
        
        if topic_info.subscribers:
            lines.append("\n订阅者 (Subscribers):")
            for i, sub in enumerate(topic_info.subscribers, 1):
                lines.append(f"  [{i}] 节点: {sub.get('node', 'N/A')}")
                qos = sub.get('qos', {})
                lines.append(f"      可靠性: {qos.get('reliability', 'N/A')}")
                lines.append(f"      持久性: {qos.get('durability', 'N/A')}")
                lines.append(f"      队列深度: {qos.get('depth', 'N/A')}")
        
        if topic_info.qos_warnings:
            lines.append("\n⚠ 兼容性警告:")
            for warn in topic_info.qos_warnings:
                lines.append(f"  {warn}")
        
        return '\n'.join(lines)
