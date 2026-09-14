# VPN Access After Password Reset

When a user changes their corporate password, the VPN client may continue using an outdated cached credential.

Recommended troubleshooting steps:
- confirm the password works in the normal company login portal
- sign out of the VPN client and sign back in
- clear any saved VPN credentials if the client supports it
- if MFA is enabled, re-register the session after the password change
- if the issue persists, capture the exact error message and device OS before escalation

Escalate to access management only after the above steps fail or if multiple users are affected.
