# import os
# import speech_recognition as sr
# from pydub import AudioSegment
# import torch
# from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
# import numpy as np
# import tempfile
# import logging
# import librosa

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class SpeechToText:
#     def __init__(self, use_advanced_model=False):
#         """
#         Initialize the speech to text converter.
        
#         Args:
#             use_advanced_model (bool): Whether to use the advanced Wav2Vec2 model
#                                       or the basic Google Speech Recognition API.
#         """
#         self.recognizer = sr.Recognizer()
#         self.use_advanced_model = use_advanced_model
        
#         # Load advanced model if requested
#         if use_advanced_model:
#             try:
#                 logger.info("Loading Wav2Vec2 model...")
#                 self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
#                 self.model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
#                 logger.info("Wav2Vec2 model loaded successfully")
#             except Exception as e:
#                 logger.error(f"Failed to load Wav2Vec2 model: {e}")
#                 logger.info("Falling back to basic speech recognition")
#                 self.use_advanced_model = False
    
#     def convert_audio_format(self, audio_file, target_format="wav"):
#         """
#         Convert audio file to the required format.
        
#         Args:
#             audio_file (str): Path to the audio file
#             target_format (str): Target audio format
            
#         Returns:
#             str: Path to the converted audio file
#         """
#         try:
#             # Get the file extension
#             file_extension = os.path.splitext(audio_file)[1][1:].lower()
            
#             # If the file is already in the target format, return it
#             if file_extension == target_format:
#                 return audio_file
                
#             # Create a temporary file for the converted audio
#             temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
#             temp_filename = temp_file.name
#             temp_file.close()
            
#             # Convert the audio file
#             audio = AudioSegment.from_file(audio_file, format=file_extension)
#             audio.export(temp_filename, format=target_format)
            
#             logger.info(f"Converted {audio_file} to {target_format} format")
#             return temp_filename
            
#         except Exception as e:
#             logger.error(f"Error converting audio format: {e}")
#             return audio_file
    
#     def transcribe_with_wav2vec2(self, audio_file):
#         """
#         Transcribe audio using the Wav2Vec2 model.
        
#         Args:
#             audio_file (str): Path to the audio file
            
#         Returns:
#             str: Transcribed text
#         """
#         try:
#             # Convert audio to wav format if needed
#             wav_file = self.convert_audio_format(audio_file, "wav")
            
#             # Load audio
#             audio, _ = librosa.load(wav_file, sr=16000)
            
#             # Process audio
#             input_values = self.processor(
#                 torch.tensor(audio), 
#                 sampling_rate=16000, 
#                 return_tensors="pt"
#             ).input_values
            
#             # Get logits
#             with torch.no_grad():
#                 logits = self.model(input_values).logits
            
#             # Get predicted ids
#             predicted_ids = torch.argmax(logits, dim=-1)
            
#             # Convert ids to text
#             transcription = self.processor.batch_decode(predicted_ids)[0]
            
#             # Clean up temporary file if created
#             if wav_file != audio_file:
#                 os.unlink(wav_file)
                
#             return transcription
            
#         except Exception as e:
#             logger.error(f"Error in Wav2Vec2 transcription: {e}")
#             return None
    
#     def transcribe_with_google(self, audio_file):
#         """
#         Transcribe audio using Google Speech Recognition.
        
#         Args:
#             audio_file (str): Path to the audio file
            
#         Returns:
#             str: Transcribed text
#         """
#         try:
#             # Convert audio to wav format if needed
#             wav_file = self.convert_audio_format(audio_file, "wav")
            
#             # Load the audio file
#             with sr.AudioFile(wav_file) as source:
#                 audio_data = self.recognizer.record(source)
            
#             # Recognize speech using Google Speech Recognition
#             text = self.recognizer.recognize_google(audio_data)
            
#             # Clean up temporary file if created
#             if wav_file != audio_file:
#                 os.unlink(wav_file)
                
#             return text
            
#         except sr.UnknownValueError:
#             logger.warning("Google Speech Recognition could not understand audio")
#             return None
#         except sr.RequestError as e:
#             logger.error(f"Could not request results from Google Speech Recognition service: {e}")
#             return None
#         except Exception as e:
#             logger.error(f"Error in Google transcription: {e}")
#             return None
    
#     def transcribe_from_file(self, audio_file):
#         """
#         Transcribe speech from an audio file.
        
#         Args:
#             audio_file (str): Path to the audio file
            
#         Returns:
#             str: Transcribed text
#         """
#         if not os.path.exists(audio_file):
#             logger.error(f"Audio file not found: {audio_file}")
#             return None
            
#         logger.info(f"Transcribing audio file: {audio_file}")
        
