#!/usr/bin/env python3
"""Compare your original LoL3 install with the measured edition fingerprints."""
from hashlib import sha256
import os
from pathlib import Path

from cli_errors import ReaderArgumentParser, game_path, run_cli


WITNESSES = {'English GOG release (1.07a)': {'LOL3.DAT': (1643520, '9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea'),
                           'LOL3.EXE': (77824, '47653b3971fd623cde6c15bc29ec063d3b3ce26d500887f1c6c60abedcc81bc6'),
                           'LOCAL.WSX': (39557829, 'ee7d077af31aad4e3180562ae1be73a6b1c7d18be7ffc67556b24399ddfcca8c'),
                           'DAT/LOCAL.WSX': (39557829,
                                             'ee7d077af31aad4e3180562ae1be73a6b1c7d18be7ffc67556b24399ddfcca8c'),
                           'DAT/GLOBAL.WSX': (8521360,
                                              '8dee4f4fdbc30b018958259c4a026f490044d01567f7cb6d73552545b4c517a9'),
                           'DAT/QWOD0.WSX': (7832695,
                                             '23bd769621be5e0de334c63cc01bc1eb56c4027fdcb590ef3d1635ce014c64c2')}}
SUBFOLDER = "DAT"
DATA_ENV = "LOL3_DAT"


def locate(root, name):
    path = game_path(root, name)
    return path if path.is_file() else None


def identify(root):
    names = dict.fromkeys(name for rows in WITNESSES.values() for name in rows)
    if SUBFOLDER == "DATA":
        child = game_path(root, SUBFOLDER)
        root = child if child.is_dir() else root
    elif SUBFOLDER == "DAT" and root.name.upper() == "DAT":
        root = root.parent
    found = {}
    for name in names:
        path = locate(root, name)
        if path is not None:
            with path.open("rb") as stream:
                found[name] = (path.stat().st_size, sha256_stream(stream))
    return root, found


def sha256_stream(stream):
    digest = sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def status(expected, observed):
    if observed is None:
        return "missing"
    return "matches" if observed == expected else "differs"


def main(argv=None):
    parser = ReaderArgumentParser(description=__doc__)
    default = os.environ.get(DATA_ENV)
    parser.add_argument("--data", type=Path, default=default, required=default is None,
                        help=f"your game folder or its {SUBFOLDER} folder (default: ${DATA_ENV})")
    parser.add_argument("--check", action="store_true",
                        help="verify that all fingerprint files match a measured edition")
    args = parser.parse_args(argv)
    root, found = identify(args.data.resolve())
    if not found:
        parser.error(f"No edition files found in {root}. Give --data your original game installation or its data folder.")

    def score(edition):
        _, rows = edition
        return (all(found.get(name) == value for name, value in rows.items()),
                sum(found.get(name) == value for name, value in rows.items()),
                sum(name in found for name in rows))

    label, rows = max(WITNESSES.items(), key=score)
    statuses = {name: status(value, found.get(name)) for name, value in rows.items()}
    differences = [f"{name} {value}" for name, value in statuses.items() if value != "matches"]
    summary = f"{label}: all {len(rows)} fingerprint files match in {root}."
    if args.check:
        if differences:
            raise ValueError(f"The {label} fingerprint does not match in {root} ({', '.join(differences)}). "
                             "Check an unmodified copy or run without --check for sizes and checksums.")
        print(f"CHECK edition: {summary}")
        return 0

    print("File | Bytes | SHA-256 | Status")
    for name, result in statuses.items():
        size, checksum = found.get(name, ("—", "—"))
        print(f"{name} | {size} | {checksum} | {result}")
    if differences:
        print(f"No complete edition fingerprint matches in {root}. The table compares with {label}.")
        return 1
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
