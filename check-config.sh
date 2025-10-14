#!/bin/bash
# Repository Protection - Direct Enforcement

set -e

# Set Git identity
git config user.name "abdopcnet"
git config user.email "abdopcnet@gmail.com"

# Force main branch
git branch -M main

# Set remotes (force update if exists)
git remote remove origin 2>/dev/null || true
git remote remove upstream 2>/dev/null || true
git remote add origin https://github.com/abdopcnet/posawesome15_lite.git
git remote add upstream https://github.com/abdopcnet/posawesome15_lite.git

echo "✅ Repository locked: abdopcnet | main branch | posawesome15_lite"