#         if self.use_advanced_model:
#             text = self.transcribe_with_wav2vec2(audio_file)
#             if text is None:
#                 logger.info("Falling back to Google Speech Recognition")
#                 text = self.transcribe_with_google(audio_file)
#         else:
#             text = self.transcribe_with_google(audio_file)
            
#         return text
    
#     def transcribe_from_microphone(self, duration=5):
#         """
#         Transcribe speech from microphone.
        
#         Args:
#             duration (int): Recording duration in seconds
            
#         Returns:
#             str: Transcribed text
#         """
#         try:
#             logger.info(f"Recording audio for {duration} seconds...")
            
#             with sr.Microphone() as source:
#                 self.recognizer.adjust_for_ambient_noise(source)
#                 audio = self.recognizer.listen(source, timeout=duration)
            
#             logger.info("Recording complete, transcribing...")
            
#             if self.use_advanced_model:
#                 # Save audio to a temporary file
#                 temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#                 temp_filename = temp_file.name
#                 temp_file.close()
                
#                 with open(temp_filename, "wb") as f:
#                     f.write(audio.get_wav_data())
                
#                 text = self.transcribe_with_wav2vec2(temp_filename)
#                 os.unlink(temp_filename)
                
#                 if text is None:
#                     logger.info("Falling back to Google Speech Recognition")
#                     text = self.recognizer.recognize_google(audio)
#             else:
#                 text = self.recognizer.recognize_google(audio)
                
#             return text
            
#         except sr.UnknownValueError:
#             logger.warning("Google Speech Recognition could not understand audio")
#             return None
#         except sr.RequestError as e:
#             logger.error(f"Could not request results from Google Speech Recognition service: {e}")
#             return None
#         except Exception as e:
#             logger.error(f"Error in microphone transcription: {e}")
#             return None


# # Example usage
# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Convert speech to text")
#     parser.add_argument("--input", help="Path to the audio file")
#     parser.add_argument("--advanced", action="store_true", help="Use advanced model")
#     parser.add_argument("--mic", action="store_true", help="Use microphone as input")
#     parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds")
    
#     args = parser.parse_args()
    
#     converter = SpeechToText(use_advanced_model=args.advanced)
    
#     if args.mic:
#         text = converter.transcribe_from_microphone(duration=args.duration)
#     elif args.input:
#         text = converter.transcribe_from_file(args.input)
#     else:
#         parser.print_help()
#         exit(1)
    
#     if text:
#         print(f"Transcribed text: {text}")
#     else:
#         print("Transcription failed") 


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OCR to PDF Converter - All-in-One File
--------------------------------------
This single file contains all functionality of the OCR to PDF Converter application,
including OCR processing, PDF creation, GUI interface, CLI interface, and batch file generation.

Dependencies:
- easyocr==1.7.0
- numpy==1.24.3
- Pillow==10.0.0
- PyPDF2==3.0.1
- reportlab==3.6.13
- python-doctr==0.7.0
- tqdm==4.66.1

Usage:
1. Command line mode:
   python ocr_to_pdf_all_in_one.py --cli --image <path_to_image> --output <output_pdf_path> [--existing-pdf <existing_pdf_path>]

2. GUI mode:
   python ocr_to_pdf_all_in_one.py
   or
   python ocr_to_pdf_all_in_one.py --gui

3. Create batch file for easy launching:
   python ocr_to_pdf_all_in_one.py --create-batch

4. Check and install dependencies:
   python ocr_to_pdf_all_in_one.py --install-deps
"""

import os
import sys
import argparse
import threading
import subprocess
import platform
import importlib.util
from pathlib import Path

# Function to check if a package is installed
def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

# Define required packages
REQUIRED_PACKAGES = [
    "easyocr==1.7.0",
    "numpy==1.24.3", 
    "Pillow==10.0.0", 
    "PyPDF2==3.0.1", 
    "reportlab==3.6.13", 
    "python-doctr==0.7.0", 
    "tqdm==4.66.1"
]

# Check for missing packages
def check_missing_packages():
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        package_name = package.split('==')[0].lower()
        if not is_package_installed(package_name):
            missing_packages.append(package)
    return missing_packages

# Install missing packages if needed
def install_dependencies():
    missing_packages = check_missing_packages()
    
    if not missing_packages:
        print("All required packages are already installed.")
        return True
    
    print(f"The following packages need to be installed: {', '.join(missing_packages)}")
    try:
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("All dependencies installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        print("Please install the required packages manually using:")
        print("pip install -r requirements.txt")
        return False

# Create requirements.txt file
def create_requirements_file():
    try:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(REQUIRED_PACKAGES))
        print("requirements.txt file created successfully.")
        return True
    except Exception as e:
        print(f"Error creating requirements.txt file: {str(e)}")
        return False

# Create batch file for easy launching on Windows
def create_batch_file():
    if platform.system() != "Windows":
        print("Batch file creation is only available on Windows.")
        return False
    
    try:
        script_path = os.path.abspath(__file__)
        venv_python = sys.executable
        
        batch_content = f"""@echo off
