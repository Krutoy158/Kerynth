# Kerynth Package Format (.ker)

**Status:** proposed format draft, version 1. The package manager and package verifier are not implemented. This document describes the format to be implemented and reviewed; it is not a claim of current compatibility.

## 1. Design goals

- deterministic package contents
- authenticated package metadata and payload
- safe inspection and extraction
- explicit dependencies and conflicts
- no package-controlled installation scripts
- support for transactional installation and rollback in the future package manager

## 2. Container layout

A `.ker` file is a POSIX ustar archive. It contains exactly these top-level members:

| Member | Required | Description |
|---|---|---|
| `manifest.json` | yes | UTF-8 package metadata in canonical form |
| `payload.tar` | yes | ustar archive containing the package files |
| `signature.ed25519` | yes | 64-byte Ed25519 signature |

The outer archive must not contain additional members, duplicate names, links, or directory entries. Members must be regular files. The outer archive must not use extensions or features outside the ustar format.

The payload is a separate ustar archive so that its exact bytes can be hashed and authenticated. Compression is not part of version 1. A later format version may define compression explicitly; implementations must not guess compression from file contents.

## 3. Manifest

The manifest is UTF-8 JSON with no byte-order mark. It must use canonical serialization:

- object keys sorted lexicographically by their UTF-8 byte representation
- no insignificant whitespace
- strings encoded as UTF-8
- integers only; floating-point values are forbidden
- duplicate object keys are forbidden
- the final byte is `}`, with no trailing newline

Required top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `format_version` | integer | Must be `1` |
| `name` | string | Lowercase package name |
| `version` | string | Package version |
| `architecture` | string | Target architecture, initially `x86_64` or `noarch` |
| `description` | string | Short package description |
| `dependencies` | array | Package dependency constraints |
| `conflicts` | array | Conflicting package constraints |
| `payload_sha256` | string | Lowercase SHA-256 of the exact `payload.tar` bytes |
| `signing_key_id` | string | Identifier of the trusted Ed25519 public key |

Package names must match `[a-z0-9][a-z0-9+_.-]*`. Version syntax and dependency constraint grammar must be specified by the package manager before packages are published. Unknown manifest fields must be rejected by version 1 readers unless a later compatibility rule explicitly permits them.

Each dependency or conflict entry is an object with `name` and optional `version` fields. The version constraint grammar is reserved until the dependency solver specification is published; implementations must not invent their own interpretation.

## 4. Payload archive

Payload paths are relative to the target filesystem root. The archive must contain regular files and directories only.

Version 1 rejects:
- absolute paths and paths containing `..` components
- empty path components, duplicate paths, and paths that normalize to a different path
- symbolic links and hard links
- device nodes, sockets, FIFOs, and other special entries
- setuid and setgid bits
- entries whose ownership or permissions cannot be represented safely

The archive must not contain a leading slash. Directory entries may be omitted; installers create required parent directories. File ownership is assigned by the installer according to package policy, not trusted from archive UID/GID values.

The manifest does not need a separate per-file digest list in version 1 because the signature authenticates the payload archive digest. The package verifier must still validate the tar structure and reject unsafe entries before extraction.

## 5. Signature

Signatures use Ed25519. The signature is calculated over this exact byte sequence:

```text
"KERYNTH-KER-V1\0" || manifest_bytes || raw_payload_sha256
```

Here `manifest_bytes` are the exact bytes stored in `manifest.json`, and `raw_payload_sha256` is the 32-byte binary value decoded from the manifest's hexadecimal `payload_sha256` field.

The public key is selected from a trusted local keyring using `signing_key_id`. The key identifier is a stable identifier defined by the repository metadata format. A package must be rejected if the key is unknown, revoked, or not trusted for the package's repository. The package must never supply or install its own trusted public key.

## 6. Verification and installation order

A future verifier must:

1. Parse the outer archive and enforce the exact member list and types.
2. Parse the manifest with duplicate-key detection and validate all fields.
3. Hash the exact `payload.tar` bytes and compare the digest.
4. Resolve `signing_key_id` from the configured trusted keyring.
5. Verify the Ed25519 signature.
6. Parse and validate every payload archive entry without extracting it.
7. Check package name, version, architecture, dependencies, conflicts, and installed-file ownership.
8. Only then allow a package manager transaction to stage installation.

A package manager must stage changes before committing them. It must record file ownership and transaction state and provide recovery from interrupted operations. Atomicity depends on filesystem capabilities and must not be claimed where it cannot be guaranteed.

## 7. No package scripts

Version 1 has no maintainer scripts, install hooks, trigger programs, or arbitrary commands embedded in packages. Package integration is declarative. Any future hook mechanism requires a separate reviewed specification with a strict trust and execution model.

## 8. Debian import

A Debian `.deb` importer treats control fields, scripts, triggers, and archive members as data. It must never execute Debian maintainer scripts during inspection or conversion.

A conversion may produce a `.ker` package only if all required metadata and filesystem behavior can be represented by version 1. Unsupported dependencies, scripts, triggers, links, special files, or filesystem assumptions must cause a clear refusal rather than silent loss of behavior.

## 9. CLI direction

The planned command-line interface is:

```sh
ker verify package.ker
ker install package.ker
ker deb inspect package.deb
ker reverse -C package.deb
```

These commands are interface proposals. They are not implemented yet. The `reverse` command is a compatibility alias only if it does not conflict with an existing system command.

## 10. Compatibility

The format version is independent of the Kerynth distribution version. A reader must reject unsupported `format_version` values. Any change to archive layout, signature input, manifest semantics, or payload safety rules requires a new format version or an explicitly backward-compatible amendment.

Before version 1 is declared stable, the specification must be reviewed and accompanied by test vectors covering valid packages, malformed archives, invalid signatures, digest mismatches, duplicate JSON keys, path traversal, and unsupported archive entry types.
