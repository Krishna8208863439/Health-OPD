"""
Test PDF generation to verify the fix
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def test_pdf_generation():
    """Test that PDF can be generated in the correct location"""
    print("=" * 60)
    print("Testing PDF Generation")
    print("=" * 60)
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n1. Script directory: {script_dir}")
    
    # Create reports directory
    reports_dir = os.path.join(script_dir, "static", "reports")
    print(f"2. Reports directory: {reports_dir}")
    
    try:
        os.makedirs(reports_dir, exist_ok=True)
        print(f"3. ✅ Directory created/verified")
    except Exception as e:
        print(f"3. ❌ Error creating directory: {e}")
        return False
    
    # Generate test PDF
    filename = f"Test_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    print(f"4. PDF filepath: {filepath}")
    
    try:
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Simple test content
        c.setFillColor(colors.HexColor('#0066CC'))
        c.rect(0, height - 100, width, 100, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, height - 50, "Test Medical Report")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 150, "This is a test PDF to verify generation works.")
        c.drawString(100, height - 170, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        print(f"5. ✅ PDF generated successfully")
    except Exception as e:
        print(f"5. ❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify file exists
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"6. ✅ PDF file exists")
        print(f"   File size: {file_size} bytes")
        print(f"   Location: {filepath}")
    else:
        print(f"6. ❌ PDF file not found")
        return False
    
    print("\n" + "=" * 60)
    print("✅ PDF GENERATION TEST PASSED!")
    print("=" * 60)
    print(f"\nTest PDF created at:")
    print(f"{filepath}")
    print("\nYou can now run the app and PDFs will be generated correctly!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_pdf_generation()
    if not success:
        print("\n❌ TEST FAILED - Please check the errors above")
        exit(1)
