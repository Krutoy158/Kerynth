# Build System

The first build tool is a small Python command-line program. It currently validates the build configuration and source lock file, then downloads locked source archives into a local cache after checking their SHA-256 digest.

It does not compile the kernel or install anything on the host yet.

## Requirements

- Python 3.11 or newer
- Network access for fetching source archives
- HTTPS source URLs
- A SHA-256 digest obtained from a trusted upstream release source

## Configuration

The build configuration is stored in `kerynth.toml`:

```toml
[build]
architecture = "x86_64"
workspace = ".kerynth-work"
```

The workspace must remain inside the project directory. Downloaded archives are stored under `.kerynth-work/sources/`.

## Source lock file

Each entry in `sources.lock` has a unique name, an HTTPS URL, a local filename, and a lowercase SHA-256 digest.

```json
{
  "version": 1,
  "sources": [
    {
      "name": "example-source",
      "url": "https://example.org/example-source.tar.xz",
      "filename": "example-source.tar.xz",
      "sha256": "replace-with-a-reviewed-64-character-sha256-digest"
    }
  ]
}
```

The example digest is deliberately not a valid lock entry. Do not add a source until its version, URL, and digest have been checked against upstream release information.

## Commands

Validate configuration and source metadata:

```sh
python3 tools/kerynth-build check
```

Fetch all locked sources:

```sh
python3 tools/kerynth-build fetch
```

Fetch one named source:

```sh
python3 tools/kerynth-build fetch linux
```

A cached archive is hashed again before it is reused. A mismatch causes the cached file to be discarded and downloaded again. Downloads are written to a temporary file and moved into place only after the digest matches.

## Current limitations

- No source archive is currently locked.
- No archive extraction is implemented.
- No compiler or sysroot is built yet.
- No build recipe execution is implemented.
- The tool does not provide sandboxing for future compiler processes; that must be designed before running build recipes.
