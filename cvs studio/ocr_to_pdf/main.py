import os
import argparse
import easyocr
import PyPDF2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from tqdm import tqdm


class OCRtoPDF:
    def __init__(self):
        # Initialize EasyOCR reader with English language
        print("Initializing OCR engine...")
        self.reader = easyocr.Reader(['en'])
        print("OCR engine initialized successfully!")

    def extract_text_from_image(self, image_path):
        """Extract text from image using EasyOCR"""
        print(f"Extracting text from {image_path}...")
        try:
            result = self.reader.readtext(image_path)
            # Extract just the text from the result
            extracted_text = ' '.join([item[1] for item in result])
            print(f"Extracted {len(extracted_text)} characters from the image.")
            return extracted_text
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return ""

    def create_new_pdf(self, text, output_path):
        """Create a new PDF with the extracted text"""
        print(f"Creating new PDF at {output_path}...")
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            style = styles["Normal"]
            
            # Split text into paragraphs and create paragraph objects
            paragraphs = [Paragraph(p, style) for p in text.split('\n\n')]
            
            # Build PDF document
            doc.build(paragraphs)
            print(f"New PDF created successfully at {output_path}")
            return True
        except Exception as e:
            print(f"Error creating new PDF: {str(e)}")
            return False

    def add_text_to_existing_pdf(self, text, existing_pdf_path, output_path):
        """Add extracted text to an existing PDF file"""
        print(f"Adding text to existing PDF {existing_pdf_path}...")
        try:
            # Create a temporary PDF with the text
            temp_text_pdf = "temp_text.pdf"
            self.create_new_pdf(text, temp_text_pdf)
            
            # Open the existing PDF
            pdf_reader = PyPDF2.PdfReader(existing_pdf_path)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add all pages from existing PDF to the writer
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
            
            # Add the text PDF pages to the writer
            text_pdf_reader = PyPDF2.PdfReader(temp_text_pdf)
            for page_num in range(len(text_pdf_reader.pages)):
                page = text_pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
            
            # Write the result to the output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Clean up temporary file
            if os.path.exists(temp_text_pdf):
                os.remove(temp_text_pdf)
                
            print(f"Text added to PDF successfully, saved at {output_path}")
            return True
        except Exception as e:
            print(f"Error adding text to existing PDF: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Extract text from images and add to PDF')
    parser.add_argument('--image', required=True, help='Path to the image file')
    parser.add_argument('--output', required=True, help='Path for the output PDF file')
    parser.add_argument('--existing-pdf', help='Path to existing PDF (optional)')
    
    args = parser.parse_args()
    
    # Initialize OCR processor
    ocr_processor = OCRtoPDF()
    
    # Extract text from image
    extracted_text = ocr_processor.extract_text_from_image(args.image)
    
    if not extracted_text:
        print("No text was extracted from the image. Exiting.")
        return
    
    # Process PDF based on user choice
    if args.existing_pdf:
        success = ocr_processor.add_text_to_existing_pdf(
            extracted_text, args.existing_pdf, args.output
        )
    else:
        success = ocr_processor.create_new_pdf(extracted_text, args.output)
    
    if success:
        print(f"Operation completed successfully. Output saved to: {args.output}")
    else:
        print("Operation failed.")


if __name__ == "__main__":
    main() 