echo Starting OCR to PDF Converter...
"{venv_python}" "{script_path}"
if %ERRORLEVEL% NEQ 0 (
    echo An error occurred. Please check if all dependencies are installed.
    echo You can install dependencies by running: python "{script_path}" --install-deps
    pause
)
"""
        
        with open("run_ocr_app.bat", "w") as f:
            f.write(batch_content)
        
        print("Batch file created successfully: run_ocr_app.bat")
        print("You can now run the application by double-clicking on run_ocr_app.bat")
        return True
    except Exception as e:
        print(f"Error creating batch file: {str(e)}")
        return False

# Import required packages for OCR and GUI functionality
try:
    import easyocr
    import PyPDF2
    from PIL import Image
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from tqdm import tqdm

    # Check if GUI dependencies are installed
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
        from PIL import ImageTk
        GUI_AVAILABLE = True
    except ImportError:
        GUI_AVAILABLE = False

except ImportError:
    # If imports fail, notify the user but continue to allow dependency installation
    print("Some required packages are missing. Use --install-deps to install them.")
    GUI_AVAILABLE = False


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


class OCRtoPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR to PDF Converter")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Initialize OCR processor in a background thread
        self.ocr_processor = None
        self.init_thread = threading.Thread(target=self.initialize_ocr)
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # Variables
        self.image_path = tk.StringVar()
        self.existing_pdf_path = tk.StringVar()
        self.output_pdf_path = tk.StringVar()
        self.use_existing_pdf = tk.BooleanVar(value=False)
        self.status_text = tk.StringVar(value="Initializing OCR engine...")
        
        self.setup_ui()
    
    def initialize_ocr(self):
        """Initialize OCR engine in background thread"""
        try:
            self.ocr_processor = OCRtoPDF()
            self.status_text.set("Ready")
        except Exception as e:
            self.status_text.set(f"Error initializing OCR: {str(e)}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image selection
        ttk.Label(main_frame, text="Select Image File:").grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Entry(main_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, pady=10)
        ttk.Button(main_frame, text="Browse...", command=self.browse_image).grid(row=0, column=2, padx=5, pady=10)
        
        # Image preview frame
        self.preview_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="10")
        self.preview_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # PDF Options frame
        pdf_options_frame = ttk.LabelFrame(main_frame, text="PDF Options", padding="10")
        pdf_options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Option to use existing PDF
        ttk.Checkbutton(
            pdf_options_frame, 
            text="Add text to existing PDF", 
            variable=self.use_existing_pdf,
            command=self.toggle_existing_pdf
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Existing PDF selection (initially disabled)
        self.existing_pdf_label = ttk.Label(pdf_options_frame, text="Select Existing PDF:")
        self.existing_pdf_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.existing_pdf_label.state(['disabled'])
        
        self.existing_pdf_entry = ttk.Entry(pdf_options_frame, textvariable=self.existing_pdf_path, width=50)
        self.existing_pdf_entry.grid(row=1, column=1, pady=5)
        self.existing_pdf_entry.state(['disabled'])
        
        self.existing_pdf_button = ttk.Button(pdf_options_frame, text="Browse...", command=self.browse_existing_pdf)
        self.existing_pdf_button.grid(row=1, column=2, padx=5, pady=5)
        self.existing_pdf_button.state(['disabled'])
        
        # Output PDF selection
        ttk.Label(pdf_options_frame, text="Output PDF Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(pdf_options_frame, textvariable=self.output_pdf_path, width=50).grid(row=2, column=1, pady=5)
        ttk.Button(pdf_options_frame, text="Browse...", command=self.browse_output_pdf).grid(row=2, column=2, padx=5, pady=5)
        
        # Process button
        ttk.Button(main_frame, text="Extract Text and Create PDF", command=self.process_image).grid(
            row=3, column=0, columnspan=3, pady=20
        )
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def toggle_existing_pdf(self):
        """Enable or disable existing PDF options based on checkbox"""
        if self.use_existing_pdf.get():
            self.existing_pdf_label.state(['!disabled'])
            self.existing_pdf_entry.state(['!disabled'])
            self.existing_pdf_button.state(['!disabled'])
        else:
            self.existing_pdf_label.state(['disabled'])
            self.existing_pdf_entry.state(['disabled'])
            self.existing_pdf_button.state(['disabled'])
    
    def browse_image(self):
        """Browse for an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=(
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            )
        )
        if file_path:
            self.image_path.set(file_path)
            self.load_image_preview(file_path)
    
    def browse_existing_pdf(self):
        """Browse for an existing PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select Existing PDF",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            )
        )
        if file_path:
            self.existing_pdf_path.set(file_path)
    
    def browse_output_pdf(self):
        """Browse for output PDF location"""
        file_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            )
        )
        if file_path:
            self.output_pdf_path.set(file_path)
    
    def load_image_preview(self, image_path):
        """Load and display image preview"""
        try:
            # Open image and resize for preview
            image = Image.open(image_path)
            
            # Calculate resize ratio to fit within preview frame
            max_width = 600
            max_height = 300
            width, height = image.size
            
            # Calculate new dimensions while preserving aspect ratio
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Display image
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image preview: {str(e)}")
    
    def process_image(self):
        """Process the image and create PDF"""
        # Validate inputs
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file.")
            return
        
        if not os.path.exists(self.image_path.get()):
            messagebox.showerror("Error", "The selected image file does not exist.")
            return
        
        if self.use_existing_pdf.get() and not os.path.exists(self.existing_pdf_path.get()):
            messagebox.showerror("Error", "The selected existing PDF file does not exist.")
            return
        
        if not self.output_pdf_path.get():
            messagebox.showerror("Error", "Please specify an output PDF path.")
            return
        
        # Make sure OCR engine is initialized
        if self.ocr_processor is None:
            messagebox.showerror("Error", "OCR engine is not initialized yet. Please wait.")
            return
        
        # Start processing in a separate thread
        self.progress.start()
        self.status_text.set("Processing image...")
        
        processing_thread = threading.Thread(target=self.run_processing)
        processing_thread.daemon = True
        processing_thread.start()
    
    def run_processing(self):
        """Run the OCR and PDF processing in a background thread"""
        try:
            # Extract text from image
            extracted_text = self.ocr_processor.extract_text_from_image(self.image_path.get())
            
            if not extracted_text:
                self.root.after(0, lambda: messagebox.showerror("Error", "No text was extracted from the image."))
                self.root.after(0, lambda: self.status_text.set("Failed: No text extracted"))
                self.root.after(0, self.progress.stop)
                return
            
            # Process PDF based on user choice
            if self.use_existing_pdf.get():
                success = self.ocr_processor.add_text_to_existing_pdf(
                    extracted_text, self.existing_pdf_path.get(), self.output_pdf_path.get()
                )
            else:
                success = self.ocr_processor.create_new_pdf(extracted_text, self.output_pdf_path.get())
            
            # Update UI with results
            if success:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Text extracted and saved to PDF successfully!\nOutput saved to: {self.output_pdf_path.get()}"
                ))
                self.root.after(0, lambda: self.status_text.set("Ready"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to create PDF."))
                self.root.after(0, lambda: self.status_text.set("Failed: PDF creation error"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)


def run_cli():
    """Run the command-line interface"""
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


def run_gui():
    """Run the GUI application"""
    if not GUI_AVAILABLE:
        print("Error: GUI dependencies (tkinter) are not installed.")
        print("Please install tkinter to use the GUI mode.")
        print("You can still use the command-line mode with --cli option.")
        sys.exit(1)
        
    root = tk.Tk()
    app = OCRtoPDFApp(root)
    root.mainloop()


def main():
    """Main entry point for the application"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='OCR to PDF Converter - All-in-One')
    parser.add_argument('--cli', action='store_true', help='Run in command-line interface mode')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode (default)')
    parser.add_argument('--create-batch', action='store_true', help='Create a batch file for easy launching')
    parser.add_argument('--install-deps', action='store_true', help='Check and install dependencies')
    parser.add_argument('--create-requirements', action='store_true', help='Create requirements.txt file')
    
    # Parse only known args to handle special commands
    args, unprocessed_args = parser.parse_known_args()
    
    # Handle special commands first
    if args.install_deps:
        install_dependencies()
        return
    
    if args.create_requirements:
        create_requirements_file()
        return
    
    if args.create_batch:
        create_batch_file()
        return
    
    # Missing packages check
    missing_packages = check_missing_packages()
    if missing_packages:
        print("Warning: Some required packages are missing. Use --install-deps to install them.")
        print(f"Missing: {', '.join(missing_packages)}")
    
    # Default to GUI mode unless CLI is specified
    if args.cli:
        # Restore unprocessed args for CLI parser
        sys.argv = [sys.argv[0]] + unprocessed_args
        run_cli()
    else:
        # GUI mode (default)
        run_gui()


if __name__ == "__main__":
    main() 