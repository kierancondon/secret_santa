"""Create the fixed Secret Santa draw. Never prints pairings."""

import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS_VAR = "SECRETS"
ASSIGNMENTS_VAR = "ASSIGNMENTS"


def read_js_data(path, var):
    """Read `window.VAR = <json>;` so the site works from file:// without fetch()."""
    text = Path(path).read_text(encoding="utf-8")
    match = re.fullmatch(rf"\s*window\.{var}\s*=\s*(.*?);?\s*", text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse {Path(path).name}.")
    return json.loads(match.group(1))


def write_js_data(path, var, data):
    Path(path).write_text(
        f"window.{var} = {json.dumps(data, indent=2)};\n", encoding="utf-8"
    )


def normalize_name(value):
    return " ".join(value.split()).casefold()


# Error messages must never include names or pairings: the draw is a surprise.
def validate_secrets(entries):
    if not isinstance(entries, list) or len(entries) < 2:
        raise ValueError("Secrets list needs at least two participants.")
    for entry in entries:
        for key in ("realName", "secretName"):
            value = entry.get(key) if isinstance(entry, dict) else None
            if not isinstance(value, str) or not normalize_name(value):
                raise ValueError(f"Every secrets entry needs a non-empty {key}.")
    if len({normalize_name(e["realName"]) for e in entries}) != len(entries):
        raise ValueError("Real names must be unique.")
    if len({normalize_name(e["secretName"]) for e in entries}) != len(entries):
        raise ValueError("Secret names must be unique.")


def validate_draw(names, draw):
    if not isinstance(draw, dict) or set(draw) != set(names) or len(draw) != len(names):
        raise ValueError("Draw does not cover exactly the participants.")
    if any(draw[n] == n for n in names):
        raise ValueError("Someone drew themselves.")
    if sorted(draw.values()) != sorted(names):
        raise ValueError("Everyone must receive from exactly one giver.")


def draw_assignments(names, rng=None):
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("Need at least two unique names to draw.")
    rng = rng or secrets.SystemRandom()
    # Rejection sampling gives a uniform random derangement.
    while True:
        receivers = list(names)
        rng.shuffle(receivers)
        if all(giver != receiver for giver, receiver in zip(names, receivers)):
            return dict(zip(names, receivers))


def write_draw(secrets_path, out_path, redraw=False):
    out_path = Path(out_path)
    if out_path.exists() and not redraw:
        raise FileExistsError("A draw already exists. Pass --redraw to replace it.")
    entries = read_js_data(secrets_path, SECRETS_VAR)
    validate_secrets(entries)
    names = [e["realName"] for e in entries]
    draw = draw_assignments(names)
    validate_draw(names, draw)
    write_js_data(out_path, ASSIGNMENTS_VAR, draw)
    return len(names)


if __name__ == "__main__":
    try:
        count = write_draw(
            ROOT / "data" / "secrets.js",
            ROOT / "data" / "assignments.js",
            redraw="--redraw" in sys.argv,
        )
        print(f"Draw written for {count} participants. Pairings are not displayed.")
    except (ValueError, FileExistsError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
