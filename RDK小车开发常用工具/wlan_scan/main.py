#!/usr/bin/env python3
"""WLAN Scanner - Network discovery and scanning tool.

A cross-platform tool for discovering network subnets, finding internet exit points,
scanning local networks, and gathering detailed device information including
MAC addresses, hostnames, vendors, and open ports.
"""

import argparse
import sys
import time
from typing import List, Optional

from core.network_utils import NetworkUtils
from core.logger import setup_logger, get_logger
from discovery import SubnetDetector, GatewayFinder
from scanner import LanScanner, PortScanner, DeviceInfo
from models import Device
from output import ConsoleWriter, JsonWriter, CsvWriter

setup_logger()
logger = get_logger(__name__)


def detect_subnets(args) -> List:
    """Detect local network subnets."""
    print("\n=== Detecting Network Subnets ===\n")
    
    detector = SubnetDetector()
    subnets = detector.detect_all_subnets()
    
    if not subnets:
        print("No network subnets found.")
        return []
    
    print(f"Found {len(subnets)} network interface(s):\n")
    for subnet in subnets:
        print(f"  Interface: {subnet.interface}")
        print(f"  Network: {subnet.cidr}")
        print(f"  Netmask: {subnet.netmask}")
        if subnet.gateway:
            print(f"  Gateway: {subnet.gateway}")
        print()
    
    return subnets


def find_gateway(args) -> Optional:
    """Find internet gateway."""
    print("\n=== Finding Internet Gateway ===\n")
    
    finder = GatewayFinder()
    gateway = finder.find_internet_exit()
    
    if gateway:
        console = ConsoleWriter()
        console.write_gateway(gateway)
        return gateway
    else:
        print("No internet gateway found.")
        return None


def scan_network(args) -> List[Device]:
    """Scan a network for devices."""
    subnet = args.subnet
    concurrency = args.concurrency
    timeout = args.timeout
    
    print(f"\n=== Scanning Network: {subnet} ===")
    print(f"Concurrency: {concurrency}, Timeout: {timeout}s\n")
    
    scanner = LanScanner(concurrency=concurrency, timeout=timeout)
    start_time = time.time()
    
    devices = scanner.scan_network(subnet, show_progress=True)
    
    duration = time.time() - start_time
    
    if not devices:
        print("No devices found.")
        return []
    
    if args.full_port or args.ports == 'all':
        print(f"\n=== Scanning Ports (0-65535) ===")
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning ports on {device.ip}...")
            device.open_ports = port_scanner.scan_ports(device.ip, show_progress=False)
    elif args.ports and args.ports != 'common':
        print(f"\n=== Scanning Ports ({args.ports}) ===")
        port_list = args.ports.split(',')
        port_list = [int(p.strip()) for p in port_list]
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning ports on {device.ip}...")
            device.open_ports = port_scanner.scan_ports(device.ip, port_list, show_progress=False)
    else:
        print(f"\n=== Scanning Common Ports ===")
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning common ports on {device.ip}...")
            device.open_ports = port_scanner.scan_common_ports(device.ip)
    
    if args.enrich or args.full_port or args.ports != 'common':
        print(f"\n=== Enriching Device Information ===")
        device_info = DeviceInfo()
        
        for device in devices:
            print(f"  Getting info for {device.ip}...")
            device_info.enrich_device(device)
    
    print(f"\nScan completed in {duration:.2f} seconds")
    
    return devices


