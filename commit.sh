#!/bin/bash

# Simple Git Protection
USER="abdopcnet"
EMAIL="abdopcnet@gmail.com"
REPO="https://github.com/abdopcnet/posawesome15_lite.git"

# Check user
if [ "$(git config user.name)" != "$USER" ]; then
    echo "❌ Wrong user"
    exit 1
fi

# Setup git
git config user.name "$USER"
git config user.email "$EMAIL"
git branch -M main
git remote set-url origin "$REPO"

# Update version
sed -i "s/__version__ = \".*\"/__version__ = \"$(date +%-d.%-m.%Y)\"/" posawesome/__init__.py
git add posawesome/__init__.py

# Commit
git commit "$@"
