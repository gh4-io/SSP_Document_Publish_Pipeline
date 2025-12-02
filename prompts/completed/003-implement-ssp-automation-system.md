<objective>
Execute the detailed implementation plan to build the complete SSP document automation system.

Implement all features phase-by-phase:
- Metadata validation (YAML schema enforcement)
- Asset pipeline (image optimization, print/web variants)
- Web output generation (HTML, responsive design, CSS, fonts, unicode)
- Batch processing (multi-document operations, parallel builds)
- Image positioning and manipulation
- Flexible, extensible architecture (plugins, configuration, templates)

Follow the plan exactly, verify each phase before proceeding, and deliver production-ready code.
</objective>

<context>
**Input from Planning Stage**:
Read the implementation plan: @plans/ssp-automation-implementation-plan.md

This document contains:
- Architecture overview
- Phased implementation breakdown (4-6 phases)
- Specific file modifications for each task
- Verification steps for each phase
- Backwards compatibility strategy
- Testing and success criteria

**Supporting Research**:
Available for reference: @research/ssp-automation-requirements.md
- Technology recommendations and rationale
- Trade-offs and alternatives
- Current codebase analysis

**Project Context**:
Read @CLAUDE.md for coding standards and workflow details.
</context>

<implementation_requirements>
Execute the plan with these principles:

1. **Follow the plan sequentially** - complete phases in order
2. **Verify before proceeding** - run verification steps after each phase
3. **Preserve working state** - keep existing workflow functional
4. **Write production code** - not prototypes; include error handling, logging, documentation
5. **Match existing style** - follow patterns in current codebase
6. **Be explicit about changes** - explain what you're doing and why
7. **Test incrementally** - verify each component before integration
8. **Document as you go** - inline comments for complex logic, docstrings for functions

**Code Quality Standards**:
- Type hints for all function signatures (Python 3.12)
- Comprehensive error handling with clear error messages
- Logging at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Docstrings for all modules, classes, and functions
- Configuration-driven where possible (avoid hardcoded paths/values)
- Modular design (single responsibility, clean interfaces)
- No TODO comments - complete features fully or defer to next phase
</implementation_requirements>

<execution_workflow>
For each phase in the implementation plan:

## Phase Execution Template

### 1. Read Phase Details
- Review phase objective, tasks, and deliverables
- Understand dependencies and verification criteria
- Identify all files to create/modify

### 2. Implement Tasks Sequentially
For each task in the phase:

**Before writing code**:
- Read existing files that will be modified
- Understand current patterns and integration points
- Plan minimal, surgical changes

**While writing code**:
- Follow the plan's specific instructions
- Match existing code style and patterns
- Add comprehensive error handling
- Include logging statements
- Write clear docstrings and comments

**After writing code**:
- Review changes for correctness
- Check for style consistency
- Verify error handling covers edge cases

### 3. Verify Phase Completion
Run the verification steps specified in the plan:
- Execute test commands
- Validate outputs
- Check for errors or warnings
- Confirm phase deliverables

### 4. Report Progress
After each phase:
- Summarize what was implemented
- List files created/modified
- Report verification results
- Note any deviations from plan (with rationale)
- Ask if ready to proceed to next phase

### 5. Proceed to Next Phase
Only after verification succeeds and user confirms.
</execution_workflow>

<parallel_tool_usage>
For maximum efficiency during implementation:

When you need to perform multiple independent operations (reading multiple files, checking multiple paths, running multiple verification commands), invoke all relevant tools simultaneously in a single response rather than sequentially.

Example:
- Reading multiple existing files before modification → parallel Read calls
- Checking multiple configuration files → parallel Read calls
- Running multiple independent test commands → parallel Bash calls

Only use sequential tool calls when operations have dependencies.
</parallel_tool_usage>

<handling_deviations>
If you discover issues during implementation:

**Minor adjustments** (better variable names, improved error messages, etc.):
- Make the improvement
- Note it in your progress report
- Continue with phase

**Significant deviations** (different approach needed, missing dependency, architectural issue):
- Stop current task
- Explain the issue clearly
- Propose alternative approach with rationale
- Wait for user confirmation before proceeding

**Blockers** (missing information, unclear requirements, conflicting constraints):
- Stop and ask clarifying questions
- Reference specific part of plan that's unclear
- Propose options if possible
- Wait for user guidance
</handling_deviations>

<verification_strategy>
After implementing each phase, verify thoroughly:

