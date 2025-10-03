import argparse
from main import main

def parse_args():
    parser = argparse.ArgumentParser(description="Run Pesticide Checker")
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to the PDF file to analyze"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(pdf_path=args.pdf)