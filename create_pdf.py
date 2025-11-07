from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("Retail_specification_1.pdf", pagesize=letter)
c.drawString(100, 750, "Retail Specification Checklist:")
with open("sample_spec.txt", 'r') as f:
    lines = f.read().split('\n')
y = 700
for line in lines:
    c.drawString(100, y, line)
    y -= 20
c.save()
print("PDF created! Retail_specification_1.pdf is ready.")