**Code-level verification**:
- No syntax errors (run Python files with `python3 -m py_compile`)
- No import errors (check all imports resolve)
- Type hints are valid (use mypy if available)

**Functional verification**:
- Run the verification commands specified in the plan
- Test with sample documents from `/drafts` or `/_boilerplate`
- Check outputs in `/published`, `/assets`, etc.
- Verify logs show expected information

**Integration verification**:
- Ensure new code integrates with existing scripts
- Backwards compatibility maintained (old workflow still works)
- Configuration files are valid (YAML syntax, schema)

**Performance verification** (for batch processing, asset optimization):
- Benchmark key operations
- Verify parallel processing works
- Check memory usage is reasonable

Report verification results clearly:
✓ Passed: [what worked]
✗ Failed: [what didn't work, error message]
⚠ Warning: [non-critical issues]
</verification_strategy>

<success_criteria>
The complete implementation must achieve:

1. **Feature Completeness**:
   - ✓ Metadata validation enforces YAML schema
   - ✓ Asset pipeline generates print/web variants
   - ✓ Web output produces responsive HTML
   - ✓ Batch processing handles multiple documents
   - ✓ Image directives expand correctly (position, scale, borders, captions)
   - ✓ Flexible CSS, fonts, unicode, emoji rendering

2. **Code Quality**:
   - ✓ Production-ready (error handling, logging, documentation)
   - ✓ Follows existing code style and patterns
   - ✓ Type hints for all functions
   - ✓ Comprehensive docstrings
   - ✓ Configuration-driven (no hardcoded values)

3. **Backwards Compatibility**:
   - ✓ Existing workflow still functions
   - ✓ Existing documents process without modification
   - ✓ Graceful degradation for missing dependencies

4. **Testing**:
   - ✓ All verification steps pass
   - ✓ Sample documents process successfully
   - ✓ Outputs match quality standards (PDF, HTML)

5. **Documentation**:
   - ✓ Inline comments for complex logic
   - ✓ Docstrings for all modules/classes/functions
   - ✓ Updated README or usage docs (if needed)

6. **Extensibility**:
   - ✓ Plugin architecture for custom processors
   - ✓ Configuration allows easy customization
   - ✓ Modular design supports future additions
</success_criteria>

<output_deliverables>
By the end of implementation, you will have created/modified:

**New Python Modules** (based on plan):
- Metadata validation system
- Asset optimization pipeline
- Web output generator
- Batch processing orchestrator
- Image directive parser/expander
- Unified CLI interface
- [Additional modules per plan]

**Modified Existing Scripts**:
- Integration hooks in existing pipeline scripts
- Updated configuration files
- Extended layout maps
- [Additional modifications per plan]

**Configuration Files**:
- YAML schemas for validation
- Pipeline configuration
- Asset optimization settings
- Web output templates
- [Additional configs per plan]

**Documentation**:
- Inline code comments
- Function/module docstrings
- Usage examples (if creating new CLI)
- Migration guide (if needed)

**Verification Outputs**:
- Test results for each phase
- Sample outputs (PDF, HTML)
- Performance benchmarks (if applicable)
</output_deliverables>

<reflection_and_adaptation>
After receiving tool results during implementation, carefully reflect:

**After reading files**:
- Do I understand the current implementation?
- What patterns should I follow?
- What's the cleanest integration approach?

**After writing code**:
- Does this follow existing patterns?
- Is error handling comprehensive?
- Are there edge cases I haven't covered?

**After running verification**:
- Did it pass? If not, what failed and why?
- Are there warnings I should address?
- Is performance acceptable?

**Before proceeding to next phase**:
- Is the current phase truly complete?
- Have I verified all deliverables?
- Are there loose ends to address?

Use extended thinking for complex implementation decisions:
- How to structure the plugin architecture for maximum flexibility?
- What's the cleanest way to share metadata between PDF and web generators?
- How to handle font loading across different output contexts?
- What's the optimal error handling strategy for batch processing?
</reflection_and_adaptation>

<final_deliverable>
When all phases are complete:

1. **Summary Report**:
   - List all files created/modified
   - Summarize each phase's deliverables
   - Report all verification results
   - Note any deviations from plan (with rationale)
   - Document known limitations or future enhancements

2. **Verification Evidence**:
   - Show successful test runs
   - Provide sample outputs (PDF, HTML)
   - Share performance benchmarks
   - Demonstrate backwards compatibility

3. **Next Steps**:
   - Recommend any follow-up work
   - Suggest additional testing or documentation
   - Identify opportunities for future enhancement
</final_deliverable>
