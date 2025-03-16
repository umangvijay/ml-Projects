import os
import argparse
import logging
import sys
from datetime import datetime

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.speech_to_text import SpeechToText
from src.image_to_text import ImageToText
from src.pdf_generator import PDFGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_audio(audio_file, use_advanced_model=False):
    """
    Process an audio file and extract text.
    
    Args:
        audio_file (str): Path to the audio file
        use_advanced_model (bool): Whether to use the advanced model
        
    Returns:
        str: Extracted text
    """
    if not audio_file:
        return None
        
    logger.info(f"Processing audio file: {audio_file}")
    
    # Initialize speech to text converter
    converter = SpeechToText(use_advanced_model=use_advanced_model)
    
    # Extract text
    text = converter.transcribe_from_file(audio_file)
    
    if text:
        logger.info(f"Successfully extracted text from audio")
    else:
        logger.error(f"Failed to extract text from audio")
    
    return text

def process_image(image_file, tesseract_cmd=None, lang='eng', preprocess=True):
    """
    Process an image file and extract text.
    
    Args:
        image_file (str): Path to the image file
        tesseract_cmd (str): Path to Tesseract executable
        lang (str): Language for OCR
        preprocess (bool): Whether to preprocess the image
        
    Returns:
        str: Extracted text
    """
    if not image_file:
        return None
        
    logger.info(f"Processing image file: {image_file}")
    
    # Initialize image to text converter
    converter = ImageToText(tesseract_cmd=tesseract_cmd, lang=lang)
    
    # Extract text
    text = converter.extract_text_from_image(image_file, preprocess=preprocess)
    
    if text:
        logger.info(f"Successfully extracted text from image")
    else:
        logger.error(f"Failed to extract text from image")
    
    return text

def generate_pdf(text_content, image_paths=None, title=None, output_path=None):
    """
    Generate a PDF from text content and images.
    
    Args:
        text_content (str or list): Text content or list of text blocks
        image_paths (list): List of image paths
        title (str): Document title
        output_path (str): Output file path
        
    Returns:
        str: Path to the generated PDF
    """
    # Initialize PDF generator
    generator = PDFGenerator()
    
    # Generate PDF
    if isinstance(text_content, list) and image_paths:
        return generator.generate_from_text_and_images(text_content, image_paths, title=title, output_path=output_path)
    elif isinstance(text_content, str):
        return generator.generate_from_text(text_content, title=title, output_path=output_path)
    else:
        logger.error("Invalid text content format")
        return None

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Convert speech and images to text and generate PDF")
    
    # Input options
    parser.add_argument("--audio", help="Path to the audio file")
    parser.add_argument("--image", help="Path to the image file")
    parser.add_argument("--mic", action="store_true", help="Use microphone as input")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds")
    
    # Processing options
    parser.add_argument("--advanced", action="store_true", help="Use advanced speech recognition model")
    parser.add_argument("--tesseract", help="Path to Tesseract executable")
    parser.add_argument("--lang", default="eng", help="Language for OCR")
    parser.add_argument("--no-preprocess", action="store_true", help="Skip image preprocessing")
    
    # Output options
    parser.add_argument("--title", default="Generated PDF", help="Document title")
    parser.add_argument("--output", help="Output PDF file")
    
    args = parser.parse_args()
    
    # Check if at least one input is provided
    if not args.audio and not args.image and not args.mic:
        parser.print_help()
        logger.error("At least one input (audio, image, or microphone) must be provided")
        return 1
    
    # Generate default output path if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"output_{timestamp}.pdf"
    
    # Process audio
    audio_text = None
    if args.mic:
        logger.info("Recording from microphone...")
        converter = SpeechToText(use_advanced_model=args.advanced)
        audio_text = converter.transcribe_from_microphone(duration=args.duration)
    elif args.audio:
        audio_text = process_audio(args.audio, use_advanced_model=args.advanced)
    
    # Process image
    image_text = None
    if args.image:
        image_text = process_image(args.image, tesseract_cmd=args.tesseract, lang=args.lang, preprocess=not args.no_preprocess)
    
    # Combine text
    combined_text = ""
    if audio_text:
        combined_text += "=== Transcribed Audio ===\n\n"
        combined_text += audio_text
        combined_text += "\n\n"
    
    if image_text:
        combined_text += "=== Extracted Text from Image ===\n\n"
        combined_text += image_text
    
    if not combined_text:
        logger.error("No text was extracted from the inputs")
        return 1
    
    # Generate PDF
    if args.image:
        # If we have an image, include it in the PDF
        text_blocks = []
        image_paths = []
        
        if audio_text:
            text_blocks.append("=== Transcribed Audio ===\n\n" + audio_text)
        
        if image_text:
            text_blocks.append("=== Extracted Text from Image ===\n\n" + image_text)
            image_paths.append(args.image)
        
        pdf_path = generate_pdf(text_blocks, image_paths, title=args.title, output_path=args.output)
    else:
        # Text-only PDF
        pdf_path = generate_pdf(combined_text, title=args.title, output_path=args.output)
    
    if pdf_path:
        logger.info(f"PDF generated successfully: {pdf_path}")
        return 0
    else:
        logger.error("Failed to generate PDF")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 