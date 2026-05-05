from pick import Picker
from typing import List, Any, Optional
import sys


class TopicSelector:
    def __init__(self, topics: List[Any], title: str = "选择话题"):
        self.topics = topics
        self.title = title
    
    def select(self) -> Optional[Any]:
        if not self.topics:
            print("没有找到任何话题")
            return None
        
        options = self._format_options()
        
        try:
            picker = Picker(
                options=options,
                title=self.title,
                indicator='>'
            )
            selected = picker.start()
            
            if selected:
                return selected[0].get('topic')
        except Exception as e:
            print(f"交互式选择不可用: {e}")
            return self._fallback_select(options)
        
        return None
    
    def _fallback_select(self, options: List) -> Optional[Any]:
        print("\n" + "=" * 60)
        print(self.title)
        print("=" * 60)
        
        for i, opt in enumerate(options):
            print(f"  [{i+1}] {opt['display']}")
        
        print("\n请输入序号 (或 Enter 退出): ", end='')
        try:
            choice = input().strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]['topic']
        except:
            pass
        
        return None
    
    def _format_options(self) -> List[str]:
        options = []
        for i, topic in enumerate(self.topics):
            pub_count = len(topic.publishers)
            sub_count = len(topic.subscribers)
            compat = "OK" if topic.qos_compatible else "WARN"
            msg_type_short = topic.msg_type.split('/')[-1] if topic.msg_type else "?"
            
            option = {
                'display': f"{topic.name:<35} [{msg_type_short:<18}] P:{pub_count} S:{sub_count} {compat}",
                'topic': topic
            }
            options.append(option)
        
        return options


class TopicViewer:
    @staticmethod
    def view_details(topic_info, qos_parser, msg_parser) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"话题: {topic_info.name}")
        lines.append("=" * 60)
        
        lines.append(f"\n[消息类型]")
        lines.append(f"  {topic_info.msg_type}")
        
        lines.append(f"\n[数据格式]")
        lines.append(f"  {topic_info.data_format or 'unknown'}")
        
        lines.append(f"\n[发布者信息] ({len(topic_info.publishers)} 个)")
        for i, pub in enumerate(topic_info.publishers, 1):
            lines.append(f"  [{i}] 节点: {pub.get('node', 'N/A')}")
            qos = pub.get('qos', {})
            lines.append(f"      可靠性: {qos.get('reliability', 'N/A')}")
            lines.append(f"      持久性: {qos.get('durability', 'N/A')}")
            lines.append(f"      队列深度: {qos.get('depth', 'N/A')}")
        
        lines.append(f"\n[订阅者信息] ({len(topic_info.subscribers)} 个)")
        for i, sub in enumerate(topic_info.subscribers, 1):
            lines.append(f"  [{i}] 节点: {sub.get('node', 'N/A')}")
            qos = sub.get('qos', {})
            lines.append(f"      可靠性: {qos.get('reliability', 'N/A')}")
            lines.append(f"      持久性: {qos.get('durability', 'N/A')}")
            lines.append(f"      队列深度: {qos.get('depth', 'N/A')}")
        
        if topic_info.qos_warnings:
            lines.append(f"\n[QOS兼容性警告]")
            for warn in topic_info.qos_warnings:
                lines.append(f"  {warn}")
        
        if topic_info.sample_message:
            lines.append(f"\n[示例消息]")
            msg = topic_info.sample_message
            if 'error' in msg:
                lines.append(f"  错误: {msg.get('error')} - {msg.get('message', '')}")
            else:
                sample = msg.get('sample', {})
                for key, value in sample.items():
                    if isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for k, v in value.items():
                            lines.append(f"    {k}: {v}")
                    else:
                        lines.append(f"  {key}: {value}")
        
        lines.append("=" * 60)
        
        return '\n'.join(lines)


def create_selector(topics: List[Any]) -> TopicSelector:
    return TopicSelector(topics)


def create_viewer() -> TopicViewer:
    return TopicViewer()
