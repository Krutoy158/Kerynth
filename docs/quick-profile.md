# Quick Profile Setup

## Goal

The installer provides a **Quick Profile Setup** path for people installing Linux for the first time. It creates the first local user account without requiring terminal commands, knowledge of Unix usernames, or a separate root password.

The quick path must remain short. Advanced account and group management belongs in a separate optional section and must not block a normal installation.

## Screen

The screen title is **Create Your Profile**.

Required fields:

1. **Your name** — a display name shown on the login screen and in the desktop session.
2. **Username** — suggested automatically from the name, but editable before continuing.
3. **Password** — a local password for this account.
4. **Confirm password** — entered separately to catch typing mistakes.

The username suggestion is a convenience only. It must not silently replace a value the user has edited. The installer shows a clear inline error when a field is invalid and keeps valid input when the user goes back to a previous step.

The password field has a local show/hide control. A local strength hint may explain whether the password is easy to guess. Password checks must not use a network service.

## Beginner-friendly behavior

- Do not ask the user to choose between root, administrator, and standard-user account types in the quick path.
- The first created account is the normal personal account. Administrative tasks use explicit sudo authorization and must explain the requested change.
- Do not ask the user to create or remember a separate root password during the quick path.
- Do not require an email address, phone number, cloud account, online sign-in, or security questions.
- Do not require knowledge of groups, shells, home-directory paths, UID/GID values, or filesystem permissions.
- Offer **Advanced account settings** separately; keep it optional.
- Use plain language, keyboard navigation, scalable text, visible focus, and accessible field labels.
- Explain that the password is needed to sign in and approve administrative actions.

## Validation

- The display name must be non-empty after trimming whitespace and must reject control characters.
- The username must follow the system's documented local-account naming policy, be unique, and be validated before any account is created.
- A generated username must be deterministic for the same normalized display name. If it is already taken, suggest a numbered alternative and let the user edit it.
- The password and confirmation must match exactly. Do not trim, normalize, log, or silently modify passwords.
- Password policy should allow long passphrases and be implemented once in the account service, not separately in each UI.
- Invalid input must never result in a partially created account.

## Privacy and credential handling

- All profile setup runs locally. No profile fields or password checks are sent over the network.
- Passwords must never be written to installer logs, debug output, crash reports, analytics, or the generated profile summary.
- The UI must clear password fields when leaving the screen or after a failed submission that cannot safely preserve them.
- The account service must pass credentials directly to the system account/authentication interface. The installer must not invent its own password storage format or keep plaintext credentials in a profile file.
- The profile summary may contain the display name, username, and account type, but never the password or password hash.
- Profile creation is a local installation action and must not create an online identity.

## Creation and rollback

- Validate every field and check username availability before modifying the target installation.
- Create the account only inside the selected target root, never on the build host or Live host.
- Create the home directory with ownership assigned to the new user and restrictive default permissions.
- Add the first user to the documented administrative authorization group only after the user-creation operation succeeds.
- Do not enable automatic login by default.
- If any account-creation step fails, stop installation finalization, report the failure without exposing credentials, and roll back the incomplete account changes inside the target root.
- The installer must show a final summary with the display name, username, and administrative-access behavior before committing installation changes.

## Acceptance tests

- A first-time user can create a profile using only the graphical interface and keyboard.
- Username suggestion, editing, duplicate handling, invalid-character handling, and password mismatch are tested.
- Tests prove passwords never appear in logs, summaries, or generated configuration.
- Tests prove no user is created on the installer host or build host.
- Tests prove a failed account-creation operation does not leave a partial account.
- Tests prove the first account uses the user-first sudo model and does not require interactive root login.
