#!/bin/sh

BASE_DIR="pdfs"
OUT_FILE="pdf-index.json"

echo "{" > "$OUT_FILE"

board_first=true

for board in "$BASE_DIR"/*; do
  [ -d "$board" ] || continue
  board_name=$(basename "$board")

  subject_first=true
  board_json=""

  for subject in "$board"/*; do
    [ -d "$subject" ] || continue
    subject_name=$(basename "$subject")

    year_first=true
    subject_json=""

    for year in "$subject"/*; do
      [ -d "$year" ] || continue
      year_name=$(basename "$year")

      # Collect PDFs safely (handles spaces)
      pdf_list=$(find "$year" -maxdepth 1 -type f -name "*.pdf" | sort)

      [ -z "$pdf_list" ] && continue

      [ "$year_first" = true ] || subject_json="$subject_json,"
      year_first=false

      subject_json="$subject_json
        \"$year_name\": ["

      pdf_first=true
      echo "$pdf_list" | while IFS= read -r pdf; do
        pdf_name=$(basename "$pdf")
        [ "$pdf_first" = true ] || subject_json="$subject_json,"
        pdf_first=false
        subject_json="$subject_json
          \"$pdf_name\""
      done

      subject_json="$subject_json
        ]"
    done

    [ -z "$subject_json" ] && continue

    [ "$subject_first" = true ] || board_json="$board_json,"
    subject_first=false

    board_json="$board_json
      \"$subject_name\": {$subject_json
      }"
  done

  [ -z "$board_json" ] && continue

  [ "$board_first" = true ] || echo "," >> "$OUT_FILE"
  board_first=false

  echo "  \"$board_name\": {$board_json
  }" >> "$OUT_FILE"
done

echo "}" >> "$OUT_FILE"

echo "✔ pdf-index.json generated dynamically from folders"
