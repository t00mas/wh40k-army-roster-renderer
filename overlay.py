from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def extract_annotations(base_pdf):
    """Extract annotations from the base PDF and return a dictionary of coordinates."""
    reader = PdfReader(base_pdf)
    annotations = []
    
    page = reader.pages[0]
    if '/Annots' in page:
        print("Extracting annotations...")
        for annot in page['/Annots']:
            annot_obj = annot.get_object()
            print(annot_obj)
            if annot_obj['/Subtype'] == '/Square' and '/Rect' in annot_obj:
                rect = annot_obj['/Rect']
                x = rect[0]
                y = rect[3]
                # no floats allowed
                annotations.append((int(x), int(y)))
    
    print(f"Extracted {len(annotations)} annotations.")
    print(annotations)
    return annotations

def create_overlay(units, annotations):
    """Create a PDF overlay with the text to insert at specific coordinates."""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    can.setFillColorRGB(0, 0, 0)  # Set text color to black
    
    for text in units:
        print(f"Placing text: '{text}' at {annotations[0]}")
        # get next annotation
        x, y = annotations.pop(0)
        # move text down according to font size too
        y -= 12
        can.drawString(x, y, text)
    
    can.showPage()  # Ensure the page is finalized
    can.save()
    packet.seek(0)
    return packet

def merge_pdfs(base_pdf, overlay_pdf, output_pdf):
    """Merge the overlay (text) PDF with the base PDF."""
    base = PdfReader(base_pdf)
    overlay = PdfReader(overlay_pdf)
    
    writer = PdfWriter()

    base_page = base.pages[0]
    overlay_page = overlay.pages[0]
    base_page.merge_page(overlay_page)
    writer.add_page(base_page)

    with open(output_pdf, 'wb') as out_pdf:
        writer.write(out_pdf)

# Example data mapping (adjust as needed)
data = [
    'Captain, Power Sword, Bolt Pistol',
    '80',
    'Tactical Squad, 5 Marines',
    '70',
    'Devastator Squad, 4 Marines',
    '140',
]

# Extract annotations from the base PDF
annotations = extract_annotations('official-roster.pdf')

# Create the overlay with the text
overlay = create_overlay(data, annotations)

# Debugging: Check if overlay PDF has content
overlay.seek(0)
overlay_reader = PdfReader(overlay)
print(f"Overlay PDF has {len(overlay_reader.pages)} pages.")

# Merge the overlay onto the original PDF
merge_pdfs('official-roster.pdf', overlay, 'output.pdf')
