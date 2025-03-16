import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageToText:
    def __init__(self, tesseract_cmd=None, lang='eng'):
        """
        Initialize the image to text converter.
        
        Args:
            tesseract_cmd (str): Path to the Tesseract executable
            lang (str): Language for OCR
        """
        # Set Tesseract command path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is properly installed")
        except Exception as e:
            logger.error(f"Tesseract OCR is not properly installed: {e}")
            logger.error("Please install Tesseract OCR and make sure it's in your PATH")
        
        self.lang = lang
    
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image (numpy.ndarray): Input image
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply thresholding to get a binary image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Apply noise removal
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def extract_text_from_image(self, image_path, preprocess=True):
        """
        Extract text from an image file.
        
        Args:
            image_path (str): Path to the image file
            preprocess (bool): Whether to preprocess the image
            
        Returns:
            str: Extracted text
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
                
            logger.info(f"Extracting text from image: {image_path}")
            
            # Read the image
            image = cv2.imread(image_path)
            
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Preprocess the image if requested
            if preprocess:
                processed_image = self.preprocess_image(image)
                
                # Save the processed image to a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_filename = temp_file.name
                temp_file.close()
                
                cv2.imwrite(temp_filename, processed_image)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(Image.open(temp_filename), lang=self.lang)
                
                # Clean up temporary file
                os.unlink(temp_filename)
            else:
                # Extract text directly using Tesseract
                text = pytesseract.image_to_string(Image.open(image_path), lang=self.lang)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return None
    
    def extract_text_from_image_data(self, image_data, preprocess=True):
        """
        Extract text from image data.
        
        Args:
            image_data (numpy.ndarray): Image data
            preprocess (bool): Whether to preprocess the image
            
        Returns:
            str: Extracted text
        """
        try:
            # Preprocess the image if requested
            if preprocess:
                processed_image = self.preprocess_image(image_data)
                
                # Save the processed image to a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_filename = temp_file.name
                temp_file.close()
                
                cv2.imwrite(temp_filename, processed_image)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(Image.open(temp_filename), lang=self.lang)
                
                # Clean up temporary file
                os.unlink(temp_filename)
            else:
                # Convert image data to PIL Image
                pil_image = Image.fromarray(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
                
                # Extract text directly using Tesseract
                text = pytesseract.image_to_string(pil_image, lang=self.lang)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image data: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path, dpi=300):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            dpi (int): DPI for PDF rendering
            
        Returns:
            str: Extracted text
        """
        try:
            from pdf2image import convert_from_path
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return None
                
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=dpi)
            
            # Extract text from each page
            text_results = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                
                # Convert PIL Image to OpenCV format
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Extract text
                page_text = self.extract_text_from_image_data(opencv_image)
                
                if page_text:
                    text_results.append(page_text)
            
            # Combine text from all pages
            return "\n\n".join(text_results)
            
        except ImportError:
            logger.error("pdf2image is required for PDF extraction")
            return None
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract text from images")
    parser.add_argument("--input", required=True, help="Path to the image or PDF file")
    parser.add_argument("--tesseract", help="Path to Tesseract executable")
    parser.add_argument("--lang", default="eng", help="Language for OCR")
    parser.add_argument("--no-preprocess", action="store_true", help="Skip image preprocessing")
    
    args = parser.parse_args()
    
    converter = ImageToText(tesseract_cmd=args.tesseract, lang=args.lang)
    
    # Check if the input is a PDF
    if args.input.lower().endswith(".pdf"):
        text = converter.extract_text_from_pdf(args.input)
    else:
        text = converter.extract_text_from_image(args.input, preprocess=not args.no_preprocess)
    
    if text:
        print(f"Extracted text:\n{text}")
    else:
        print("Text extraction failed") 