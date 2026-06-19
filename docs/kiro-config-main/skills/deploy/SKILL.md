---
name: deploy
description: Guided deployment workflow per repo. Checks branch state, runs tests, and walks through deploy steps. Use when ready to deploy to staging or production.
---

## Usage

`/deploy <repo> <environment>` — Deploy a repo to an environment

## Pre-Deploy Checks

1. Confirm branch is clean (`git status`)
2. Confirm on correct branch
3. Run tests (`/run-tests`)
4. Confirm all tests pass

## Per-Repo Deploy

Update this section to match your project's deployment targets and commands.

### Backend
- **Staging:** (deploy command)
- **Production:** (deploy command)

### Frontend
- **Staging:** (deploy command or branch push)
- **Production:** (deploy command)

### Mobile
- **Preview:** (build command)
- **Production:** (build + submit command)

### Infra
- **Any env:** Review plan before applying — NEVER apply without reviewing plan output

## Rules

- Always require explicit user confirmation before deploying
- Show what will be deployed (commits, changes)
- For production deploys, double-confirm
- After deploy, verify the deployment succeeded before closing out
