#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Auto Commit Script
Commits each changed file separately with its filename as commit message
"""

import subprocess
import sys
import os
from datetime import datetime


def run_command(command, cwd=None, capture_output=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def get_changed_files(repo_path):
    """Get list of changed files with their status"""
    code, stdout, stderr = run_command("git status --short", cwd=repo_path)
    if code != 0:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            # Extract status and filename from git status output
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                status = parts[0]
                filename = parts[1]
                files.append({'status': status, 'file': filename})
    return files


def commit_single_file(repo_path, file_info, branch="main"):
    """
    Commit a single file and push
    
    Args:
        repo_path: Path to git repository
        file_info: Dict with 'status' and 'file' keys
        branch: Git branch to push to
    
    Returns:
        bool: True if successful, False otherwise
    """
    filename = file_info['file']
    status = file_info['status']
    
    # Determine action based on status
    if 'D' in status:
        action = "Delete"
    elif 'M' in status:
        action = "Update"
    elif 'A' in status or '?' in status:
        action = "Add"
    else:
        action = "Update"
    
    # Generate commit message from filename
    commit_message = f"{action}: {filename}"
    
    print(f"\n� Processing: {filename}")
    print(f"   Status: {status}")
    print(f"   Message: {commit_message}")
    
    # Step 1: Add this specific file
    print(f"   ➕ Adding file...")
    code, stdout, stderr = run_command(f'git add "{filename}"', cwd=repo_path)
    
    if code != 0:
        print(f"   ❌ Error adding file: {stderr}")
        return False
    
    # Step 2: Commit this file
    print(f"   💾 Committing...")
    code, stdout, stderr = run_command(
        f'git commit -m "{commit_message}"',
        cwd=repo_path
    )
    
    if code != 0:
        print(f"   ❌ Error committing: {stderr}")
        return False
    
    # Step 3: Push this commit
    print(f"   🚀 Pushing to {branch}...")
    code, stdout, stderr = run_command(
        f"git push origin {branch}",
        cwd=repo_path
    )
    
    if code != 0:
        print(f"   ❌ Error pushing: {stderr}")
        return False
    
    print(f"   ✅ Success!")
    return True


def git_auto_commit(repo_path=None, branch="main"):
    """
    Automate git operations - commit each file separately
    
    Args:
        repo_path: Path to git repository (default: current directory)
        branch: Git branch to push to (default: main)
    """
    
    # Set repository path
    if repo_path is None:
        repo_path = os.getcwd()
    
    print("=" * 70)
    print("🚀 Git Auto Commit Script (One File Per Commit)")
    print("=" * 70)
    print(f"📁 Repository: {repo_path}")
    print(f"🌿 Branch: {branch}")
    print()
    
    # Step 1: Git Status
    print("� Checking git status...")
    code, stdout, stderr = run_command("git status", cwd=repo_path, capture_output=True)
    
    if code != 0:
        print(f"❌ Error: {stderr}")
        return False
    
    # Check if there are changes
    if "nothing to commit" in stdout:
        print("✅ No changes to commit!")
        return True
    
    # Get changed files
    changed_files = get_changed_files(repo_path)
    
    if not changed_files:
        print("✅ No changed files found!")
        return True
    
    print(f"\n📝 Found {len(changed_files)} changed file(s):")
    for i, f in enumerate(changed_files, 1):
        print(f"   {i}. [{f['status']}] {f['file']}")
    print()
    
    # Process each file separately
    success_count = 0
    failed_count = 0
    failed_files = []
    
    print("=" * 70)
    print("🔄 Starting individual commits...")
    print("=" * 70)
    
    for i, file_info in enumerate(changed_files, 1):
        print(f"\n[{i}/{len(changed_files)}]", end=" ")
        
        if commit_single_file(repo_path, file_info, branch):
            success_count += 1
        else:
            failed_count += 1
            failed_files.append(file_info['file'])
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"✅ Successful commits: {success_count}")
    print(f"❌ Failed commits: {failed_count}")
    
    if failed_files:
        print("\n❌ Failed files:")
        for f in failed_files:
            print(f"   - {f}")
    
    print("=" * 70)
    
    return failed_count == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automate git operations: commit each file separately with its filename",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Commit all changed files separately (each with its filename as message)
  python git_auto_commit.py

  # Specify repository path
  python git_auto_commit.py -p /path/to/repo

  # Push to different branch
  python git_auto_commit.py -b develop

  # Combine options
  python git_auto_commit.py -p /path/to/repo -b feature/new-ui
  
Note: Each file will be committed separately with format: "Action: filename"
      Actions: Add, Update, or Delete based on git status
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        type=str,
        default=None,
        help='Path to git repository (default: current directory)'
    )
    
    parser.add_argument(
        '-b', '--branch',
        type=str,
        default='main',
        help='Git branch to push to (default: main)'
    )
    
    args = parser.parse_args()
    
    # Run git automation
    success = git_auto_commit(
        repo_path=args.path,
        branch=args.branch
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automate git add, commit, and push operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-commit with auto-generated message
  python git_auto_commit.py
  
  # Custom commit message
  python git_auto_commit.py -m "Fix: Update API mapper"
  
  # Specify repository path
  python git_auto_commit.py -p /path/to/repo
  
  # Different branch
  python git_auto_commit.py -b development
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        help='Path to git repository (default: current directory)',
        default=None
    )
    
    parser.add_argument(
        '-m', '--message',
        help='Commit message (default: auto-generated from files)',
        default=None
    )
    
    parser.add_argument(
        '-b', '--branch',
        help='Git branch to push to (default: main)',
        default='main'
    )
    
    args = parser.parse_args()
    
    # Run git operations
    success = git_auto_commit(
        repo_path=args.path,
        commit_message=args.message,
        branch=args.branch
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
