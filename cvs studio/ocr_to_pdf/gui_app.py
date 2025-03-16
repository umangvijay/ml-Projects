import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
from main import OCRtoPDF

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


def main():
    """Entry point for the GUI application"""
    root = tk.Tk()
    app = OCRtoPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 