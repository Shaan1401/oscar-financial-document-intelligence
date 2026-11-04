import sys
from pathlib import Path

# Add backend to python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.extraction.synthetic_generator import SyntheticStatementGenerator

def main():
    pdf_dir = ROOT / "sample_data" / "pdf"
    gt_dir = ROOT / "sample_data" / "ground_truth"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    pdf_a = pdf_dir / "synthetic_statement_layout_a.pdf"
    gt_a = gt_dir / "synthetic_statement_layout_a_truth.json"

    print(f"Generating Layout A PDF: {pdf_a}")
    SyntheticStatementGenerator.generate_layout_a(pdf_a, gt_a)
    print("Layout A generated successfully!")

if __name__ == "__main__":
    main()
