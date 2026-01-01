#!/bin/sh

BASE_DIR="pdfs"
OUT_FILE="pdf-index.json"

echo "{" > "$OUT_FILE"

first_board=true

for board in "$BASE_DIR"/*; do
  [ -d "$board" ] || continue
  board_name=$(basename "$board")

  # Check if board has subjects with PDFs
  has_content=false
  for subject in "$board"/*; do
    [ -d "$subject" ] || continue
    if ls "$subject"/*.pdf >/dev/null 2>&1; then
      has_content=true
      break
    fi
  done

  [ "$has_content" = false ] && continue

  [ "$first_board" = true ] || echo "," >> "$OUT_FILE"
  first_board=false

  echo "  \"$board_name\": {" >> "$OUT_FILE"

  first_subject=true
  for subject in "$board"/*; do
    [ -d "$subject" ] || continue
    subject_name=$(basename "$subject")

    pdfs=$(ls "$subject"/*.pdf 2>/dev/null)
    [ -z "$pdfs" ] && continue

    [ "$first_subject" = true ] || echo "," >> "$OUT_FILE"
    first_subject=false

    echo "    \"$subject_name\": [" >> "$OUT_FILE"

    first_pdf=true
    for pdf in $pdfs; do
      pdf_name=$(basename "$pdf")

      [ "$first_pdf" = true ] || echo "," >> "$OUT_FILE"
      first_pdf=false

      echo "      \"$pdf_name\"" >> "$OUT_FILE"
    done

    echo "    ]" >> "$OUT_FILE"
  done

  echo "  }" >> "$OUT_FILE"
done

echo "}" >> "$OUT_FILE"

echo "✔ pdf-index.json generated"
