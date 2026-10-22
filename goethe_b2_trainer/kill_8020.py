import os, sys, subprocess

# Run netstat
out = subprocess.check_output("netstat -ano", shell=True).decode()
pids = set()
for line in out.splitlines():
    if ":8020 " in line and "LISTENING" in line:
        parts = line.strip().split()
        pid = parts[-1]
        pids.add(int(pid))

print(f"Found PIDs on port 8020: {pids}")
for pid in pids:
    print(f"Killing PID {pid}...")
    try:
        subprocess.check_call(f"taskkill /F /PID {pid}", shell=True)
        print(f"Successfully killed {pid}")
    except Exception as e:
        print(f"Failed to kill {pid}: {e}")
