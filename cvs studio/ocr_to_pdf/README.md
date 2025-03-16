# OCR to PDF Converter

This application extracts text from images using Optical Character Recognition (OCR) and adds the extracted text to either a new PDF or an existing PDF file.

## Features

- Extract text from various image formats (JPG, PNG, BMP, TIFF)
- Create a new PDF document with the extracted text
- Add extracted text to an existing PDF document
- User-friendly GUI interface
- Command-line interface for automation

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

This will install the necessary packages including:
- EasyOCR for text extraction
- PyPDF2 for PDF manipulation
- ReportLab for PDF creation
- Pillow for image processing
- Tkinter for the GUI (usually comes with Python)

## Usage

### GUI Application

To run the GUI application:

```bash
python gui_app.py
```

The GUI provides the following options:
1. Select an image containing text
2. Preview the selected image
3. Choose to create a new PDF or add text to an existing PDF
4. Specify the output PDF path
5. Process the image and create/update the PDF

### Command Line Interface

For batch processing or automation, you can use the command-line interface:

```bash
python main.py --image <path_to_image> --output <output_pdf_path> [--existing-pdf <existing_pdf_path>]
```

Arguments:
- `--image`: Path to the image file (required)
- `--output`: Path for the output PDF file (required)
- `--existing-pdf`: Path to an existing PDF file (optional)

## Examples

### Extract text from an image and create a new PDF

```bash
python main.py --image sample.jpg --output extracted_text.pdf
```

### Extract text from an image and add it to an existing PDF

```bash
python main.py --image sample.jpg --output updated_document.pdf --existing-pdf original_document.pdf
```

## How It Works

1. The application uses EasyOCR, a deep learning-based OCR engine, to extract text from images
2. The extracted text is then formatted and processed
3. Depending on user choice:
   - A new PDF is created with the extracted text using ReportLab
   - The text is added to an existing PDF using PyPDF2

## Limitations

- OCR accuracy depends on image quality, text clarity, and font
- Complex layouts may not be preserved in the output PDF
- Currently supports English text extraction (additional languages can be added)

## License

This project is open-source and available under the MIT License.

## Acknowledgements

This application uses the following open-source libraries:
- EasyOCR
- PyPDF2
- ReportLab
- PIL/Pillow
- Tkinter 