# Documentation Standards

## Project Documentation Location
- **Path**: `~/.kiro/docs/`
- **Purpose**: Store project documentation that doesn't need to be in context automatically
- **Access**: Viewable by user, referenceable when needed

## When to Create Documentation
- **Major migrations** (API changes, infrastructure updates)
- **Complex implementations** (multi-service changes)
- **Decision records** (architecture choices, trade-offs)
- **Deployment guides** (step-by-step procedures)

## Documentation Format
- **Markdown files** with descriptive names
- **Consolidate** multiple related docs into single comprehensive file
- **Include**: Executive summary, technical details, decisions made, rollback plans
- **Avoid**: Cluttering repo root directories with temporary docs

## File Naming Convention
- `project-name-type.md` (e.g., `feature-migration.md`)
- Use hyphens, lowercase
- Include project and document type for clarity

## Content Structure
1. **Executive Summary** - High-level overview
2. **Implementation Details** - Technical specifics
3. **Architecture Decisions** - Why choices were made
4. **Deployment/Testing** - Practical steps
5. **Rollback Plans** - Safety measures
6. **Key Learnings** - For future reference