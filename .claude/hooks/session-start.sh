#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Set git identity so commits are always verified
git config --global user.email noreply@anthropic.com
git config --global user.name Claude

# Install backend dependencies
cd "$CLAUDE_PROJECT_DIR/backend"
pip install -r requirements.txt -q

# Install frontend dependencies
cd "$CLAUDE_PROJECT_DIR/frontend"
npm install
