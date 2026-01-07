"""
Stop all weather app servers (FastAPI, scheduler, etc.)
"""

import socket
import subprocess
import sys
import time

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def check_port(port):
    """Check if port is active"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    return result == 0


def find_process_on_port(port):
    """Find PID of process using a port"""
    try:
        cmd = f"netstat -ano | findstr :{port}"
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        for line in result.stdout.strip().split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                return pid
    except:
        pass
    return None


def kill_by_pid(pid):
    """Kill process by PID"""
    try:
        subprocess.run(f"taskkill //F //PID {pid}", shell=True, capture_output=True)
        return True
    except:
        return False


print("=" * 60)
print("STOP ALL WEATHER APP SERVERS")
print("=" * 60)

# Check port 8000 (FastAPI)
if check_port(8000):
    print("\n✅ Found server on port 8000 (FastAPI)")
    pid = find_process_on_port(8000)

    if pid:
        print(f"   PID: {pid}")
        print(f"   Stopping...")
        if kill_by_pid(pid):
            print(f"   ✅ Stopped!")
        else:
            print(f"   ❌ Failed to stop")

        time.sleep(2)

        if check_port(8000):
            print(f"   ⚠️  Port 8000 still active, trying again...")
            kill_by_pid(pid)
            time.sleep(2)
    else:
        print("   ⚠️  Could not find PID")
else:
    print("\n❌ No server on port 8000")

# Check port 5173 (Vite)
if check_port(5173):
    print("\n✅ Found server on port 5173 (Vite)")
    pid = find_process_on_port(5173)

    if pid:
        print(f"   PID: {pid}")
        print(f"   Stopping...")
        if kill_by_pid(pid):
            print(f"   ✅ Stopped!")
        else:
            print(f"   ❌ Failed to stop")

        time.sleep(2)
    else:
        print("   ⚠️  Could not find PID")
else:
    print("\n❌ No server on port 5173")

# Final check
print("\n" + "=" * 60)
print("FINAL STATUS")
print("=" * 60)
port_8000_active = check_port(8000)
port_5173_active = check_port(5173)

if port_8000_active:
    print("❌ Port 8000: STILL ACTIVE")
    print("   Try manually stopping via Task Manager")
    print("   Look for 'python.exe' processes")
else:
    print("✅ Port 8000: FREE")

if port_5173_active:
    print("❌ Port 5173: STILL ACTIVE")
    print("   Try manually stopping via Task Manager")
    print("   Look for 'node.exe' processes")
else:
    print("✅ Port 5173: FREE")

print("\n" + "=" * 60)

if not port_8000_active and not port_5173_active:
    print("✅ All servers stopped successfully!")
else:
    print("⚠️  Some servers may still be running")
    print("   Check Task Manager and manually stop if needed")

print("=" * 60)