def scan_local_network(args) -> List[Device]:
    """Scan all local networks."""
    concurrency = args.concurrency
    timeout = args.timeout
    
    print(f"\n=== Scanning Local Networks ===")
    print(f"Concurrency: {concurrency}, Timeout: {timeout}s\n")
    
    scanner = LanScanner(concurrency=concurrency, timeout=timeout)
    start_time = time.time()
    
    devices = scanner.scan_local_network(show_progress=True)
    
    if args.full_port or args.ports == 'all':
        print(f"\n=== Scanning Ports (0-65535) ===")
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning ports on {device.ip}...")
            device.open_ports = port_scanner.scan_ports(device.ip, show_progress=False)
    elif args.ports and args.ports != 'common':
        port_list = args.ports.split(',')
        port_list = [int(p.strip()) for p in port_list]
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning ports on {device.ip}...")
            device.open_ports = port_scanner.scan_ports(device.ip, port_list, show_progress=False)
    else:
        print(f"\n=== Scanning Common Ports ===")
        port_scanner = PortScanner(concurrency=concurrency)
        
        for device in devices:
            print(f"  Scanning common ports on {device.ip}...")
            device.open_ports = port_scanner.scan_common_ports(device.ip)
    
    if args.enrich or args.full_port or args.ports != 'common':
        print(f"\n=== Enriching Device Information ===")
        device_info = DeviceInfo()
        
        for device in devices:
            print(f"  Getting info for {device.ip}...")
            device_info.enrich_device(device)
    
    duration = time.time() - start_time
    print(f"\nTotal scan completed in {duration:.2f} seconds")
    
    return devices


def output_results(devices: List[Device], args) -> None:
    """Output scan results in specified formats."""
    if args.output_format == 'console' or (not args.output_json and not args.output_csv):
        console = ConsoleWriter()
        console.write_devices(devices)
        console.write_summary(devices, args.subnet or 'local network')
    
    if args.output_json:
        json_writer = JsonWriter()
        json_writer.write_devices(devices, args.output_json)
    
    if args.output_csv:
        csv_writer = CsvWriter()
        csv_writer.write_devices(devices, args.output_csv)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='WLAN Scanner - Network discovery and scanning tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Scan local network:
    python main.py --scan-local

  Scan specific subnet:
    python main.py --subnet 192.168.1.0/24

  Scan with full port scan:
    python main.py --scan-local --full-port

  Scan and save to JSON:
    python main.py --subnet 192.168.1.0/24 --output-json results.json

  Scan and save to CSV:
    python main.py --subnet 192.168.1.0/24 --output-csv results.csv

  Find gateway:
    python main.py --find-gateway

  Detect subnets:
    python main.py --detect-subnets
        """
    )
    
    parser.add_argument('--detect-subnets', action='store_true',
                        help='Detect all local network subnets')
    parser.add_argument('--find-gateway', action='store_true',
                        help='Find internet gateway')
    parser.add_argument('--scan-local', action='store_true',
                        help='Scan all local network interfaces')
    parser.add_argument('--subnet', type=str,
                        help='Scan specific subnet (CIDR notation, e.g., 192.168.1.0/24)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode (menu-driven)')
    
    parser.add_argument('--full-port', action='store_true',
                        help='Scan all ports (0-65535)')
    parser.add_argument('--ports', type=str, default='common',
                        help='Ports to scan: "common" (default), "all", or comma-separated list (e.g., "22,80,443")')
    
    parser.add_argument('--concurrency', type=int, default=500,
                        help='Number of concurrent scans (default: 500)')
    parser.add_argument('--timeout', type=float, default=1.0,
                        help='Timeout for each host/port check in seconds (default: 1.0)')
    
    parser.add_argument('--enrich', action='store_true',
                        help='Enrich device info (MAC vendor, hostname)')
    
    parser.add_argument('--output-json', type=str, metavar='FILE',
                        help='Save results to JSON file')
    parser.add_argument('--output-csv', type=str, metavar='FILE',
                        help='Save results to CSV file')
    parser.add_argument('--output-format', type=str, choices=['console', 'json', 'csv'], default='console',
                        help='Output format (default: console)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress non-essential output')
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.quiet:
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    
    if args.interactive:
        from interactive import InteractiveMenu
        from config import Config
        menu = InteractiveMenu(Config())
        menu.run()
        return
    
    if not any([args.detect_subnets, args.find_gateway, args.scan_local, args.subnet]):
        parser.print_help()
        return
    
    devices = []
    
    if args.detect_subnets:
        detect_subnets(args)
    
    if args.find_gateway:
        find_gateway(args)
    
    if args.scan_local:
        devices = scan_local_network(args)
    elif args.subnet:
        devices = scan_network(args)
    
    if devices:
        output_results(devices, args)


if __name__ == '__main__':
    main()
