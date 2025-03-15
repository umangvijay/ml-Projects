import os
import logging
from fpdf import FPDF
import tempfile
from PIL import Image
import textwrap

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, page_size='A4', orientation='P', unit='mm', font='Arial'):
        """
        Initialize the PDF generator.
        
        Args:
            page_size (str): Page size (A4, Letter, etc.)
            orientation (str): Page orientation (P for Portrait, L for Landscape)
            unit (str): Unit of measurement (mm, pt, cm, in)
            font (str): Font family
        """
        self.page_size = page_size
        self.orientation = orientation
        self.unit = unit
        self.font = font
        
        # Initialize PDF object
        self.pdf = FPDF(orientation=orientation, unit=unit, format=page_size)
        
        # Set default font
        self.pdf.set_font(font, '', 12)
        
        # Add metadata
        self.pdf.set_title("Generated PDF")
        self.pdf.set_author("Speech and Image to PDF Converter")
        
        # Add first page
        self.pdf.add_page()
    
    def add_title(self, title, font_size=16, align='C'):
        """
        Add a title to the PDF.
        
        Args:
            title (str): Title text
            font_size (int): Font size
            align (str): Alignment (L, C, R)
        """
        self.pdf.set_font(self.font, 'B', font_size)
        self.pdf.cell(0, 10, title, 0, 1, align)
        self.pdf.ln(5)
        self.pdf.set_font(self.font, '', 12)
    
    def add_text(self, text, font_size=12, align='L'):
        """
        Add text to the PDF.
        
        Args:
            text (str): Text content
            font_size (int): Font size
            align (str): Alignment (L, C, R)
        """
        if not text:
            logger.warning("Empty text provided, skipping")
            return
            
        self.pdf.set_font(self.font, '', font_size)
        
        # Calculate effective page width for text
        effective_page_width = self.pdf.w - 2 * self.pdf.l_margin
        
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if paragraph.strip() == '':
                self.pdf.ln(5)
                continue
                
            # Wrap text to fit page width
            wrapped_text = textwrap.fill(paragraph, width=80)
            lines = wrapped_text.split('\n')
            
            for line in lines:
                self.pdf.multi_cell(effective_page_width, 5, line, 0, align)
            
            self.pdf.ln(3)
    
    def add_image(self, image_path, width=0, height=0, x=None, y=None, caption=None):
        """
        Add an image to the PDF.
        
        Args:
            image_path (str): Path to the image file
            width (float): Image width (0 for auto)
            height (float): Image height (0 for auto)
            x (float): X position (None for current position)
            y (float): Y position (None for current position)
            caption (str): Image caption
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return
                
            # Check if there's enough space on the current page
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate image dimensions if not specified
            if width == 0 and height == 0:
                # Use 75% of page width as default
                width = self.pdf.w * 0.75
                height = width * img_height / img_width
            elif width == 0:
                width = height * img_width / img_height
            elif height == 0:
                height = width * img_height / img_width
            
            # Check if image fits on current page
            if self.pdf.y + height + 10 > self.pdf.h:
                self.pdf.add_page()
            
            # Add image
            if x is None:
                x = (self.pdf.w - width) / 2
            if y is None:
                y = self.pdf.y
                
            self.pdf.image(image_path, x=x, y=y, w=width, h=height)
            
            # Update Y position
            self.pdf.y = y + height + 5
            
            # Add caption if provided
            if caption:
                self.pdf.set_font(self.font, 'I', 10)
                self.pdf.cell(0, 5, caption, 0, 1, 'C')
                self.pdf.set_font(self.font, '', 12)
                self.pdf.ln(5)
            
        except Exception as e:
            logger.error(f"Error adding image to PDF: {e}")
    
    def add_page_break(self):
        """
        Add a page break to the PDF.
        """
        self.pdf.add_page()
    
    def add_header(self, header_text):
        """
        Add a header to all pages.
        
        Args:
            header_text (str): Header text
        """
        self.pdf.set_header_fn(lambda: self._header_function(header_text))
    
    def _header_function(self, header_text):
        """
        Internal header function.
        
        Args:
            header_text (str): Header text
        """
        self.pdf.set_font(self.font, 'I', 8)
        self.pdf.cell(0, 10, header_text, 0, 0, 'C')
        self.pdf.ln(5)
    
    def add_footer(self, footer_text):
        """
        Add a footer to all pages.
        
        Args:
            footer_text (str): Footer text
        """
        self.pdf.set_footer_fn(lambda: self._footer_function(footer_text))
    
    def _footer_function(self, footer_text):
        """
        Internal footer function.
        
        Args:
            footer_text (str): Footer text
        """
        self.pdf.set_y(-15)
        self.pdf.set_font(self.font, 'I', 8)
        self.pdf.cell(0, 10, f'{footer_text} - Page {self.pdf.page_no()}', 0, 0, 'C')
    
    def save(self, output_path):
        """
        Save the PDF to a file.
        
        Args:
            output_path (str): Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Save the PDF
            self.pdf.output(output_path)
            
            logger.info(f"PDF saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return False
    
    def generate_from_text(self, text, title=None, output_path=None):
        """
        Generate a PDF from text.
        
        Args:
            text (str): Text content
            title (str): Document title
            output_path (str): Output file path
            
        Returns:
            str: Path to the generated PDF
        """
        try:
            # Reset PDF
            self.pdf = FPDF(orientation=self.orientation, unit=self.unit, format=self.page_size)
            self.pdf.set_font(self.font, '', 12)
            self.pdf.add_page()
            
            # Add title if provided
            if title:
                self.add_title(title)
            
            # Add text
            self.add_text(text)
            
            # Save PDF
            if output_path:
                return self.save(output_path)
            else:
                # Generate temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_filename = temp_file.name
                temp_file.close()
                
                self.save(temp_filename)
                return temp_filename
                
        except Exception as e:
            logger.error(f"Error generating PDF from text: {e}")
            return None
    
    def generate_from_text_and_images(self, text_blocks, image_paths, title=None, output_path=None):
        """
        Generate a PDF from text blocks and images.
        
        Args:
            text_blocks (list): List of text blocks
            image_paths (list): List of image paths
            title (str): Document title
            output_path (str): Output file path
            
        Returns:
            str: Path to the generated PDF
        """
        try:
            # Reset PDF
            self.pdf = FPDF(orientation=self.orientation, unit=self.unit, format=self.page_size)
            self.pdf.set_font(self.font, '', 12)
            self.pdf.add_page()
            
            # Add title if provided
            if title:
                self.add_title(title)
            
            # Interleave text blocks and images
            max_items = max(len(text_blocks), len(image_paths))
            
            for i in range(max_items):
                # Add text block if available
                if i < len(text_blocks) and text_blocks[i]:
                    self.add_text(text_blocks[i])
                    self.pdf.ln(5)
                
                # Add image if available
                if i < len(image_paths) and image_paths[i]:
                    self.add_image(image_paths[i])
                    self.pdf.ln(5)
            
            # Save PDF
            if output_path:
                return self.save(output_path)
            else:
                # Generate temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_filename = temp_file.name
                temp_file.close()
                
                self.save(temp_filename)
                return temp_filename
                
        except Exception as e:
            logger.error(f"Error generating PDF from text and images: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate PDF from text")
    parser.add_argument("--text", help="Text content")
    parser.add_argument("--text-file", help="Text file")
    parser.add_argument("--image", help="Image file")
    parser.add_argument("--title", default="Generated PDF", help="Document title")
    parser.add_argument("--output", required=True, help="Output PDF file")
    
    args = parser.parse_args()
    
    generator = PDFGenerator()
    
    # Get text content
    text_content = args.text
    if args.text_file:
        try:
            with open(args.text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            exit(1)
    
    if args.image:
        generator.generate_from_text_and_images([text_content], [args.image], title=args.title, output_path=args.output)
    else:
        generator.generate_from_text(text_content, title=args.title, output_path=args.output)
    
    print(f"PDF generated: {args.output}") 