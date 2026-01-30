"""Role-Based Access Control (RBAC) utilities."""
from typing import List, Dict
from fastapi import HTTPException, status


# Role definitions
class UserRole:
    ADMIN = "admin"
    VERIFIER = "verifier"
    PARTNER_VERIFIER = "partner_verifier"
    SPONSOR = "sponsor"
    INVESTOR = "investor"
    GOVERNMENT = "government"
    EPC = "epc"


# Permission definitions
class Permission:
    # Project permissions
    CREATE_PROJECT = "create_project"
    UPDATE_OWN_PROJECT = "update_own_project"
    UPDATE_ANY_PROJECT = "update_any_project"
    DELETE_PROJECT = "delete_project"
    VIEW_ALL_PROJECTS = "view_all_projects"

    # Verification permissions
    VERIFY_PROJECTS = "verify_projects"
    APPROVE_VERIFICATION = "approve_verification"

    # Document permissions
    UPLOAD_DOCUMENTS = "upload_documents"
    VIEW_PRIVATE_DOCUMENTS = "view_private_documents"

    # Data room permissions
    REQUEST_ACCESS = "request_access"
    GRANT_ACCESS = "grant_access"

    # Deal room permissions
    CREATE_DEALROOM = "create_dealroom"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"


# Role-to-permissions mapping
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    UserRole.ADMIN: ["*"],  # Full access

    UserRole.VERIFIER: [
        Permission.VIEW_ALL_PROJECTS,
        Permission.VERIFY_PROJECTS,
        Permission.APPROVE_VERIFICATION,
        Permission.VIEW_PRIVATE_DOCUMENTS,
        Permission.UPDATE_ANY_PROJECT,
        Permission.VIEW_AUDIT_LOGS,
    ],

    UserRole.PARTNER_VERIFIER: [
        Permission.VERIFY_PROJECTS,
        Permission.VIEW_PRIVATE_DOCUMENTS,
    ],

    UserRole.SPONSOR: [
        Permission.CREATE_PROJECT,
        Permission.UPDATE_OWN_PROJECT,
        Permission.UPLOAD_DOCUMENTS,
        Permission.GRANT_ACCESS,
    ],

    UserRole.INVESTOR: [
        Permission.REQUEST_ACCESS,
        Permission.CREATE_DEALROOM,
    ],

    UserRole.GOVERNMENT: [
        Permission.CREATE_PROJECT,
        Permission.UPDATE_OWN_PROJECT,
        Permission.UPLOAD_DOCUMENTS,
        Permission.VIEW_ALL_PROJECTS,
    ],

    UserRole.EPC: [
        Permission.REQUEST_ACCESS,
    ],
}


def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has a specific permission.

    Args:
        user_role: The user's role
        required_permission: The permission to check

    Returns:
        True if user has permission, False otherwise
    """
    if user_role == UserRole.ADMIN:
        return True

    role_perms = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in role_perms or "*" in role_perms


def require_permission(user_role: str, required_permission: str):
    """
    Raise HTTP 403 if user doesn't have permission.

    Args:
        user_role: The user's role
        required_permission: The permission to check

    Raises:
        HTTPException: If user lacks permission
    """
    if not check_permission(user_role, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission} required"
        )


def can_edit_project(
    user_id: str,
    user_role: str,
    project_creator_id: str
) -> bool:
    """
    Check if user can edit a specific project.

    Args:
        user_id: The user's ID
        user_role: The user's role
        project_creator_id: ID of the user who created the project

    Returns:
        True if user can edit the project
    """
    # Admins and verifiers can edit any project
    if user_role in [UserRole.ADMIN, UserRole.VERIFIER]:
        return True

    # Sponsors can edit their own projects
    if user_role == UserRole.SPONSOR and str(user_id) == str(project_creator_id):
        return True

    return False
