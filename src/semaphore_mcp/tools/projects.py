"""
Project-related tools for Semaphore MCP.

This module provides tools for interacting with Semaphore projects.
These tools support full CRUD operations for projects.
"""

import logging
from copy import deepcopy
from typing import Any, Optional

from .base import BaseTool

logger = logging.getLogger(__name__)

BACKUP_SECTIONS: tuple[str, ...] = (
    "templates",
    "repositories",
    "keys",
    "views",
    "inventories",
    "environments",
    "integrations",
    "integration_aliases",
    "schedules",
    "secret_storages",
    "roles",
    "runners",
)

BACKUP_NAME_FIELDS: dict[str, tuple[str, ...]] = {
    "templates": ("name",),
    "repositories": ("name",),
    "keys": ("name",),
    "views": ("title", "name"),
    "inventories": ("name",),
    "environments": ("name",),
    "integrations": ("name",),
    "integration_aliases": ("alias", "name"),
    "schedules": ("name",),
    "secret_storages": ("name",),
    "roles": ("name",),
    "runners": ("name",),
}


def _backup_section_items(backup: dict[str, Any], section: str) -> list[Any]:
    items = backup.get(section, [])
    return items if isinstance(items, list) else []


def _backup_item_name(item: Any, fields: tuple[str, ...]) -> Optional[str]:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return None
    for field in fields:
        value = item.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def _backup_section_names(backup: dict[str, Any], section: str) -> list[str]:
    fields = BACKUP_NAME_FIELDS[section]
    names: list[str] = []
    for item in _backup_section_items(backup, section):
        name = _backup_item_name(item, fields)
        if name is not None:
            names.append(name)
    return names


def _backup_summary(backup: dict[str, Any]) -> dict[str, Any]:
    meta = backup.get("meta", {})
    project_name = meta.get("name") if isinstance(meta, dict) else None
    sections = {
        section: len(_backup_section_items(backup, section))
        for section in BACKUP_SECTIONS
    }
    names = {
        section: _backup_section_names(backup, section)
        for section in BACKUP_SECTIONS
        if section != "integration_aliases"
    }
    key_types = [
        item.get("type")
        for item in _backup_section_items(backup, "keys")
        if isinstance(item, dict)
    ]

    return {
        "project_name": project_name,
        "sections": sections,
        "names": names,
        "total_resources": sum(sections.values()),
        "contains_secret_references": any(
            key_type in {"ssh", "login_password"} for key_type in key_types
        )
        or sections["secret_storages"] > 0,
    }


