"""
Demo: Load screening data with sp.load().

Run from project root:
  python docs/usage/demo_load_csv.py

Or from docs/usage:
  python demo_load_csv.py

Comma-delimited (default) is common. For tab-delimited files:
  raw, rpt = sp.load(relative_path, delimiter="\t")
"""

from pathlib import Path

from sprime import SPrime as sp

# Path to demo data (comma-delimited, S'-only checkpoint)
_SCRIPT_DIR = Path(__file__).resolve().parent
DEMO_CSV = _SCRIPT_DIR / "demo_data_s_prime.csv"


def main():
    # Comma-delimited (default); use delimiter="\t" for tab-delimited
    print("Loading demo_data_s_prime.csv (comma-delimited)...")
    raw, rpt = sp.load(DEMO_CSV)
    print(f"Loaded {len(raw)} profile(s)")
    for p in raw.profiles:
        print(f"  - {p.compound.name} vs {p.cell_line.name}")


if __name__ == "__main__":
    main()
