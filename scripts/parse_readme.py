import json
import re
import os

README_PATH = os.path.join(os.path.dirname(__file__), '..', 'README.md')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'readme.json')

def parse_table(lines):
    """
    Givet linjer fra en Markdown-tabel, returnér liste af dicts.
    Forventet format:
        | Col1 | Col2 | ...
        | ---- | ---- | ...
        | val1 | val2 | ...
    """
    # Fjern eventuelle tomme linjer
    lines = [l for l in lines if l.strip()]

    if not lines:
        return []

    # Første linje er overskrifter
    headers_line = lines[0].strip().strip('|')
    headers = [h.strip() for h in headers_line.split('|')]

    # Anden linje er "separator" (f.eks. | --- | --- |)
    # Resten er data
    data_lines = lines[2:]  # spring separator-linjen over

    rows = []
    for dl in data_lines:
        dl = dl.strip().strip('|')
        if not dl:
            continue
        parts = [p.strip() for p in dl.split('|')]
        row = {}
        for idx, col in enumerate(parts):
            if idx < len(headers):
                row[headers[idx]] = col
        rows.append(row)
    return rows

def main():
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()

    sections = []
    current_section = None
    current_table_lines = []
    in_table = False

    for line in content:
        # Tjek om vi møder en ny sektion (## Overskrift)
        if re.match(r'^##\s+', line):
            # Hvis vi har en igangværende sektion, gem den gamle tabel
            if current_section and current_table_lines:
                # parse den sidste tabel
                parsed_table = parse_table(current_table_lines)
                current_section["tables"].append(parsed_table)
                current_table_lines = []
                in_table = False

            # Start en ny sektion
            section_title = line.replace('##', '').strip()
            current_section = {
                "title": section_title,
                "tables": []
            }
            sections.append(current_section)
            continue

        # Er vi i en sektion, og linjen ligner en tabel?
        if current_section:
            if line.strip().startswith('|') and line.strip().endswith('|'):
                # Linjen er en del af en tabel
                current_table_lines.append(line)
                in_table = True
            else:
                # Hvis vi netop var i table-mode, og nu stopper det
                if in_table and not (line.strip().startswith('|') and line.strip().endswith('|')):
                    # parse den tabel vi lige har opsamlet
                    parsed_table = parse_table(current_table_lines)
                    current_section["tables"].append(parsed_table)
                    current_table_lines = []
                    in_table = False
                # Ellers er det bare tekst i sektionen, som vi ignorerer i dette eksempel.
                # Man kunne gemme "free text" her, hvis man ville.
                pass

    # Hvis filen sluttede mens vi var midt i en tabel
    if current_section and current_table_lines:
        parsed_table = parse_table(current_table_lines)
        current_section["tables"].append(parsed_table)

    # Gem data som JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        json.dump({"sections": sections}, out, ensure_ascii=False, indent=2)

    print(f"Skrev JSON til {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
