import fitz  # PyMuPDF
import os

def apply_safe_large_stamp(pdf_path, image_path, search_text="PMT"):
    doc = fitz.open(pdf_path)

    w_pad = 60
    h_pad = 25

    for page in doc:
        page_rect = page.rect
        text_instances = page.search_for(search_text)

        for inst in text_instances:
            new_x0 = max(page_rect.x0, inst.x0 - w_pad)
            new_y0 = max(page_rect.y0, inst.y0 - h_pad)
            new_x1 = min(page_rect.x1, inst.x1 + w_pad)
            new_y1 = min(page_rect.y1, inst.y1 + h_pad)

            large_rect = fitz.Rect(new_x0, new_y0, new_x1, new_y1)

            # Remove underlying text
            page.add_redact_annot(large_rect, fill=(1, 1, 1))
            page.apply_redactions()

            # Insert image
            try:
                page.insert_image(
                    large_rect,
                    filename=image_path,
                    keep_proportion=True
                )
            except TypeError:
                page.insert_image(large_rect, filename=image_path)

    # Save IN-PLACE (replace original)
    doc.save(pdf_path, incremental=False)
    doc.close()


def process_all_pdfs():
    # Go one level up from this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))

    pdfs_dir = os.path.join(root_dir, "pdfs")
    image_path = os.path.join(root_dir, "mem1.png")

    if not os.path.exists(pdfs_dir):
        raise FileNotFoundError(f"'pdfs' folder not found at {pdfs_dir}")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"'mem1.png' not found at {image_path}")

    for root, _, files in os.walk(pdfs_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"Stamping: {pdf_path}")
                apply_safe_large_stamp(pdf_path, image_path)

    print("✅ All PDFs stamped successfully!")


if __name__ == "__main__":
    process_all_pdfs()
