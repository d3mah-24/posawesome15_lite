#!/usr/bin/env python3
import subprocess
import datetime
import os

def main():
    os.chdir("/home/frappe/frappe-bench-15/apps/posawesome")
    
    # Get changed files
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return
    
    # Collect files
    files = []
    for line in result.stdout.split('\n'):
        if line.strip():
            filename = line[2:].strip()
            files.append(filename)
    
    # Sort by modification time - oldest first
    files.sort(key=lambda f: os.path.getmtime(f))
    oldest_file = files[0]
    
    # Git operations
    subprocess.run(f'git add "{oldest_file}"', shell=True)
    
    subprocess.run(f'git commit -m "{oldest_file}"', shell=True)
    
    subprocess.run("git push origin main", shell=True)

if __name__ == "__main__":
    main()