"""Interactive menu for WLAN Scanner."""

import os
import sys
from typing import List, Callable, Any, Optional

try:
    from colorama import Fore, Style
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

from config import Config


class Menu:
    """Interactive menu system."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.use_colors = COLORAMA_AVAILABLE
    
    @property
    def c(self):
        return Fore.CYAN if self.use_colors else ''
    
    @property
    def g(self):
        return Fore.GREEN if self.use_colors else ''
    
    @property
    def y(self):
        return Fore.YELLOW if self.use_colors else ''
    
    @property
    def r(self):
        return Fore.RED if self.use_colors else ''
    
    @property
    def m(self):
        return Fore.MAGENTA if self.use_colors else ''
    
    @property
    def w(self):
        return Fore.WHITE if self.use_colors else ''
    
    @property
    def rs(self):
        return Style.RESET_ALL if self.use_colors else ''
    
    @property
    def bm(self):
        return Style.BRIGHT if self.use_colors else ''
    
    def clear(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def header(self, title: str) -> None:
        width = 60
        print()
        print(f"{self.c}{'='*width}{self.rs}")
        print(f"{self.c}{title:^{width}}{self.rs}")
        print(f"{self.c}{'='*width}{self.rs}")
        print()
    
    def footer(self) -> None:
        width = 60
        print(f"{self.c}{'='*width}{self.rs}")
        print()
    
    def prompt(self, text: str) -> str:
        return input(f"{self.g}➜ {self.w}{text}: {self.rs}")
    
    def confirm(self, text: str, default: bool = True) -> bool:
        suffix = " [Y/n]" if default else " [y/N]"
        while True:
            result = self.prompt(f"{text}{suffix}")
            if not result:
                return default
            result = result.lower().strip()
            if result in ('y', 'yes'):
                return True
            if result in ('n', 'no'):
                return False
            print(f"{self.r}请输入 y 或 n{self.rs}")
    
    def choose(self, title: str, options: List[str], 
               default: int = 0, format_func: Optional[Callable] = None) -> int:
        print(f"\n{self.c}{title}{self.rs}")
        print(f"{self.c}{'-'*40}{self.rs}")
        
        for i, option in enumerate(options):
            if format_func:
                display = format_func(i, option, i == default)
            else:
                marker = "●" if i == default else "○"
                display = f"  {marker} {option}"
            
            if i == default:
                print(f"{self.g}{display}{self.rs}")
            else:
                print(f"  {display}")
        
        print()
        
        while True:
            result = self.prompt(f"请选择 [0-{len(options)-1}], 默认 [{default}]")
            if not result:
                return default
            try:
                idx = int(result)
                if 0 <= idx < len(options):
                    return idx
                print(f"{self.r}请输入 0 到 {len(options)-1} 之间的数字{self.rs}")
            except ValueError:
                print(f"{self.r}请输入有效的数字{self.rs}")
    
    def input_with_default(self, title: str, default: Any, 
                          validator: Optional[Callable] = None) -> Any:
        default_str = str(default) if default is not None else ""
        prompt_text = f"{title}"
        if default_str:
            prompt_text += f" [{default_str}]"
        
        while True:
            result = self.prompt(prompt_text)
            if not result:
                return default
            if validator:
                try:
                    return validator(result)
                except Exception as e:
                    print(f"{self.r}{e}{self.rs}")
            else:
                return result
    
    def input_subnet(self) -> str:
        from discovery import SubnetDetector
        
        detector = SubnetDetector()
        subnets = detector.detect_all_subnets()
        
        if not subnets:
            return self.input_with_default("请输入网段 (CIDR格式)", "192.168.1.0/24")
        
        options = ["手动输入"] + [s.cidr for s in subnets]
        idx = self.choose("请选择要扫描的网段", options, default=0)
        
        if idx == 0:
            return self.input_with_default("请输入网段 (CIDR格式)", "192.168.1.0/24")
        else:
            return subnets[idx - 1].cidr


class InteractiveMenu:
    """Main interactive menu for WLAN Scanner."""
    
    def __init__(self, config: Optional[Config] = None):
        self.menu = Menu(config)
        self.config = config or Config()
        self.args = None
    
    def run(self):
        while True:
            self._main_menu()
            
            if self.args:
                self._execute_scan()
    
    def _main_menu(self):
        self.menu.clear()
        self.menu.header(" WLAN Scanner  网络扫描工具 ")
        
        print(f"  {self.menu.g}1.{self.menu.rs} 检测本机网段")
        print(f"  {self.menu.g}2.{self.menu.rs} 寻找互联网网关")
        print(f"  {self.menu.g}3.{self.menu.rs} 扫描局域网设备")
        print(f"  {self.menu.g}4.{self.menu.rs} 扫描指定网段")
        print()
        print(f"  {self.menu.y}5.{self.menu.rs} 设置默认选项")
        print(f"  {self.menu.y}6.{self.menu.rs} 查看当前配置")
        print()
        print(f"  {self.menu.r}0.{self.menu.rs} 退出")
        
        self.menu.footer()
        
        choice = self.menu.input_with_default("请选择操作", "3")
        
        if choice == "0":
            print(f"\n{self.menu.g}再见！{self.menu.rs}")
            sys.exit(0)
        elif choice == "1":
            self._detect_subnets()
        elif choice == "2":
            self._find_gateway()
        elif choice == "3":
            self._prepare_scan_local()
        elif choice == "4":
            self._prepare_scan_subnet()
        elif choice == "5":
            self._settings_menu()
        elif choice == "6":
            self._show_config()
        else:
            self.args = None
    
    def _detect_subnets(self):
        from discovery import SubnetDetector
        
        print(f"\n{self.menu.c}正在检测网段...{self.menu.rs}\n")
        detector = SubnetDetector()
        subnets = detector.detect_all_subnets()
        
        if not subnets:
            print(f"{self.menu.r}未发现任何网段{self.menu.rs}")
        else:
            print(f"{self.menu.g}发现 {len(subnets)} 个网络接口:{self.menu.rs}\n")
            for i, s in enumerate(subnets, 1):
                print(f"  {self.menu.g}{i}.{self.menu.rs} {s.interface}")
                print(f"      网段: {s.cidr}")
                print(f"      子网掩码: {s.netmask}")
                if s.gateway:
                    print(f"      网关: {s.gateway}")
                print()
        
        self.menu.prompt("按回车继续...")
    
    def _find_gateway(self):
        from discovery import GatewayFinder
        
        print(f"\n{self.menu.c}正在寻找网关...{self.menu.rs}\n")
        finder = GatewayFinder()
        gateway = finder.find_internet_exit()
        
        if gateway:
            print(f"{self.menu.g}找到互联网网关:{self.menu.rs}")
            print(f"  IP地址: {gateway.ip_address}")
            print(f"  接口: {gateway.interface}")
            reachable = f"{self.menu.g}是{self.menu.rs}" if gateway.can_reach_internet else f"{self.menu.r}否{self.menu.rs}"
            print(f"  可访问互联网: {reachable}")
            if gateway.latency_ms:
                print(f"  延迟: {gateway.latency_ms:.2f}ms")
        else:
            print(f"{self.menu.r}未找到网关{self.menu.rs}")
        
        self.menu.prompt("\n按回车继续...")
    
    def _prepare_scan_local(self):
        self.menu.clear()
        self.menu.header(" 扫描局域网设备 ")
        
        ports_options = [
            "常用端口 (约50个)",
            "全部端口 (0-65535)",
            "自定义端口"
        ]
        ports_idx = self.menu.choose("请选择端口扫描范围", ports_options, 
                                     default={"common": 0, "all": 1}.get(self.config.ports, 0))
        
        if ports_idx == 0:
            self.args_ports = "common"
        elif ports_idx == 1:
            self.args_ports = "all"
        else:
            self.args_ports = self.menu.input_with_default("请输入端口 (逗号分隔)", "22,80,443")
        
        self.args_enrich = self.menu.confirm("是否获取设备详细信息 (MAC/主机名/厂商)", 
                                              default=self.config.enrich)
        
        output_options = ["终端输出", "JSON文件", "CSV文件", "JSON + CSV"]
        output_idx = self.menu.choose("请选择输出方式", output_options, 
                                      default={"console": 0, "json": 1, "csv": 2, "both": 3}.get(
                                          self.config.output_format, 0))
        
        self.args_output_json = None
        self.args_output_csv = None
        
        if output_idx == 1:
            self.args_output_json = self.menu.input_with_default("JSON文件名", self.config.json_file)
        elif output_idx == 2:
            self.args_output_csv = self.menu.input_with_default("CSV文件名", self.config.csv_file)
        elif output_idx == 3:
            self.args_output_json = self.menu.input_with_default("JSON文件名", self.config.json_file)
            self.args_output_csv = self.menu.input_with_default("CSV文件名", self.config.csv_file)
        
        self.args_scan_local = True
        self.args_subnet = None
        self.args = True
    
    def _prepare_scan_subnet(self):
        self.menu.clear()
        self.menu.header(" 扫描指定网段 ")
        
        self.args_subnet = self.menu.input_subnet()
        
        ports_options = [
            "常用端口 (约50个)",
            "全部端口 (0-65535)",
            "自定义端口"
        ]
        ports_idx = self.menu.choose("请选择端口扫描范围", ports_options, 
                                     default={"common": 0, "all": 1}.get(self.config.ports, 0))
        
        if ports_idx == 0:
            self.args_ports = "common"
        elif ports_idx == 1:
            self.args_ports = "all"
        else:
            self.args_ports = self.menu.input_with_default("请输入端口 (逗号分隔)", "22,80,443")
        
        self.args_enrich = self.menu.confirm("是否获取设备详细信息 (MAC/主机名/厂商)", 
                                              default=self.config.enrich)
        
        output_options = ["终端输出", "JSON文件", "CSV文件", "JSON + CSV"]
        output_idx = self.menu.choose("请选择输出方式", output_options, 
                                      default={"console": 0, "json": 1, "csv": 2, "both": 3}.get(
                                          self.config.output_format, 0))
        
        self.args_output_json = None
        self.args_output_csv = None
        
        if output_idx == 1:
            self.args_output_json = self.menu.input_with_default("JSON文件名", self.config.json_file)
        elif output_idx == 2:
            self.args_output_csv = self.menu.input_with_default("CSV文件名", self.config.csv_file)
        elif output_idx == 3:
            self.args_output_json = self.menu.input_with_default("JSON文件名", self.config.json_file)
            self.args_output_csv = self.menu.input_with_default("CSV文件名", self.config.csv_file)
        
        self.args_scan_local = False
        self.args = True
    
    def _settings_menu(self):
        while True:
            self.menu.clear()
            self.menu.header(" 设置默认选项 ")
            
            print(f"  {self.menu.g}1.{self.menu.rs} 并发数: {self.config.concurrency}")
            print(f"  {self.menu.g}2.{self.menu.rs} 超时时间: {self.config.timeout}秒")
            print(f"  {self.menu.g}3.{self.menu.rs} 默认端口: {self.config.ports}")
            print(f"  {self.menu.g}4.{self.menu.rs} 自动获取设备信息: {'是' if self.config.enrich else '否'}")
            print()
            print(f"  {self.menu.y}5.{self.menu.rs} 输出格式: {self.config.output_format}")
            print(f"  {self.menu.y}6.{self.menu.rs} JSON文件名: {self.config.json_file}")
            print(f"  {self.menu.y}7.{self.menu.rs} CSV文件名: {self.config.csv_file}")
            print()
            print(f"  {self.menu.c}8.{self.menu.rs} 恢复默认设置")
            print()
            print(f"  {self.menu.r}0.{self.menu.rs} 返回")
            
            self.menu.footer()
            
            choice = self.menu.input_with_default("请选择", "0")
            
            if choice == "0":
                break
            elif choice == "1":
                value = self.menu.input_with_default("并发数 (50-1000)", self.config.concurrency)
                try:
                    self.config.concurrency = max(50, min(1000, int(value)))
                except:
                    print(f"{self.menu.r}请输入有效数字{self.menu.rs}")
            elif choice == "2":
                value = self.menu.input_with_default("超时时间 (0.1-10秒)", self.config.timeout)
                try:
                    self.config.timeout = max(0.1, min(10, float(value)))
                except:
                    print(f"{self.menu.r}请输入有效数字{self.menu.rs}")
            elif choice == "3":
                options = ["common", "all"]
                idx = self.menu.choose("默认端口", options, default=0)
                self.config.ports = options[idx]
            elif choice == "4":
                self.config.enrich = self.menu.confirm("自动获取设备信息", default=self.config.enrich)
            elif choice == "5":
                options = ["console", "json", "csv", "both"]
                idx = self.menu.choose("输出格式", options, default=0)
                self.config.output_format = options[idx]
            elif choice == "6":
                self.config.json_file = self.menu.input_with_default("JSON文件名", self.config.json_file)
            elif choice == "7":
                self.config.csv_file = self.menu.input_with_default("CSV文件名", self.config.csv_file)
            elif choice == "8":
                if self.menu.confirm("确定要恢复默认设置吗"):
                    self.config.reset()
                    print(f"{self.menu.g}已恢复默认设置{self.menu.rs}")
    
    def _show_config(self):
        self.menu.clear()
        self.menu.header(" 当前配置 ")
        
        print(f"  并发数: {self.config.concurrency}")
        print(f"  超时时间: {self.config.timeout}秒")
        print(f"  默认端口: {self.config.ports}")
        print(f"  自动获取设备信息: {'是' if self.config.enrich else '否'}")
        print(f"  输出格式: {self.config.output_format}")
        print(f"  JSON文件名: {self.config.json_file}")
        print(f"  CSV文件名: {self.config.csv_file}")
        
        self.menu.prompt("\n按回车继续...")
    
    def _execute_scan(self):
        from main import detect_subnets, find_gateway, scan_network, scan_local_network, output_results
        
        class Args:
            pass
        
        args = Args()
        args.subnet = getattr(self, 'args_subnet', None)
        args.scan_local = getattr(self, 'args_scan_local', False)
        args.concurrency = self.config.concurrency
        args.timeout = self.config.timeout
        args.enrich = getattr(self, 'args_enrich', self.config.enrich)
        args.ports = getattr(self, 'args_ports', self.config.ports)
        args.full_port = args.ports == "all"
        args.output_json = getattr(self, 'args_output_json', None)
        args.output_csv = getattr(self, 'args_output_csv', None)
        args.output_format = "console"
        
        print(f"\n{self.menu.c}开始扫描...{self.menu.rs}\n")
        
        if args.scan_local:
            devices = scan_local_network(args)
        else:
            devices = scan_network(args)
        
        if devices:
            output_results(devices, args)
        
        self.menu.prompt("\n扫描完成，按回车继续...")
        
        self.args = None
