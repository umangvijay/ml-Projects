import os
import sys
import argparse

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.speech_to_text import SpeechToText
from src.image_to_text import ImageToText
from src.pdf_generator import PDFGenerator

def example_speech_to_pdf(audio_file, output_file):
    """
    Example of converting speech to PDF.
    
    Args:
        audio_file (str): Path to the audio file
        output_file (str): Path to the output PDF file
    """
    print(f"Converting speech to PDF: {audio_file} -> {output_file}")
    
    # Initialize speech to text converter
    converter = SpeechToText()
    
    # Extract text
    text = converter.transcribe_from_file(audio_file)
    
    if text:
        print(f"Extracted text: {text[:100]}...")
        
        # Initialize PDF generator
        generator = PDFGenerator()
        
        # Generate PDF
        generator.generate_from_text(text, title="Speech to PDF Example", output_path=output_file)
        
        print(f"PDF generated: {output_file}")
    else:
        print("Failed to extract text from audio")

def example_image_to_pdf(image_file, output_file):
    """
    Example of converting image to PDF.
    
    Args:
        image_file (str): Path to the image file
        output_file (str): Path to the output PDF file
    """
    print(f"Converting image to PDF: {image_file} -> {output_file}")
    
    # Initialize image to text converter
    converter = ImageToText()
    
    # Extract text
    text = converter.extract_text_from_image(image_file)
    
    if text:
        print(f"Extracted text: {text[:100]}...")
        
        # Initialize PDF generator
        generator = PDFGenerator()
        
        # Generate PDF with text and image
        generator.generate_from_text_and_images([text], [image_file], title="Image to PDF Example", output_path=output_file)
        
        print(f"PDF generated: {output_file}")
    else:
        print("Failed to extract text from image")

def example_combined(audio_file, image_file, output_file):
    """
    Example of combining speech and image in a PDF.
    
    Args:
        audio_file (str): Path to the audio file
        image_file (str): Path to the image file
        output_file (str): Path to the output PDF file
    """
    print(f"Converting speech and image to PDF: {audio_file}, {image_file} -> {output_file}")
    
    # Initialize converters
    speech_converter = SpeechToText()
    image_converter = ImageToText()
    
    # Extract text from audio
    audio_text = speech_converter.transcribe_from_file(audio_file)
    
    # Extract text from image
    image_text = image_converter.extract_text_from_image(image_file)
    
    if audio_text or image_text:
        # Initialize PDF generator
        generator = PDFGenerator()
        
        # Prepare text blocks and images
        text_blocks = []
        image_paths = []
        
        if audio_text:
            text_blocks.append("=== Transcribed Audio ===\n\n" + audio_text)
        
        if image_text:
            text_blocks.append("=== Extracted Text from Image ===\n\n" + image_text)
            image_paths.append(image_file)
        
        # Generate PDF
        generator.generate_from_text_and_images(text_blocks, image_paths, title="Combined Example", output_path=output_file)
        
        print(f"PDF generated: {output_file}")
    else:
        print("Failed to extract text from inputs")

def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Example usage of the speech and image to PDF converter")
    parser.add_argument("--example", choices=["speech", "image", "combined"], required=True, help="Example to run")
    parser.add_argument("--audio", help="Path to the audio file")
    parser.add_argument("--image", help="Path to the image file")
    parser.add_argument("--output", required=True, help="Output PDF file")
    
    args = parser.parse_args()
    
    if args.example == "speech":
        if not args.audio:
            print("Audio file is required for speech example")
            return 1
        example_speech_to_pdf(args.audio, args.output)
    elif args.example == "image":
        if not args.image:
            print("Image file is required for image example")
            return 1
        example_image_to_pdf(args.image, args.output)
    elif args.example == "combined":
        if not args.audio or not args.image:
            print("Both audio and image files are required for combined example")
            return 1
        example_combined(args.audio, args.image, args.output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 