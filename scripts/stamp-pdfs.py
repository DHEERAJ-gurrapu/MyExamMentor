import fitz  # PyMuPDF
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

SEARCH_TEXT = "PMT"
STAMP_MARKER = "MEM_STAMPED"   # invisible marker text
MAX_WORKERS = 4                # safe for GitHub Actions


def is_pdf_stamped(doc):
    """Check if this PDF was already stamped"""
    for page in doc:
        if page.search_for(STAMP_MARKER):
            return True
    return False


def apply_safe_large_stamp(pdf_path, image_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return ("corrupt", pdf_path, str(e))

    try:
        if is_pdf_stamped(doc):
            doc.close()
            return ("skipped", pdf_path, "Already stamped")

        w_pad = 60
        h_pad = 25
        stamped = False

        for page in doc:
            page_rect = page.rect
            text_instances = page.search_for(SEARCH_TEXT)

            for inst in text_instances:
                new_x0 = max(page_rect.x0, inst.x0 - w_pad)
                new_y0 = max(page_rect.y0, inst.y0 - h_pad)
                new_x1 = min(page_rect.x1, inst.x1 + w_pad)
                new_y1 = min(page_rect.y1, inst.y1 + h_pad)

                large_rect = fitz.Rect(new_x0, new_y0, new_x1, new_y1)

                page.add_redact_annot(large_rect, fill=(1, 1, 1))
                page.apply_redactions()

                page.insert_image(
                    large_rect,
                    filename=image_path,
                    keep_proportion=True
                )

                stamped = True

            # Invisible marker so we know it's stamped
            page.insert_text(
                fitz.Point(-100, -100),
                STAMP_MARKER,
                fontsize=1,
                color=(1, 1, 1)
            )

        if stamped:
            doc.save(
                pdf_path,
                incremental=True,
                encryption=fitz.PDF_ENCRYPT_KEEP
            )
            result = ("stamped", pdf_path, None)
        else:
            result = ("no-text", pdf_path, "Search text not found")

        doc.close()
        return result

    except Exception as e:
        doc.close()
        return ("error", pdf_path, str(e))


def process_all_pdfs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))

    pdfs_dir = os.path.join(root_dir, "pdfs")
    image_path = os.path.join(root_dir, "mem1.png")

    if not os.path.exists(pdfs_dir):
        sys.exit("❌ pdfs folder not found")

    if not os.path.exists(image_path):
        sys.exit("❌ mem1.png not found")

    pdf_files = []
    for root, _, files in os.walk(pdfs_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    print(f"🔍 Found {len(pdf_files)} PDFs")

    stats = {
        "stamped": 0,
        "skipped": 0,
        "corrupt": 0,
        "no-text": 0,
        "error": 0,
    }

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(apply_safe_large_stamp, pdf, image_path)
            for pdf in pdf_files
        ]

        for future in as_completed(futures):
            status, path, info = future.result()
            stats[status] += 1

            if status == "stamped":
                print(f"✅ Stamped: {path}")
            elif status == "skipped":
                print(f"⏭ Skipped: {path}")
            elif status == "no-text":
                print(f"⚠ No '{SEARCH_TEXT}': {path}")
            else:
                print(f"❌ {status.upper()}: {path} ({info})")

    print("\n📊 SUMMARY")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    process_all_pdfs()
