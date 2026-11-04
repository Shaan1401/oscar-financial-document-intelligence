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

    # 1. Layout A: Separate Debit and Credit columns
    pdf_a = pdf_dir / "synthetic_statement_layout_a.pdf"
    gt_a = gt_dir / "synthetic_statement_layout_a_truth.json"
    print(f"Generating Layout A PDF: {pdf_a}")
    SyntheticStatementGenerator.generate_layout_a(pdf_a, gt_a)
    print("Layout A generated successfully!")

    # 2. Layout B: Combined Amount with DR/CR tags
    pdf_b = pdf_dir / "synthetic_statement_layout_b.pdf"
    gt_b = gt_dir / "synthetic_statement_layout_b_truth.json"
    print(f"Generating Layout B PDF: {pdf_b}")
    SyntheticStatementGenerator.generate_layout_b(pdf_b, gt_b)
    print("Layout B generated successfully!")

    # 3. Layout C: Multi-Page with wrapped descriptions
    pdf_c = pdf_dir / "synthetic_statement_layout_c.pdf"
    gt_c = gt_dir / "synthetic_statement_layout_c_truth.json"
    print(f"Generating Layout C PDF: {pdf_c}")
    SyntheticStatementGenerator.generate_layout_c(pdf_c, gt_c)
    print("Layout C generated successfully!")

    # 4. Scanned PDF (Raster bitmap generated from Layout A)
    pdf_scanned = pdf_dir / "synthetic_statement_scanned.pdf"
    print(f"Generating Scanned PDF: {pdf_scanned}")
    SyntheticStatementGenerator.generate_scanned_pdf(pdf_scanned, pdf_a)
    print("Scanned PDF generated successfully!")

    print("\nAll synthetic demonstration PDFs and ground truth data generated successfully!")

if __name__ == "__main__":
    main()
