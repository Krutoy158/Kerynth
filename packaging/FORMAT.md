# Kerynth Package Format (.ker)

**Status:** proposed format draft, version 1. The builder and verifier are experimental prototypes, not a stable package manager or installer.

## 1. Design goals

- deterministic package contents
- authenticated metadata and payload
- safe inspection before extraction
- explicit dependencies and conflicts
- no package-controlled installation scripts

## 2. Container layout

A `.ker` file is a POSIX ustar archive containing exactly three regular-file members in this order: `manifest.json`, `payload.tar`, and `signature.ed25519`. Additional members, duplicate names, links, and directory entries are rejected. Compression is not defined in version 1.

## 3. Manifest

The manifest is UTF-8 JSON without a BOM or trailing newline. Canonical serialization uses UTF-8, lexicographically sorted object keys, no insignificant whitespace, integer-only numbers, and no duplicate keys. Unknown fields are rejected.

Required fields are `format_version`, `name`, `version`, `architecture`, `description`, `dependencies`, `conflicts`, `payload_sha256`, and `signing_key_id`.

Package names match `[a-z0-9][a-z0-9+_.-]*`. The prototype accepts a conservative version-character set, but dependency version semantics are not defined. Dependency and conflict entries contain a package `name` and may contain a `version` string. The prototype does not resolve dependencies.

## 4. Payload archive

The payload is a separate ustar archive. Paths are relative to the target filesystem root. Only regular files and directories are accepted.

The prototype rejects absolute paths, backslashes, empty, dot, and parent components, non-normalized and duplicate paths, links, special entries, PAX metadata, setuid/setgid bits, and non-normalized ownership. UID/GID must be zero in the archive; installation ownership is not implemented.

The verifier scans archive metadata without extracting files. No installer exists.

## 5. Signature

Ed25519 signs this exact byte sequence:

```text
"KERYNTH-KER-V1\\0" || manifest_bytes || raw_payload_sha256
```

The public key is selected from a local JSON keyring by `signing_key_id`. The package cannot add keys to the keyring. Unknown keys are rejected.

## 6. Prototype commands

Install the test dependency with `python -m pip install -r requirements-test.txt`. Keep the private key outside the repository. The local keyring maps key IDs to 32-byte Ed25519 public keys encoded as hexadecimal.

Build:

```sh
python tools/ker-package build \
  --payload-dir ./staging-root \
  --name hello-kerynth \
  --version 1.0 \
  --description "Example package" \
  --key-id local-test-key \
  --private-key ./private-key.pem \
  --output ./hello-kerynth.ker
```

Verify:

```sh
python tools/ker-package verify ./hello-kerynth.ker --keyring ./trusted-keys.json
```

There is no install, remove, upgrade, dependency solver, repository metadata, key revocation service, or Debian importer. Do not use this prototype to install software on a live system.

## 7. Debian import

A future importer must treat control fields, scripts, triggers, and archive members as data. It must never execute maintainer scripts during inspection or conversion. Unsupported dependencies, scripts, triggers, links, special files, or filesystem assumptions must cause a clear refusal.

## 8. Compatibility and tests

The format version is independent of the Kerynth distribution version. Readers reject unsupported format versions. Before version 1 is stable, the format needs independent review and test vectors for valid packages, malformed archives, invalid signatures, digest mismatches, duplicate JSON keys, traversal, and unsupported entry types.
