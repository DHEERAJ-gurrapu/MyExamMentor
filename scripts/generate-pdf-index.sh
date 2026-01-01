#!/bin/sh

BASE_DIR="pdfs"
OUT_FILE="pdf-index.json"

echo "{" > "$OUT_FILE"

first_board=true

for board in "$BASE_DIR"/*; do
  [ -d "$board" ] || continue
  board_name=$(basename "$board")

  first_subject=true
  board_content=""

  for subject in "$board"/*; do
    [ -d "$subject" ] || continue
    subject_name=$(basename "$subject")

    first_year=true
    subject_content=""

    for year in "$subject"/*; do
      [ -d "$year" ] || continue
      year_name=$(basename "$year")

      pdfs=$(ls "$year"/*.pdf 2>/dev/null)
      [ -z "$pdfs" ] && continue

      [ "$first_year" = true ] || subject_content="$subject_content,"
      first_year=false

      subject_content="$subject_content
        \"$year_name\": ["

      first_pdf=true
      for pdf in $pdfs; do
        pdf_name=$(basename "$pdf")
        [ "$first_pdf" = true ] || subject_content="$subject_content,"
        first_pdf=false
        subject_content="$subject_content
          \"$pdf_name\""
      done

      subject_content="$subject_content
        ]"
    done

    [ -z "$subject_content" ] && continue

    [ "$first_subject" = true ] || board_content="$board_content,"
    first_subject=false

    board_content="$board_content
      \"$subject_name\": {$subject_content
      }"
  done

  [ -z "$board_content" ] && continue

  [ "$first_board" = true ] || echo "," >> "$OUT_FILE"
  first_board=false

  echo "  \"$board_name\": {$board_content
  }" >> "$OUT_FILE"
done

echo "}" >> "$OUT_FILE"

echo "✔ pdf-index.json generated with YEAR support"
