# Speech and Image to PDF Converter

This application uses machine learning to:
1. Convert speech to text
2. Extract text from images
3. Generate PDF documents from the extracted text

## Features

- **Speech Recognition**: Converts audio files or microphone input to text
- **OCR (Optical Character Recognition)**: Extracts text from images
- **PDF Generation**: Creates PDF documents from the extracted text

## Requirements

- Python 3.8+
- Tesseract OCR engine (for image text extraction)
- FFmpeg (for audio processing)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/speech_text_image_converter.git
cd speech_text_image_converter
```

2. Install the required Python packages:
```
pip install -r requirements.txt
```

3. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

4. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

## Usage

### Speech to PDF
```
python src/speech_to_pdf.py --input audio_file.mp3 --output output.pdf
```

### Image to PDF
```
python src/image_to_pdf.py --input image_file.jpg --output output.pdf
```

### Combined Conversion
```
python src/main.py --audio audio_file.mp3 --image image_file.jpg --output output.pdf
```

## License

MIT 