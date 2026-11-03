# AETHER Package Format (.aet)

**Status:** design draft; no stable binary format or installer is implemented yet.

## Goals

- deterministic package contents
- authenticated package metadata
- safe extraction
- explicit dependency and conflict declarations
- reliable package ownership tracking
- transactional installation and rollback

## Proposed container

The first implementation should use a well-supported archive container rather than inventing a compression algorithm. The exact container and manifest encoding must be selected before the format is declared stable.

A package will contain:
- `manifest.json`: package identity, version, architecture, dependencies, conflicts, file list, checksums, and format version
- `payload/`: files installed into the target root
- `SIGNATURE`: detached signature over canonical manifest and payload digest list

## Required manifest fields

- `format_version`
- `name`
- `version`
- `architecture`
- `description`
- `dependencies`
- `conflicts`
- `files`
- `payload_digest`
- `signing_key_id`

The canonical serialization rules must be specified so signatures do not depend on whitespace or object key order.

## Installation requirements

1. Verify the package signature against a trusted keyring.
2. Verify every payload checksum.
3. Validate every archive path before writing.
4. Reject absolute paths, parent traversal, duplicate paths, and entries that escape through symlinks.
5. Reject device nodes, sockets, and other special files in the initial format.
6. Check installed-file ownership and package conflicts.
7. Resolve dependencies before changing the target root.
8. Extract to a staging area on the same filesystem where possible.
9. Commit the transaction atomically where filesystem support permits.
10. Record package ownership and transaction history.
11. Roll back incomplete transactions.

Package installation scripts are not part of the initial format. System integration should use declarative service metadata and trusted package hooks implemented by the package manager itself.

## Debian import

Debian packages are imported, not blindly relabeled. The importer must parse the ar container, control archive, data archive, control fields, dependencies, conffiles, scripts, and triggers as data.

Maintainer scripts and triggers must never be executed during inspection or conversion. Unsupported behavior must be reported. The importer may produce an .aet package only when all required semantics are safely representable.

## CLI direction

```sh
aether package verify file.aet
aether install file.aet
aether deb inspect file.deb
aether reverse -C file.deb
```

The `reverse` command is a compatibility alias only if it does not shadow an existing command. The canonical interface remains under `aether`.
