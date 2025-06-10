# Implementation Plan for Refactoring MCP Tools

This document outlines the plan for refactoring the Semaphore MCP tools to improve organization and solve context window overflow issues.

## 1. Create New Directory Structure

- [ ] Create `src/semaphore_mcp/tools/` directory
- [ ] Create `src/semaphore_mcp/tools/__init__.py`
- [ ] Create `tests/tools/` directory
- [ ] Create `tests/tools/__init__.py`

## 2. Extract Tool Logic by Functionality

### File Structure:

```
src/semaphore_mcp/tools/
├── __init__.py
├── base.py
├── projects.py
├── templates.py
├── tasks.py
└── environments.py
```

### Implementation Tasks:

1. **Create Base Tool Class**
   - [ ] Create `base.py` with common functionality
   - [ ] Implement semaphore client initialization

2. **Extract Project Tools**
   - [ ] Create `projects.py`
   - [ ] Move `list_projects()` and `get_project()`
   - [ ] Add necessary imports

3. **Extract Template Tools**
   - [ ] Create `templates.py`
   - [ ] Move `list_templates()` and `get_template()`
   - [ ] Add necessary imports

4. **Extract Task Tools**
   - [ ] Create `tasks.py`
   - [ ] Move `list_tasks()`, `get_task()`, `run_task()`, `get_task_output()`, `get_latest_failed_task()`
   - [ ] Add necessary imports

5. **Extract Environment Tools**
   - [ ] Create `environments.py`
   - [ ] Move the environment and inventory-related tools
   - [ ] Add necessary imports

6. **Update `tools/__init__.py`**
   - [ ] Import all tool classes
   - [ ] Set up `__all__` for clean imports

## 3. Refactor Server Class

- [ ] Update `server.py` to import tool classes
- [ ] Initialize tool instances in the `__init__` method
- [ ] Update `register_tools()` to use tool instances
- [ ] Clean up old tool methods

## 4. Split Test Files

- [ ] Create matching test structure in `tests/tools/`
- [ ] Move tests for each tool group to corresponding test file
- [ ] Update imports in test files
- [ ] Ensure test mocks are properly set up

## 5. Execution Phases

1. **Phase 1**: Create all directories and files
2. **Phase 2**: Implement base tool class
3. **Phase 3**: Extract tool methods to new files one functional group at a time
4. **Phase 4**: Update server to use the new structure
5. **Phase 5**: Split and update tests
6. **Phase 6**: Clean up and documentation

## 6. Notes on Implementation

- Keep all code async-compatible
- Maintain error handling patterns
- Ensure consistent logging
- Update docstrings to reflect any changes in behavior
- Verify each step with tests before moving to the next
