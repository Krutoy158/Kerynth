# Kerynth privacy and telemetry policy

## Zero-telemetry rule

Kerynth does not send diagnostic, analytics, behavioral, crash-report, usage, advertising, or device-inventory data to the project maintainers. No unique device identifier is generated for remote reporting. Local hardware discovery is permitted only to identify the machine's own devices and select compatible drivers or firmware.

## Local hardware inventory

The \`kerynth-hw\` utility reads local Linux sysfs device attributes, the installed kernel module database, firmware files, and (when available) local \`modinfo\` output. It prints a local report or JSON to standard output. It does not connect to a remote service or upload its results.

## Network activity

Network access required for explicitly requested package-repository synchronization or system updates is separate from telemetry. Repository operations contact the configured HTTPS repository to obtain package metadata and package files. They must not include hardware inventory, usage history, crash reports, or a persistent device identifier.

No background update polling, analytics beacon, telemetry daemon, or automatic diagnostic upload is permitted by this policy. Any future optional diagnostic export must remain local until the user explicitly chooses to share it.

## Verification

The hardware inventory tool reports \`telemetry: false\`. Unit tests check that its implementation does not import general network-client modules. These checks cover the current hardware inventory component; every new network-capable component must be reviewed separately before release.
