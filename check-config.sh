#!/bin/bash
# Repository Protection - Direct Enforcement

REPO_URL="https://github.com/abdopcnet/posawesome15_lite.git"

# Set Git identity
git config user.name "abdopcnet" >/dev/null 2>&1
git config user.email "abdopcnet@gmail.com" >/dev/null 2>&1

# Force main branch
git branch -M main >/dev/null 2>&1

# Set remotes with push configuration
git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL" >/dev/null 2>&1
git remote set-url upstream "$REPO_URL" 2>/dev/null || git remote add upstream "$REPO_URL" >/dev/null 2>&1
git config branch.main.remote origin >/dev/null 2>&1
git config branch.main.merge refs/heads/main >/dev/null 2>&1

echo "✅ Locked: abdopcnet | main | posawesome15_lite"
