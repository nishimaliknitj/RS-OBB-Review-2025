"""
boi_calculator/boi_tool.py
==========================
Standalone, interactive BOI calculator.

Allows researchers to compute BOI for their own methods
without needing to load any paper data.

USAGE:
    python boi_calculator/boi_tool.py
    python boi_calculator/boi_tool.py --primary 8.2 --transfer 4.1
    python boi_calculator/boi_tool.py --batch methods.csv

FORMULA:
    BOI = delta_mAP_primary / delta_mAP_transfer

    BOI <= 1.5  → Transfers well (green zone)
    BOI 1.5-2.0 → Review carefully (amber zone)
    BOI > 2.0   → Does NOT transfer (red zone)
    BOI > 3.0   → Severe benchmark overfitting
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.python.boi_calculator import compute_boi, interpret_boi


def print_boi_report(method_name, primary, transfer, primary_dataset="DOTA-v1.0",
                     transfer_dataset="FAIR1M-2.0"):
    """Print a formatted BOI report for a single method."""
    boi = compute_boi(primary, transfer)
    interp = interpret_boi(boi)

    print(f"\n  Method:          {method_name}")
    print(f"  Primary ({primary_dataset}):  {primary:+.2f} mAP")
    print(f"  Transfer ({transfer_dataset}): {transfer:+.2f} mAP")
    print(f"  BOI:             {boi:.3f}")
    print(f"  Tier:            {interp['tier'].upper()}")
    print(f"  Transfers:       {'YES ✓' if interp['transfers'] else 'NO ✗'}")
    print(f"  Interpretation:  {interp['description']}")
    print(f"  Recommendation:  {interp['recommendation']}")

    # Visual bar
    bar_len = min(40, int(boi * 10))
    if boi <= 1.5:
        color_char = "█"
        zone = "SAFE"
    elif boi <= 2.0:
        color_char = "▓"
        zone = "CAUTION"
    else:
        color_char = "░"
        zone = "DANGER"
    print(f"\n  BOI [{zone}]:  {color_char * min(bar_len, 40)} {boi:.2f}")
    print(f"               {'|':<16}{'|':<16}{'|'}")
    print(f"               0         1.5        2.0+")


def interactive_mode():
    """Interactive prompt for computing BOI."""
    print("\n" + "="*60)
    print("  BOI Calculator — Benchmark Overfitting Index Tool")
    print("  Paper: RS OBB Detection Review 2025")
    print("="*60)
    print("\nEnter your augmentation results to compute BOI.")
    print("Type 'quit' to exit, 'help' for more info.\n")

    while True:
        try:
            name = input("  Method name (or 'quit'): ").strip()
            if name.lower() in ("quit", "q", "exit"):
                break
            if name.lower() == "help":
                print("\n  BOI = delta_mAP(primary) / delta_mAP(transfer)")
                print("  delta_mAP = augmented_mAP - baseline_mAP")
                print("  Typical primary: DOTA-v1.0")
                print("  Typical transfer: FAIR1M-2.0 or HRSC2016\n")
                continue

            primary_str = input(
                "  mAP gain on primary benchmark (e.g. DOTA-v1.0): ").strip()
            transfer_str = input(
                "  mAP gain on transfer benchmark (e.g. FAIR1M-2.0): ").strip()

            primary  = float(primary_str)
            transfer = float(transfer_str)

            print_boi_report(name, primary, transfer)
            print()

        except ValueError:
            print("  ERROR: Please enter numeric values for mAP gains.\n")
        except (KeyboardInterrupt, EOFError):
            break

    print("\nGoodbye.\n")


def batch_mode(csv_path):
    """Compute BOI for a batch of methods from a CSV file."""
    import csv

    print(f"\nReading methods from: {csv_path}")
    print(f"Expected columns: method,primary_gain,transfer_gain\n")

    results = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name     = row.get("method", row.get("name", "Unknown"))
            primary  = float(row["primary_gain"])
            transfer = float(row["transfer_gain"])
            boi      = compute_boi(primary, transfer)
            interp   = interpret_boi(boi)
            results.append((name, primary, transfer, boi, interp))

    # Sort by BOI ascending
    results.sort(key=lambda x: x[3])

    print(f"{'Method':<30} {'Primary':>8} {'Transfer':>9} "
          f"{'BOI':>6}  {'Tier':<14} {'Transfers?'}")
    print("-" * 80)
    for name, p, t, boi, interp in results:
        mark = "YES ✓" if interp["transfers"] else "NO  ✗"
        print(f"  {name:<28} {p:>8.2f} {t:>9.2f} "
              f"{boi:>6.3f}  {interp['tier']:<14} {mark}")

    n_transfer     = sum(1 for *_, i in results if i["transfers"])
    n_non_transfer = len(results) - n_transfer
    print(f"\n  Summary: {n_transfer} transfer, "
          f"{n_non_transfer} do NOT transfer "
          f"({n_non_transfer/len(results)*100:.1f}% BOI>2)")


def main():
    parser = argparse.ArgumentParser(
        description="Compute Benchmark Overfitting Index (BOI) for OBB methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python boi_calculator/boi_tool.py
  python boi_calculator/boi_tool.py --primary 7.4 --transfer 18.0 --name "FDA"
  python boi_calculator/boi_tool.py --batch my_methods.csv

CSV format for --batch:
  method,primary_gain,transfer_gain
  MyMethod,8.2,4.1
  AnotherMethod,5.3,5.0
        """
    )
    parser.add_argument("--primary",  type=float,
                        help="mAP gain on primary benchmark (e.g. DOTA-v1.0)")
    parser.add_argument("--transfer", type=float,
                        help="mAP gain on transfer benchmark (e.g. FAIR1M-2.0)")
    parser.add_argument("--name",     type=str, default="My Method",
                        help="Method name (for report)")
    parser.add_argument("--primary-dataset",  default="DOTA-v1.0")
    parser.add_argument("--transfer-dataset", default="FAIR1M-2.0")
    parser.add_argument("--batch",    type=str,
                        help="Path to CSV file for batch computation")

    args = parser.parse_args()

    if args.batch:
        if not os.path.exists(args.batch):
            print(f"ERROR: CSV file not found: {args.batch}")
            return 1
        batch_mode(args.batch)

    elif args.primary is not None and args.transfer is not None:
        print("\n" + "="*60)
        print("  BOI Calculator — Single Method Report")
        print("="*60)
        print_boi_report(
            args.name, args.primary, args.transfer,
            args.primary_dataset, args.transfer_dataset)
        print()

    else:
        interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
