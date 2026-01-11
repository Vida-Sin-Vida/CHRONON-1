import argparse
import sys
from chronon_core.reproduce import run_reproduce

def main():
    p = argparse.ArgumentParser(prog="chronon1", description="CHRONON-1 Scientific Pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    # reproduce command
    r = sub.add_parser("reproduce", help="Run reproducible pipeline end-to-end")
    r.add_argument("--config", required=True, help="Path to YAML config")

    # validate command (placeholder as requested)
    v = sub.add_parser("validate", help="Validate a dataset against the protocol schemas")
    v.add_argument("path", help="Path to dataset")

    args = p.parse_args()
    
    if args.cmd == "reproduce":
        try:
            run_reproduce(args.config)
        except Exception as e:
            print(f"Error during reproduction: {e}")
            sys.exit(1)
            
    elif args.cmd == "validate":
        print(f"Validation not yet implemented for {args.path}")

if __name__ == "__main__":
    main()
