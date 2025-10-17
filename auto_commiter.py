#!/usr/bin/env python3
"""
Simple Auto Git Commit & Push
Just commits all changes and pushes with basic logging
"""

import os
import subprocess
import datetime

# Configuration
REPO_PATH = "/home/frappe/frappe-bench-15/apps/posawesome"
LOG_FILE = "/home/frappe/frappe-bench-15/apps/posawesome/auto_commiter.log"

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_git(command):
    """Run git command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def commit_and_push():
    """Commit each file separately, then push all"""
    os.chdir(REPO_PATH)
    
    # Check if there are any changes
    success, status, error = run_git("git status --porcelain")
    if not success or not status.strip():
        log("No changes to commit")
        return True
    
    # Get list of changed files
    files = []
    for line in status.split('\n'):
        if line.strip():
            files.append(line[3:].strip())
    
    log(f"Found {len(files)} changed files: {', '.join(files)}")
    
    committed_count = 0
    commit_ids = []
    
    # Commit each file separately
    for filepath in files:
        # Add single file
        success, output, error = run_git(f'git add "{filepath}"')
        if not success:
            log(f"Failed to add {filepath}: {error}")
            continue
        
        # Commit single file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-commit: {filepath} at {timestamp}"
        
        success, output, error = run_git(f'git commit -m "{commit_msg}"')
        if success:
            # Get commit ID
            success, commit_id, error = run_git("git rev-parse --short HEAD")
            if success:
                commit_ids.append(commit_id)
                log(f"Committed: {commit_id} - {filepath}")
                committed_count += 1
        else:
            if "nothing to commit" not in error:
                log(f"Failed to commit {filepath}: {error}")
    
    if committed_count > 0:
        # Push all commits
        success, output, error = run_git("git push origin main")
        if success:
            log(f"Pushed {committed_count} commits successfully: {', '.join(commit_ids)}")
            return True
        else:
            log(f"Failed to push: {error}")
            return False
    
    return True

def main():
    """Main function"""
    log("=== Auto-commit started ===")
    success = commit_and_push()
    if success:
        log("=== Auto-commit completed successfully ===")
    else:
        log("=== Auto-commit failed ===")

if __name__ == "__main__":
    main()