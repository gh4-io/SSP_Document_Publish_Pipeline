<objective>
Create a detailed, step-by-step implementation plan for the SSP document automation pipeline based on research findings.

This plan will guide the implementation stage and produce a robust, flexible system that handles:
- Full pipeline automation (Markdown → Pandoc → DocBook/HTML → Scribus/Web → PDF/HTML)
- Web output generation with responsive design
- Metadata validation (YAML schema enforcement)
- Asset pipeline (image optimization, print/web variants)
- Batch processing (multi-document operations)
- Image positioning and manipulation
- Flexible CSS, HTML, fonts, type rendering, emojis, unicode, layouts

The plan must be detailed enough for implementation without further architectural decisions.
</objective>

<context>
**Input from Research Stage**:
Read the research document: @research/ssp-automation-requirements.md

This document contains:
- Technology recommendations for each feature gap
- Current codebase analysis and integration points
- Architecture patterns and design decisions
- Trade-offs and rationale

**Project Context**:
Read @CLAUDE.md for project standards and workflow details.

**Current System**:
- Scripts: @scripts/scribus_pipeline_adv_v3.py, @scripts/release_packager.py
- Layout config: @scripts/layout_map.yaml
- Asset structure: @assets/ (images, xml, fonts, diagrams, web)
</context>

<planning_requirements>
Create a comprehensive, hierarchical plan that:

1. **Breaks down work into phases** (4-6 major phases)
2. **Defines clear deliverables** for each phase
3. **Sequences work logically** (foundational → incremental → integration)
4. **Identifies dependencies** between tasks
5. **Specifies file modifications** (which files to create/edit/delete)
6. **Includes verification steps** for each phase
7. **Plans for backwards compatibility** with existing workflow
8. **Addresses migration path** from current to new system

The plan should be optimized for solo agentic development (Claude executing the plan).
</planning_requirements>

<planning_structure>
Create the plan document: `./plans/ssp-automation-implementation-plan.md`

**Required Sections**:

## 1. Architecture Overview
Brief summary of the overall architecture based on research recommendations:
- High-level component diagram (text-based)
- Technology stack
- Data flow: Markdown → outputs (PDF, HTML, web)
- Integration approach with existing system

## 2. Phase Breakdown
For each phase (4-6 phases recommended):

### Phase N: [Phase Name]
**Objective**: [What this phase accomplishes]

**Dependencies**: [Previous phases or external requirements]

**Tasks**:
1. [Task name]
   - **Files to modify**: `./path/to/file.py`, `./path/to/config.yaml`
   - **Changes**: [Specific code/config changes]
   - **Rationale**: [Why this approach]
   - **Verification**: [How to test this task]

2. [Next task...]
   [Continue for all tasks in phase]

**Phase Deliverables**:
- [Concrete output 1]
- [Concrete output 2]

**Verification Criteria**:
- [How to verify phase completion]
- [Example test case or command]

---

## 3. Suggested Phase Structure
Based on the research findings, structure phases like:

**Phase 1: Foundation & Configuration**
- Metadata validation system
- Configuration management (YAML schemas, validation rules)
- Directory structure for new features
- Logging and error handling infrastructure

**Phase 2: Asset Pipeline**
- Image optimization workflow
- Print/web variant generation
- Asset registry and version tracking
- Integration with existing `/assets` structure

**Phase 3: Web Output Generation**
- Pandoc HTML5 conversion pipeline
- CSS framework integration
- Font loading and web font handling
- Unicode and emoji rendering
- Responsive image handling

**Phase 4: Batch Processing**
- Multi-document conversion orchestration
- Dependency tracking
- Parallel processing
- Incremental builds
- Build script and CLI

**Phase 5: Image Positioning & Manipulation**
- Directive parsing and expansion
- CSS positioning for web
- Scribus frame manipulation for PDF
- Caption and border handling

**Phase 6: Integration & Polish**
- Unified CLI interface
- End-to-end testing
- Documentation and examples
- Migration guide from old → new workflow

(Adjust phases based on research recommendations)

## 4. File Modification Plan
Comprehensive list of files to create/modify/delete:

**New Files**:
- `./scripts/metadata_validator.py` - YAML schema validation
- `./scripts/asset_optimizer.py` - Image optimization pipeline
- `./scripts/web_generator.py` - HTML output generation
- `./scripts/batch_processor.py` - Multi-document orchestration
- `./config/schema.yaml` - Metadata validation schema
- `./config/pipeline.yaml` - Pipeline configuration
- [Additional files based on research]

**Modified Files**:
- `./scripts/scribus_pipeline_adv_v3.py` - Integration hooks for validation, assets
- `./scripts/release_packager.py` - Include web outputs in releases
- `./scripts/layout_map.yaml` - Extended for new features
- [Additional files based on research]

**Deleted Files**:
- [Any deprecated scripts or configs]

## 5. Backwards Compatibility Strategy
How to maintain existing workflow while adding new features:
- Feature flags or configuration switches
- Graceful degradation for missing dependencies
- Migration path for existing documents
- Testing strategy for existing documents

## 6. Testing & Verification Plan
How to verify each phase and the complete system:
- Unit tests for new modules
- Integration tests for pipeline
- End-to-end tests with sample documents
- Performance benchmarks (batch processing, image optimization)
- Visual regression tests (PDF/HTML output comparison)

## 7. Open Questions for Implementation
Any decisions deferred to implementation stage:
- [Question 1]
- [Question 2]

## 8. Success Criteria
The complete implementation must:
- [Criterion 1: e.g., "Generate pixel-perfect PDF and responsive HTML from same Markdown source"]
- [Criterion 2: e.g., "Validate all metadata against schema with clear error messages"]
- [Criterion 3: e.g., "Process 100 documents in under 5 minutes"]
- [Additional criteria based on research recommendations]
</planning_structure>

<planning_approach>
1. **Read the research document thoroughly** - understand all recommendations and rationale
2. **Identify foundational components** - what must be built first (validation, config, error handling)
3. **Sequence phases logically** - each phase builds on previous phases
4. **Be specific about file changes** - include actual file paths and high-level change descriptions
5. **Include verification steps** - how to test each phase before moving to next
6. **Consider integration points** - how new features connect to existing scripts
7. **Plan for flexibility** - configuration-driven where possible, plugin architecture for extensibility
8. **Think maintenance** - clear module boundaries, well-documented interfaces

Use extended thinking for complex architectural decisions:
- How to structure the asset pipeline for maximum flexibility?
- What's the optimal way to share metadata between PDF and web outputs?
- How to handle font loading across Scribus and web contexts?
- What configuration format provides best balance of power and simplicity?
</planning_approach>

<success_criteria>
The implementation plan must:
- Be detailed enough for immediate execution (no further design work needed)
- Sequence work logically with clear dependencies
- Specify concrete file modifications with rationale
- Include verification steps for each phase
- Address backwards compatibility explicitly
- Be optimized for solo agentic development (Claude as executor)
- Incorporate all research recommendations
- Define clear success criteria for the complete system
- Be comprehensive yet flexible (allow for discovery during implementation)
</success_criteria>

<output_handoff>
This plan will feed into the IMPLEMENTATION stage, which will execute it step-by-step:
- Create/modify files as specified
- Follow verification steps
- Report progress phase-by-phase
- Adapt as needed based on implementation discoveries

Ensure the plan is:
- Specific enough to guide implementation
- Flexible enough to allow adaptation
- Complete enough to avoid mid-implementation research
</output_handoff>
