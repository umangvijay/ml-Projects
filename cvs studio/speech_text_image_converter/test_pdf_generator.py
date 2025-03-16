import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_generator import PDFGenerator

def main():
    """
    Test the PDF generator functionality.
    """
    # Create a sample text
    sample_text = """
    # Speech and Image to PDF Converter

    This is a test of the PDF generator functionality.
    
    ## Features
    
    - Speech Recognition
    - OCR (Optical Character Recognition)
    - PDF Generation
    
    This application uses machine learning to:
    1. Convert speech to text
    2. Extract text from images
    3. Generate PDF documents from the extracted text
    """
    
    # Initialize PDF generator
    generator = PDFGenerator()
    
    # Generate PDF
    output_path = "test_output.pdf"
    generator.generate_from_text(sample_text, title="Test PDF", output_path=output_path)
    
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    main() 