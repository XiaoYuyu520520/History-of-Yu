#!/usr/bin/env python3
import os, sys, subprocess, platform, signal, socket, time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
PORT = os.environ.get("PORT", "7777")

BINARIES = {
    ("Linux", "aarch64"): "netspeed-linux-arm64",
    ("Linux", "arm64"):   "netspeed-linux-arm64",
    ("Linux", "x86_64"):  "netspeed-linux-amd64",
    ("Linux", "amd64"):   "netspeed-linux-amd64",
    ("Windows", "AMD64"): "netspeed-windows-amd64.exe",
    ("Windows", "x86_64"):"netspeed-windows-amd64.exe",
}

def get_ips():
    try:
        out = subprocess.check_output(["hostname", "-I"], text=True).strip()
        return [ip for ip in out.split() if not ip.startswith("127.")]
    except:
        pass
    try:
        return list(set(a[4][0] for a in socket.getaddrinfo(socket.gethostname(), None)
                      if a[0] == socket.AF_INET and not a[4][0].startswith("127.")))
    except:
        return []

def detect_binary():
    system, machine = platform.system(), platform.machine().lower()
    key = (system, machine)
    alt = {"aarch64": "arm64", "arm64": "aarch64", "x86_64": "amd64", "amd64": "x86_64"}
    if key not in BINARIES and machine in alt:
        key = (system, alt[machine])
    name = BINARIES.get(key)
    if not name:
        print(f"Unsupported: {system} {machine}"); sys.exit(1)
    path = os.path.join(BUILD_DIR, name)
    if not os.path.exists(path):
        print(f"Binary not found: {path}")
        print("Compile first: cd", PROJECT_DIR, "&& bash build.sh")
        sys.exit(1)
    return path

def start_server(binary):
    env = os.environ.copy(); env["PORT"] = PORT
    proc = subprocess.Popen([binary], env=env, cwd=PROJECT_DIR,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    if proc.poll() is not None:
        print("Server failed to start!"); sys.exit(1)
    return proc

def print_banner(binary, ips):
    print()
    print("=" * 54)
    print("   NetSpeed - Network Speed Test")
    print("=" * 54)
    print(f"   Binary: {os.path.basename(binary)}")
    print(f"   Platform: {platform.system()} {platform.machine()}")
    print(f"   Port: {PORT}")
    print("-" * 54)
    print("   Access URLs:")
    print(f"      Local:   http://localhost:{PORT}")
    for ip in ips:
        print(f"      Network: http://{ip}:{PORT}")
    print("-" * 54)
    print("   Press Ctrl+C to stop the server")
    print("=" * 54)
    print()

def main():
    binary = detect_binary()
    ips = get_ips()
    proc = start_server(binary)
    print_banner(binary, ips)

    def cleanup(signum=None, frame=None):
        print("\nShutting down...")
        proc.terminate()
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try: proc.wait()
    except KeyboardInterrupt: cleanup()

if __name__ == "__main__":
    main()
