#!/usr/bin/env python3
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import Config, create_default_config
from scanner import Scanner
from msg_parser import MsgParser
from qos_parser import QoSParser
from saver import ResultSaver, ScanResult
from ui.selector import create_selector, create_viewer


class ROS2Helper:
    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.ros2_bin = self.config.get_ros2_bin()
        self.timeout = self.config.get('scan.timeout', 5)
        self.msg_timeout = self.config.get('scan.msg_parse_timeout', 5)
        self.refresh_interval = self.config.get('scan.refresh_interval', 2)
        self.strict_mode = not self.config.get('scan.strict_mode', False)
        
        self.scanner = Scanner(self.ros2_bin, self.timeout)
        self.msg_parser = MsgParser(self.ros2_bin, self.msg_timeout)
        self.qos_parser = QoSParser()
        
        self.topics = []
    
    def scan_once(self, parse_messages: bool = True) -> list:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 扫描话题中...")
        
        self.topics = self.scanner.scan_topics()
        
        if not self.topics:
            print("未发现任何活跃话题")
            return []
        
        print(f"发现 {len(self.topics)} 个话题，正在解析消息类型...")
        
        for topic in self.topics:
            topic.data_format = self.msg_parser.infer_data_format(topic.msg_type)
            
            if parse_messages and topic.msg_type and topic.msg_type != 'unknown':
                try:
                    sample = self.msg_parser.get_sample_message(topic.name, topic.msg_type)
                    topic.sample_message = sample
                    if sample and 'data_format' in sample:
                        topic.data_format = sample['data_format']
                except Exception as e:
                    if not self.strict_mode:
                        print(f"  警告: 无法解析话题 {topic.name}: {e}")
        
        return self.topics
    
    def scan_continuous(self, duration: int = None):
        print("实时监控模式已启动 (按 Ctrl+C 退出)")
        print("-" * 60)
        
        start_time = time.time()
        scan_count = 0
        
        try:
            while True:
                self.scan_once()
                scan_count += 1
                print(f"\n[扫描 #{scan_count}] 发现 {len(self.topics)} 个话题")
                
                if self.topics:
                    selector = create_selector(self.topics)
                    selected = selector.select()
                    
                    if selected:
                        viewer = create_viewer()
                        detail = viewer.view_details(selected, self.qos_parser, self.msg_parser)
                        print(detail)
                
                if duration and (time.time() - start_time) >= duration:
                    break
                
                print(f"\n{self.refresh_interval}秒后自动刷新...")
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n监控已停止")
        
        return self._ask_save()
    
    def interactive_select(self):
        if not self.topics:
            self.scan_once()
        
        if not self.topics:
            print("没有可选择的话题")
            return
        
        selector = create_selector(self.topics)
        selected = selector.select()
        
        if selected:
            viewer = create_viewer()
            detail = viewer.view_details(selected, self.qos_parser, self.msg_parser)
            print(detail)
            
            return selected
        
        return None
    
    def _ask_save(self) -> bool:
        if not self.topics:
            return False
        
        print("\n是否保存扫描结果?")
        print("  [j] 保存为 JSON")
        print("  [y] 保存为 YAML")
        print("  [b] 保存为 JSON 和 YAML")
        print("  [n] 不保存")
        
        choice = input("\n请选择 [b]: ").strip().lower() or 'b'
        
        formats = []
        if choice in ['j', 'json']:
            formats = ['json']
        elif choice in ['y', 'yaml']:
            formats = ['yaml']
        elif choice in ['b', 'both']:
            formats = ['json', 'yaml']
        else:
            print("已取消保存")
            return False
        
        save_dir = self.config.get('output.save_dir', '~/ros2_scans')
        saver = ResultSaver(os.path.expanduser(save_dir))
        result = ScanResult(self.topics)
        saved = saver.save(result, formats)
        
        print("\n保存成功:")
        for fmt, path in saved.items():
            print(f"  {fmt}: {path}")
        
        return True
    
    def run(self, args):
        if args.create_config:
            create_default_config()
            return
        
        if args.list_saved:
            save_dir = self.config.get('output.save_dir', '~/ros2_scans')
            saver = ResultSaver(os.path.expanduser(save_dir))
            files = saver.list_saved()
            if files:
                print("已保存的扫描结果:")
                for f in files:
                    print(f"  {f['name']} - {f['time']}")
            else:
                print("没有保存的扫描结果")
            return
        
        if args.monitor:
            self.scan_continuous(args.duration)
        else:
            self.scan_once()
            if self.topics:
                self.interactive_select()
                self._ask_save()


def main():
    parser = argparse.ArgumentParser(description='ROS2 话题扫描工具')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('--create-config', action='store_true', help='创建默认配置文件')
    parser.add_argument('-m', '--monitor', action='store_true', help='实时监控模式')
    parser.add_argument('-d', '--duration', type=int, default=None, help='监控持续时间(秒)')
    parser.add_argument('-l', '--list-saved', action='store_true', help='列出已保存的扫描结果')
    parser.add_argument('--ros2-bin', help='ROS2 可执行文件路径(覆盖配置)')
    
    args = parser.parse_args()
    
    helper = ROS2Helper(args.config)
    
    if args.ros2_bin:
        helper.ros2_bin = args.ros2_bin
        helper.scanner = Scanner(args.ros2_bin, helper.timeout)
        helper.msg_parser = MsgParser(args.ros2_bin, helper.msg_timeout)
    
    helper.run(args)


if __name__ == '__main__':
    main()
