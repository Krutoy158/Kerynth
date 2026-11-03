# Privilege and authorization model

## Purpose

Kerynth is a user-first operating system. The signed-in user owns their session, personal files, and preferences. Administrative authority is requested only for operations that genuinely require system-wide changes.

The initial implementation will use a mature upstream privilege-escalation mechanism rather than inventing a custom setuid program or authorization daemon.

## User and administrator roles

- A normal account is used for all interactive work.
- Administrative privileges are obtained on demand through `sudo` or a compatible, explicitly configured authorization frontend.
- The root identity is the privileged execution identity used by the operating system. It is not the default desktop identity.
- No routine desktop session or application runs as root.
- The system must not enable passwordless unrestricted sudo by default.

## Authorization requirements

1. Privileged commands must be initiated by an explicit user action.
2. Authorization must be scoped to the requested command or operation, not granted to an unrelated application.
3. The user must be able to identify the action being authorized.
4. Authentication must fail closed if the authorization service is unavailable or its policy cannot be read.
5. A failed or cancelled authorization must not partially apply a system change.
6. Privilege must not be inherited by child processes beyond what the authorized command requires.
7. Applications must not receive a reusable root shell or unrestricted root token.
8. Graphical administration must use a maintained policy framework and must not implement its own privileged helper casually.

## File ownership and package operations

- User home directories and user configuration remain owned by the relevant user.
- Package installation may modify only paths owned by the package database and explicitly designated system locations.
- Package scripts are not executed with unrestricted root privileges. The package format should prefer declarative file installation and narrowly defined system integration actions.
- Package removal must not delete user data or user-created files that are not owned by that package.
- System configuration changes must preserve backups or provide a rollback mechanism.
- Build jobs and package compilation run as an unprivileged user in an isolated workspace.

## Audit and privacy

- Administrative actions may be recorded in local system logs for troubleshooting and accountability.
- Logs remain local and are never uploaded automatically.
- No telemetry, analytics, remote usage reporting, or diagnostic upload is permitted.
- Logs should identify the requested operation and result without recording passwords, authentication tokens, or unrelated personal data.

## Initial implementation choice

The first bootable release should integrate a maintained upstream `sudo` implementation and a standard authorization policy. Kerynth-specific graphical authorization and fine-grained policy tooling are deferred until the base system, package manager, and service model are stable.

Do not write a custom setuid-root helper as a shortcut. Any future privileged component requires a threat model, code review, adversarial tests, and a documented recovery path.

## Acceptance criteria

- A fresh installation creates a normal unprivileged user.
- The normal user can use the system without logging in as root.
- An explicitly authorized administrative command works.
- A denied or cancelled command makes no system changes.
- Desktop applications do not run as root.
- Package builds run without root privileges.
- Administrative logs remain local.
- No telemetry or diagnostic upload component exists.
