import pdfplumber

def extract_items_from_pdf(pdf_path, items):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()

    sections = {}
    lines = full_text.split('\n')
    current_item = None
    for line in lines:
        # Check if the line is a section header
        if any(item in line for item in items):
            current_item = line.strip()
            sections[current_item] = ''
        elif current_item:
            sections[current_item] += line + '\n'

    return sections

pdf_path = 'AAPL_10K_2023.pdf'
items_to_extract = ['Item 1.', 'Item 7.', 'Item 7A.']
extracted_sections = extract_items_from_pdf(pdf_path, items_to_extract)

for item, content in extracted_sections.items():
    print(f"{item}\n{content}\n")
