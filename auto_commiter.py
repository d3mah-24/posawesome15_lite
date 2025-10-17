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
    
    # Get first file from git status
    first_line = result.stdout.split('\n')[0].strip()
    filename = first_line[2:].strip()
    
    # Git operations
    subprocess.run(f'git add "{filename}"', shell=True)
    subprocess.run(f'git commit -m "{filename}" -- "{filename}"', shell=True)
    subprocess.run("git push origin main", shell=True)

if __name__ == "__main__":
    main()