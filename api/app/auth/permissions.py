"""Enterprise RBAC permission constants and role→permission mappings.

Permissions follow the pattern: `domain:action`
Roles are mapped to sets of permissions. Route guards check permissions, not roles directly.
"""
from __future__ import annotations

from app.tenants.models import PlatformRole, TenantRole


# ─── Permission Constants ──────────────────────────────────────────────────────

# Grow domain
GROW_READ = "grow:read"
GROW_CREATE = "grow:create"
GROW_UPDATE = "grow:update"
GROW_DELETE = "grow:delete"

# Device domain
DEVICE_READ = "device:read"
DEVICE_CREATE = "device:create"
DEVICE_UPDATE = "device:update"
DEVICE_DELETE = "device:delete"
DEVICE_PROVISION = "device:provision"

# Sensor domain
SENSOR_READ = "sensor:read"
SENSOR_CREATE = "sensor:create"
SENSOR_UPDATE = "sensor:update"

# Integration domain
INTEGRATION_READ = "integration:read"
INTEGRATION_CREATE = "integration:create"
INTEGRATION_UPDATE = "integration:update"
INTEGRATION_DELETE = "integration:delete"
INTEGRATION_SYNC = "integration:sync"

# Journal/Feeding domain
JOURNAL_READ = "journal:read"
JOURNAL_CREATE = "journal:create"
JOURNAL_UPDATE = "journal:update"
JOURNAL_DELETE = "journal:delete"

# Photo domain
PHOTO_READ = "photo:read"
PHOTO_CREATE = "photo:create"
PHOTO_UPDATE = "photo:update"
PHOTO_DELETE = "photo:delete"

# Strain domain
STRAIN_READ = "strain:read"
STRAIN_CREATE = "strain:create"
STRAIN_UPDATE = "strain:update"
STRAIN_DELETE = "strain:delete"

# Outdoor domain
OUTDOOR_READ = "outdoor:read"
OUTDOOR_CREATE = "outdoor:create"
OUTDOOR_UPDATE = "outdoor:update"
OUTDOOR_DELETE = "outdoor:delete"

# Commercial/Task domain
TASK_READ = "task:read"
TASK_CREATE = "task:create"
TASK_UPDATE = "task:update"
TASK_DELETE = "task:delete"

# Tenant management
TENANT_READ = "tenant:read"
TENANT_MANAGE = "tenant:manage"
TENANT_MEMBERS_READ = "tenant:members:read"
TENANT_MEMBERS_MANAGE = "tenant:members:manage"

# Billing
BILLING_READ = "billing:read"
BILLING_MANAGE = "billing:manage"

# Platform admin
PLATFORM_READ = "platform:read"
PLATFORM_MANAGE = "platform:manage"
PLATFORM_USERS_READ = "platform:users:read"
PLATFORM_USERS_MANAGE = "platform:users:manage"


# ─── Tenant Role → Permission Mapping ─────────────────────────────────────────

_VIEWER_PERMISSIONS: frozenset[str] = frozenset({
    GROW_READ,
    DEVICE_READ,
    SENSOR_READ,
    INTEGRATION_READ,
    JOURNAL_READ,
    PHOTO_READ,
    STRAIN_READ,
    OUTDOOR_READ,
    TASK_READ,
    TENANT_READ,
    BILLING_READ,
})

_MEMBER_PERMISSIONS: frozenset[str] = _VIEWER_PERMISSIONS | frozenset({
    GROW_CREATE,
    GROW_UPDATE,
    DEVICE_CREATE,
    DEVICE_UPDATE,
    SENSOR_CREATE,
    SENSOR_UPDATE,
    INTEGRATION_CREATE,
    INTEGRATION_UPDATE,
    INTEGRATION_SYNC,
    JOURNAL_CREATE,
    JOURNAL_UPDATE,
    PHOTO_CREATE,
    PHOTO_UPDATE,
    STRAIN_CREATE,
    STRAIN_UPDATE,
    OUTDOOR_CREATE,
    OUTDOOR_UPDATE,
    TASK_CREATE,
    TASK_UPDATE,
})

_ADMIN_PERMISSIONS: frozenset[str] = _MEMBER_PERMISSIONS | frozenset({
    GROW_DELETE,
    DEVICE_DELETE,
    DEVICE_PROVISION,
    INTEGRATION_DELETE,
    JOURNAL_DELETE,
    PHOTO_DELETE,
    STRAIN_DELETE,
    OUTDOOR_DELETE,
    TASK_DELETE,
    TENANT_MANAGE,
    TENANT_MEMBERS_READ,
    TENANT_MEMBERS_MANAGE,
    BILLING_MANAGE,
})

TENANT_ROLE_PERMISSIONS: dict[TenantRole, frozenset[str]] = {
    TenantRole.viewer: _VIEWER_PERMISSIONS,
    TenantRole.member: _MEMBER_PERMISSIONS,
    TenantRole.admin: _ADMIN_PERMISSIONS,
}


# ─── Platform Role → Permission Mapping ───────────────────────────────────────

_READONLY_ADMIN_PERMISSIONS: frozenset[str] = frozenset({
    PLATFORM_READ,
    PLATFORM_USERS_READ,
}) | _VIEWER_PERMISSIONS

_SUPPORT_PERMISSIONS: frozenset[str] = _READONLY_ADMIN_PERMISSIONS | frozenset({
    PLATFORM_USERS_MANAGE,  # Can modify user accounts (reset, unlock)
    TENANT_MEMBERS_READ,
})

_SUPER_ADMIN_PERMISSIONS: frozenset[str] = _ADMIN_PERMISSIONS | frozenset({
    PLATFORM_READ,
    PLATFORM_MANAGE,
    PLATFORM_USERS_READ,
    PLATFORM_USERS_MANAGE,
})

PLATFORM_ROLE_PERMISSIONS: dict[PlatformRole, frozenset[str]] = {
    PlatformRole.user: frozenset(),  # No platform-level permissions
    PlatformRole.readonly_admin: _READONLY_ADMIN_PERMISSIONS,
    PlatformRole.support: _SUPPORT_PERMISSIONS,
    PlatformRole.super_admin: _SUPER_ADMIN_PERMISSIONS,
}


def has_permission(
    platform_role: PlatformRole,
    tenant_role: TenantRole | None,
    required: str,
) -> bool:
    """Check if the combination of platform + tenant role grants a permission."""
    # Super admin bypasses everything
    if platform_role == PlatformRole.super_admin:
        return True

    # Check platform-level permissions
    if required in PLATFORM_ROLE_PERMISSIONS[platform_role]:
        return True

    # Check tenant-level permissions (if user has a tenant context)
    if tenant_role is not None and required in TENANT_ROLE_PERMISSIONS[tenant_role]:
        return True

    return False


def get_effective_permissions(
    platform_role: PlatformRole,
    tenant_role: TenantRole | None,
) -> frozenset[str]:
    """Get the complete set of permissions for a user's role combination."""
    if platform_role == PlatformRole.super_admin:
        return _SUPER_ADMIN_PERMISSIONS

    perms = set(PLATFORM_ROLE_PERMISSIONS[platform_role])
    if tenant_role is not None:
        perms |= TENANT_ROLE_PERMISSIONS[tenant_role]
    return frozenset(perms)
