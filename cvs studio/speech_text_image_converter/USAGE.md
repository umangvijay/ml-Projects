# Speech and Image to PDF Converter - Usage Guide

This guide explains how to use the Speech and Image to PDF Converter application.

## Prerequisites

Before using the application, make sure you have installed:

1. Python 3.8 or higher
2. Tesseract OCR (for image text extraction)
3. FFmpeg (for audio processing)
4. All required Python packages (see README.md for installation instructions)

## Command Line Usage

### Converting Speech to PDF

To convert an audio file to PDF:

```bash
python src/main.py --audio path/to/audio_file.mp3 --output output.pdf
```

To record from microphone and convert to PDF:

```bash
python src/main.py --mic --duration 10 --output output.pdf
```

### Converting Image to PDF

To extract text from an image and create a PDF:

```bash
python src/main.py --image path/to/image_file.jpg --output output.pdf
```

### Combined Conversion

To process both audio and image:

```bash
python src/main.py --audio path/to/audio_file.mp3 --image path/to/image_file.jpg --output output.pdf
```

## Advanced Options

### Speech Recognition

- `--advanced`: Use the advanced Wav2Vec2 model for speech recognition (more accurate but slower)
- `--duration`: Recording duration in seconds when using microphone input (default: 5)

### Image Processing

- `--tesseract`: Path to Tesseract executable (if not in PATH)
- `--lang`: Language for OCR (default: eng)
- `--no-preprocess`: Skip image preprocessing (faster but may be less accurate)

### Output Options

- `--title`: Document title (default: "Generated PDF")

## Programmatic Usage

You can also use the application programmatically in your Python code:

```python
from src.speech_to_text import SpeechToText
from src.image_to_text import ImageToText
from src.pdf_generator import PDFGenerator

# Convert speech to text
speech_converter = SpeechToText()
text = speech_converter.transcribe_from_file("audio.mp3")

# Extract text from image
image_converter = ImageToText()
image_text = image_converter.extract_text_from_image("image.jpg")

# Generate PDF
generator = PDFGenerator()
generator.generate_from_text(text, title="My Document", output_path="output.pdf")
```

See the `examples` directory for more detailed examples.

## Troubleshooting

### Speech Recognition Issues

- Make sure FFmpeg is installed and in your PATH
- Check that your audio file is in a supported format (MP3, WAV, etc.)
- Try using the `--advanced` option for better accuracy

### Image Text Extraction Issues

- Make sure Tesseract OCR is installed and in your PATH
- Check that your image is clear and has good contrast
- Try different preprocessing options
- Use the `--lang` option if your text is not in English

### PDF Generation Issues

- Make sure you have write permissions for the output directory
- Check that the text was successfully extracted from the input 