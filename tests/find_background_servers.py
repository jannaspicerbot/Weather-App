"""
Find and identify background servers running for the Weather App
"""

import os
import sys
import subprocess
import socket

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def check_port(port, description):
    """Check if a port is in use and by what process"""
    print(f"\n🔍 Checking port {port} ({description})...")

    # Try to connect to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()

    if result == 0:
        print(f"   ✅ Port {port} is ACTIVE")

        # Find process using PowerShell
        try:
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

            if result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                print(f"   📍 Process ID: {pid}")

                # Get process details
                cmd2 = f'powershell -Command "Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object ProcessName, Path, StartTime"'
                result2 = subprocess.run(cmd2, capture_output=True, text=True, shell=True)

                if result2.stdout.strip():
                    print(f"   📋 Process Details:")
                    for line in result2.stdout.strip().split('\n'):
                        if line.strip() and not line.startswith('ProcessName'):
                            print(f"      {line}")

                return pid
            else:
                print(f"   ⚠️  Could not identify process")
                return None
        except Exception as e:
            print(f"   ⚠️  Error finding process: {e}")
            return None
    else:
        print(f"   ❌ Port {port} is not in use")
        return None


def find_node_processes():
    """Find all Node.js processes (Vite dev server)"""
    print("\n🔍 Searching for Node.js/Vite processes...")

    try:
        cmd = 'powershell -Command "Get-Process | Where-Object {$_.ProcessName -like \'*node*\'} | Select-Object Id, ProcessName, Path, StartTime"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.stdout.strip() and not 'Id' in result.stdout:
            print("   ✅ Found Node.js processes:")
            print(result.stdout)
            return True
        else:
            print("   ❌ No Node.js processes found")
            return False
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return False


def find_python_processes():
    """Find all Python processes (FastAPI/uvicorn/scheduler)"""
    print("\n🔍 Searching for Python processes...")

    try:
        cmd = 'powershell -Command "Get-Process | Where-Object {$_.ProcessName -like \'*python*\'} | Select-Object Id, ProcessName, Path, StartTime"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.stdout.strip() and not result.stdout.strip().startswith('Get-Process'):
            lines = result.stdout.strip().split('\n')
            python_procs = [line for line in lines if line.strip() and not line.startswith('Id')]

            if python_procs:
                print(f"   ✅ Found {len(python_procs)} Python process(es):")
                for line in python_procs:
                    print(f"      {line}")
                return python_procs
            else:
                print("   ❌ No Python processes found")
                return []
        else:
            print("   ❌ No Python processes found")
            return []
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return []


def kill_process(pid, process_name):
    """Kill a process by PID"""
    print(f"\n⚠️  Attempting to stop {process_name} (PID: {pid})...")

    try:
        # Use taskkill
        cmd = f'taskkill /F /PID {pid}'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            print(f"   ✅ Successfully stopped process {pid}")
            return True
        else:
            print(f"   ❌ Failed to stop process: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("="*80)
    print("WEATHER APP - BACKGROUND SERVER FINDER")
    print("="*80)
    print()
    print("This script will:")
    print("  1. Check if ports 5173 (Vite) and 8000 (FastAPI) are in use")
    print("  2. Identify processes using those ports")
    print("  3. Find all Node.js and Python processes")
    print("  4. Offer to stop them")
    print()
    print("="*80)

    # Check common ports
    vite_pid = check_port(5173, "Vite dev server")
    fastapi_pid = check_port(8000, "FastAPI backend")

    # Find all relevant processes
    node_found = find_node_processes()
    python_procs = find_python_processes()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    processes_to_kill = []

    if vite_pid:
        print(f"✅ Vite dev server (port 5173): Running (PID: {vite_pid})")
        processes_to_kill.append(('Vite dev server', vite_pid))
    else:
        print("❌ Vite dev server (port 5173): Not running")

    if fastapi_pid:
        print(f"✅ FastAPI backend (port 8000): Running (PID: {fastapi_pid})")
        processes_to_kill.append(('FastAPI backend', fastapi_pid))
    else:
        print("❌ FastAPI backend (port 8000): Not running")

    if python_procs:
        print(f"⚠️  Found {len(python_procs)} Python process(es) - may include scheduler")

    # Offer to kill processes
    if processes_to_kill:
        print("\n" + "="*80)
        print("STOP PROCESSES")
        print("="*80)
        print("Found the following processes to stop:")
        for name, pid in processes_to_kill:
            print(f"  - {name} (PID: {pid})")

        print()
        response = input("Stop these processes? (y/n): ").strip().lower()

        if response == 'y':
            for name, pid in processes_to_kill:
                kill_process(pid, name)

            print("\n✅ Done! Processes have been stopped.")
            print("   Verify by checking if localhost:5173 still loads in your browser.")
        else:
            print("\n⚠️  Processes were NOT stopped.")
            print("   You can manually stop them using Task Manager.")
    else:
        print("\n⚠️  No processes found on ports 5173 or 8000")
        print("   But localhost:5173 is serving data, so something else is running.")
        print()
        print("Possible explanations:")
        print("  1. The server is on a different port")
        print("  2. The frontend is using cached data")
        print("  3. The frontend is using test data")

        if python_procs:
            print("\nFound Python processes. One of these might be the scheduler:")
            print("Check Task Manager for 'python.exe' processes and their command lines.")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("After stopping servers:")
    print("  1. Verify localhost:5173 is no longer accessible")
    print("  2. Re-run the diagnostic: python tests/diagnose_api_fixes.py")
    print("  3. Monitor API calls without interference from background processes")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
