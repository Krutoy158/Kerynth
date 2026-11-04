# Signed .ker repositories

The ker-repository tool creates and verifies a signed package index and synchronizes verified packages into a local cache. It is a development-host tool at this stage; it is not yet installed in the minimal Kerynth root filesystem and does not automatically update the running OS.

## Repository layout

A repository contains:

- index.json: canonical UTF-8 JSON containing repository identity and package metadata.
- index.ed25519: Ed25519 signature over the index, using the KERYNTH-KER-REPOSITORY-V1 signing domain.
- One .ker file for each indexed package.

Each package must independently pass .ker signature verification. The index includes the filename, package identity, version, architecture, description, dependency and conflict metadata, file size, and SHA-256 digest. Duplicate package names are rejected so a repository has one selected version per package.

## Build a repository

Prepare a directory containing signed .ker packages and a JSON keyring containing the trusted Ed25519 public keys. The repository signing key must be present in that keyring as well.

    python3 tools/ker-repository build \
      --repository stable \
      --packages-dir ./packages \
      --output-dir ./repo/stable \
      --keyring ./trusted-keys.json \
      --key-id release-2026 \
      --private-key ./release-private.pem

The output directory must not already exist. The private signing key should be kept offline or in a protected release environment and must not be committed to the repository.

## Verify a local repository

    python3 tools/ker-repository verify \
      --repo-dir ./repo/stable \
      --keyring ./trusted-keys.json

Verification checks the index signature, canonical index encoding, package list, package file sizes and hashes, package signatures, and agreement between signed package manifests and repository metadata. Unindexed .ker files are rejected.

## Synchronize a repository

Publish the repository directory over HTTPS, then run:

    python3 tools/ker-repository sync \
      --url https://packages.example.invalid/kerynth/stable/ \
      --cache-dir ~/.cache/kerynth/repositories \
      --keyring ./trusted-keys.json

Synchronization verifies the signed index before downloading package files, requires HTTPS (including after redirects), verifies each downloaded size and SHA-256 digest, and verifies every package signature before atomically placing it in the local cache. Existing valid cached packages are reused.

## Check installed package updates

The update checker reads package records from an existing installed root and compares them with a verified local repository. It does not create or modify files in the installed root.

    python3 tools/ker-repository updates \
      --repo-dir ./repo/stable \
      --keyring ./trusted-keys.json \
      --installed-root ./.kerynth-work/targets/test-install \
      --json

Only dot-separated numeric versions (for example, 1.2 or 1.2.3) are ordered automatically. A newer repository version is marked `update_available`; a repository version older than the installed one is marked `repository_older`, never as an update. Versions with suffixes or formats the checker cannot order are marked `manual_review`. The report always sets `automatic_changes` to false.

## Current limitations

This is the first repository-metadata and cache layer. It does not resolve dependency graphs, calculate upgrades, install packages into /, manage rollback transactions, rotate keys, or bootstrap a Python/cryptography runtime into the target system. The existing package installer still restricts installation to disposable build targets. A running-system package manager and update UI remain separate work.
