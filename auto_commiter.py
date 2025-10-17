#!/usr/bin/env python3
import subprocess
import datetime
import os

# تبسيط كامل - أقل من 30 سطر
def main():
    os.chdir("/home/frappe/frappe-bench-15/apps/posawesome")
    
    # git status --porcelain
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        return
    
    # أول ملف متغير
    first_file = result.stdout.split('\n')[0][2:].strip()
    
    # git add
    subprocess.run(f'git add "{first_file}"', shell=True)
    
    # git commit
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(f'git commit -m "Auto: {first_file} at {timestamp}"', shell=True)
    
    # git push
    subprocess.run("git push origin main", shell=True)

if __name__ == "__main__":
    main()