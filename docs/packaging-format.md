# Kerynth Package Format (.ker)

**Status:** experimental format version 1. The package builder, verifier, and disposable-root installer are development prototypes. The format and command interface may still change before a stable release.

## Container layout

A `.ker` file is a POSIX ustar archive containing exactly three regular-file members in this order:

1. `manifest.json`
2. `payload.tar`
3. `signature.ed25519`

Additional members, duplicate names, links, directory entries, and PAX metadata are rejected. Compression is not defined in version 1.

## Manifest

The manifest is UTF-8 JSON without a BOM or trailing newline. Canonical serialization uses UTF-8, lexicographically sorted object keys, no insignificant whitespace, integer-only numbers, and no duplicate keys. Unknown fields are rejected.

Required fields are `format_version`, `name`, `version`, `architecture`, `description`, `dependencies`, `conflicts`, `payload_sha256`, and `signing_key_id`.

Names match `[a-z0-9][a-z0-9+_.-]*`. A relation can be written as a package name or an exact version requirement. For example, `--depends libc=1.2.6`. Version comparison is exact string matching; range expressions and upgrade ordering are not implemented.

## Payload archive

Payload paths are relative to the target filesystem root. Only regular files and directories are accepted. Absolute paths, backslashes, empty, dot, and parent components, duplicate paths, file-as-parent collisions, links, special entries, PAX metadata, setuid/setgid bits, and non-normalized ownership are rejected. UID/GID must be zero in the archive. Installation preserves file modes but does not support package-owned symlinks or special device files.

## Signature

Ed25519 signs the domain separator `KERYNTH-KER-V1\0`, followed by the exact manifest bytes and the raw 32-byte payload SHA-256 digest.

The public key is selected from a local JSON keyring by `signing_key_id`. The package cannot add keys to the keyring. Unknown keys and invalid signatures are rejected.

## Commands

Install the test dependency:

```sh
python3 -m pip install -r requirements-test.txt
```

Keep the private signing key outside the repository. The keyring maps key IDs to 32-byte Ed25519 public keys encoded as hexadecimal.

Build a package:

```sh
python3 tools/ker-package build --payload-dir ./staging-root --name hello-kerynth --version 1.0 --description "Example package" --key-id local-test-key --private-key ./private-key.pem --output ./hello-kerynth.ker
```

Optional dependency and conflict flags can be repeated:

```sh
--depends libc=1.2.6 --depends base-files=0.1
--conflicts legacy-runtime
```

Verify:

```sh
python3 tools/ker-package verify ./hello-kerynth.ker --keyring ./trusted-keys.json
```

Install into a disposable test root:

```sh
python3 tools/ker-package install ./hello-kerynth.ker --keyring ./trusted-keys.json --root ./.kerynth-work/targets/test-root
```

List installed packages or remove one:

```sh
python3 tools/ker-package list --root ./.kerynth-work/targets/test-root
python3 tools/ker-package remove hello-kerynth --root ./.kerynth-work/targets/test-root
```

For safety, install/list/remove are restricted to a directory below `.kerynth-work/targets/`. They cannot target `/` or arbitrary host paths. The package database records ownership, exact dependencies, conflicts, and file hashes. Removal checks that package-owned files have not been modified and refuses to remove a package still required by another installed package.

## Not implemented

- Upgrade and downgrade transactions.
- Repository indexes, mirrors, metadata signatures, key rotation, and revocation.
- Version ranges, virtual packages, optional dependencies, and full dependency solving.
- Installation into a live Kerynth system with the explicit sudo boundary.
- Debian `.deb` inspection or conversion.
- Integration of this Python prototype into the minimal Kerynth userspace.