def _validate_backup_references(backup: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    names = {
        section: set(_backup_section_names(backup, section))
        for section in BACKUP_SECTIONS
    }

    for index, repository in enumerate(_backup_section_items(backup, "repositories")):
        if not isinstance(repository, dict):
            continue
        ssh_key = repository.get("ssh_key")
        if isinstance(ssh_key, str) and ssh_key and ssh_key not in names["keys"]:
            errors.append(
                f"repositories[{index}].ssh_key references missing key '{ssh_key}'"
            )

    for index, inventory in enumerate(_backup_section_items(backup, "inventories")):
        if not isinstance(inventory, dict):
            continue
        for field in ("ssh_key", "become_key"):
            key_name = inventory.get(field)
            if isinstance(key_name, str) and key_name and key_name not in names["keys"]:
                errors.append(
                    f"inventories[{index}].{field} references missing key '{key_name}'"
                )

    for index, template in enumerate(_backup_section_items(backup, "templates")):
        if not isinstance(template, dict):
            continue
        repository = template.get("repository")
        if not isinstance(repository, str) or not repository:
            errors.append(f"templates[{index}].repository is required")
        elif repository not in names["repositories"]:
            errors.append(
                f"templates[{index}].repository references missing repository "
                f"'{repository}'"
            )

        inventory = template.get("inventory")
        if (
            isinstance(inventory, str)
            and inventory
            and inventory not in names["inventories"]
        ):
            errors.append(
                f"templates[{index}].inventory references missing inventory "
                f"'{inventory}'"
            )

        view = template.get("view")
        if isinstance(view, str) and view and view not in names["views"]:
            errors.append(f"templates[{index}].view references missing view '{view}'")

        build_template = template.get("build_template")
        if (
            isinstance(build_template, str)
            and build_template
            and build_template not in names["templates"]
        ):
            errors.append(
                f"templates[{index}].build_template references missing template "
                f"'{build_template}'"
            )

        vault_key = template.get("vault_key")
        if isinstance(vault_key, str) and vault_key and vault_key not in names["keys"]:
            errors.append(
                f"templates[{index}].vault_key references missing key '{vault_key}'"
            )

        environments = template.get("environments", [])
        if environments is not None and not isinstance(environments, list):
            errors.append(f"templates[{index}].environments must be a list")
        elif isinstance(environments, list):
            for env_name in environments:
                if isinstance(env_name, str) and env_name not in names["environments"]:
                    errors.append(
                        f"templates[{index}].environments references missing "
                        f"environment '{env_name}'"
                    )

        vaults = template.get("vaults", [])
        if vaults is not None and not isinstance(vaults, list):
            errors.append(f"templates[{index}].vaults must be a list")
        elif isinstance(vaults, list):
            for vault_index, vault in enumerate(vaults):
                if not isinstance(vault, dict):
                    errors.append(
                        f"templates[{index}].vaults[{vault_index}] must be an object"
                    )
                    continue
                vault_name = vault.get("vault_key")
                if (
                    isinstance(vault_name, str)
                    and vault_name
                    and vault_name not in names["keys"]
                ):
                    errors.append(
                        f"templates[{index}].vaults[{vault_index}].vault_key "
                        f"references missing key '{vault_name}'"
                    )

    for index, schedule in enumerate(_backup_section_items(backup, "schedules")):
        if not isinstance(schedule, dict):
            continue
        template = schedule.get("template")
        if (
            isinstance(template, str)
            and template
            and template not in names["templates"]
        ):
            errors.append(
                f"schedules[{index}].template references missing template '{template}'"
            )
        repository = schedule.get("checkable_repository")
        if (
            isinstance(repository, str)
            and repository
            and repository not in names["repositories"]
        ):
            errors.append(
                f"schedules[{index}].checkable_repository references missing "
                f"repository '{repository}'"
            )

    for index, integration in enumerate(_backup_section_items(backup, "integrations")):
        if not isinstance(integration, dict):
            continue
        template = integration.get("template")
        if (
            isinstance(template, str)
            and template
            and template not in names["templates"]
        ):
            errors.append(
                f"integrations[{index}].template references missing template "
                f"'{template}'"
            )
        auth_secret = integration.get("auth_secret")
        if (
            isinstance(auth_secret, str)
            and auth_secret
            and auth_secret not in names["keys"]
        ):
            errors.append(
                f"integrations[{index}].auth_secret references missing key "
                f"'{auth_secret}'"
            )

    return errors


def _validate_project_backup(backup: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(backup, dict):
        return {
            "valid": False,
            "errors": ["backup must be an object"],
            "warnings": [],
            "summary": {},
        }

    meta = backup.get("meta")
    if not isinstance(meta, dict):
        errors.append("meta must be an object")
    else:
        name = meta.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append("meta.name is required")

    for section in BACKUP_SECTIONS:
        if section not in backup:
            warnings.append(f"{section} section is missing; treating it as empty")
            continue
        items = backup[section]
        if not isinstance(items, list):
            errors.append(f"{section} must be a list")
            continue
        for index, item in enumerate(items):
            if section == "integration_aliases":
                if not isinstance(item, str):
                    errors.append(f"{section}[{index}] must be a string")
            elif not isinstance(item, dict):
                errors.append(f"{section}[{index}] must be an object")

        seen: set[str] = set()
        for name in _backup_section_names(backup, section):
            if name in seen:
                warnings.append(f"{section} contains duplicate name '{name}'")
            seen.add(name)

    errors.extend(_validate_backup_references(backup))

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": _backup_summary(backup),
    }


def _validated_backup_or_raise(backup: Any) -> dict[str, Any]:
    validation = _validate_project_backup(backup)
    if not validation["valid"]:
        raise ValueError(
            "Invalid Semaphore project backup: " + "; ".join(validation["errors"])
        )
    return backup


class ProjectTools(BaseTool):
    """Tools for working with Semaphore projects.

    Provides full CRUD operations for projects in SemaphoreUI.
    All operations have been tested and verified to work with SemaphoreUI API.
    """

    async def list_projects(self) -> dict[str, Any]:
        """List all projects in SemaphoreUI.

        Returns:
            A dictionary containing the list of projects.
        """
        try:
            projects = self.semaphore.list_projects()
            return {"projects": projects}
        except Exception as e:
            self.handle_error(e, "listing projects")

    async def get_project(self, project_id: int) -> dict[str, Any]:
        """Get details of a specific project.

        Args:
            project_id: ID of the project to fetch

        Returns:
            Project details
        """
        try:
            return self.semaphore.get_project(project_id)
        except Exception as e:
            self.handle_error(e, f"getting project {project_id}")

    async def create_project(
        self,
        name: str,
        alert: bool = False,
        alert_chat: Optional[str] = None,
        max_parallel_tasks: int = 0,
        project_type: Optional[str] = None,
        demo: bool = False,
    ) -> dict[str, Any]:
        """Create a new project.

        Args:
            name: Project name
            alert: Enable alerts (default: False)
            alert_chat: Chat channel for alerts (optional)
            max_parallel_tasks: Maximum parallel tasks, 0 = unlimited (default: 0)
            project_type: Project type (optional)
            demo: Create demo resources (default: False)

        Returns:
            Created project details
        """
        try:
            return self.semaphore.create_project(
                name=name,
                alert=alert,
                alert_chat=alert_chat,
                max_parallel_tasks=max_parallel_tasks,
                project_type=project_type,
                demo=demo,
            )
        except Exception as e:
            self.handle_error(e, f"creating project '{name}'")

    async def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        alert: Optional[bool] = None,
        alert_chat: Optional[str] = None,
        max_parallel_tasks: Optional[int] = None,
        project_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing project.

        Args:
            project_id: ID of the project to update
            name: Project name (optional)
            alert: Enable alerts (optional)
            alert_chat: Chat channel for alerts (optional)
            max_parallel_tasks: Maximum parallel tasks (optional)
            project_type: Project type (optional)

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.update_project(
                project_id=project_id,
                name=name,
                alert=alert,
                alert_chat=alert_chat,
                max_parallel_tasks=max_parallel_tasks,
                project_type=project_type,
            )
        except Exception as e:
            self.handle_error(e, f"updating project {project_id}")

    async def delete_project(self, project_id: int) -> dict[str, Any]:
        """Delete a project.

        Args:
            project_id: ID of the project to delete

        Returns:
            Empty dict on success
        """
        try:
            return self.semaphore.delete_project(project_id)
        except Exception as e:
            self.handle_error(e, f"deleting project {project_id}")

    async def backup_project(self, project_id: int) -> dict[str, Any]:
        """Export a Semaphore project backup.

        Args:
            project_id: ID of the project to back up

        Returns:
            Backup payload and a resource summary.
        """
        try:
            backup = self.semaphore.backup_project(project_id)
            validation = _validate_project_backup(backup)
            return {
                "project_id": project_id,
                "backup": backup,
                "summary": validation["summary"],
                "warnings": validation["warnings"],
            }
        except Exception as e:
            self.handle_error(e, f"backing up project {project_id}")

    async def restore_project_backup(
        self,
        backup: dict[str, Any],
        project_name: Optional[str] = None,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Restore a Semaphore project from a backup payload.

        Args:
            backup: Backup payload returned by backup_project
            project_name: Optional name override for the restored project
            validate: Validate payload shape and references before restore

        Returns:
            Created project and summary of the restored backup payload.
        """
        try:
            payload = deepcopy(backup)
            if project_name is not None:
                payload.setdefault("meta", {})["name"] = project_name
            if validate:
                _validated_backup_or_raise(payload)

            project = self.semaphore.restore_project_backup(payload)
            return {
                "project": project,
                "summary": _backup_summary(payload),
            }
        except Exception as e:
            self.handle_error(e, "restoring project backup")

    async def validate_project_backup(self, backup: dict[str, Any]) -> dict[str, Any]:
        """Validate a project backup before attempting restore.

        Args:
            backup: Backup payload to inspect

        Returns:
            Validation result, errors, warnings, and a summary.
        """
        try:
            return _validate_project_backup(backup)
        except Exception as e:
            self.handle_error(e, "validating project backup")

    async def summarize_project_backup(self, backup: dict[str, Any]) -> dict[str, Any]:
        """Summarize the resources contained in a project backup.

        Args:
            backup: Backup payload to summarize

        Returns:
            Counts, names, and secret-reference indicators for the backup.
        """
        try:
            _validated_backup_or_raise(backup)
            return _backup_summary(backup)
        except Exception as e:
            self.handle_error(e, "summarizing project backup")

    async def clone_project(
        self,
        project_id: int,
        name: str,
        validate: bool = True,
    ) -> dict[str, Any]:
        """Clone a project by backing it up and restoring it with a new name.

        Args:
            project_id: ID of the source project
            name: Name for the cloned project
            validate: Validate backup payload before restore

        Returns:
            Source project ID, created clone, and backup summary.
        """
        try:
            backup = self.semaphore.backup_project(project_id)
            payload = deepcopy(backup)
            payload.setdefault("meta", {})["name"] = name
            if validate:
                _validated_backup_or_raise(payload)

            project = self.semaphore.restore_project_backup(payload)
            return {
                "source_project_id": project_id,
                "project": project,
                "summary": _backup_summary(payload),
            }
        except Exception as e:
            self.handle_error(e, f"cloning project {project_id}")
