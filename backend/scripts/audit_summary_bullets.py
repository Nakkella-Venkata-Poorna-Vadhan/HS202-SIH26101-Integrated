"""Extract official sub-themes from KCM summary pages (p25, p27, p29-33)."""
import pymupdf

doc = pymupdf.open(r"data\raw\KCM-Output_RestructuredOct17.pdf")

pages = [25, 27, 29, 30, 31, 32, 33]

for pno in pages:
    page = doc[pno - 1]
    blocks = page.get_text("blocks")
    print(f"=== PAGE {pno} ===")
    for b in sorted(blocks, key=lambda x: (x[1], x[0])):
        t = b[4].strip()
        if "•" in t or "1." in t or "2." in t or "3." in t or "4." in t or "5." in t:
            print("  --- BLOCK ---")
            for l in t.splitlines():
                if l.strip():
                    print("   ", l.strip())

doc.close()
