from setuptools import setup, find_packages

setup(
    name="speech_text_image_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition>=3.10.0",
        "pydub>=0.25.1",
        "pytesseract>=0.3.10",
        "Pillow>=10.0.0",
        "fpdf>=1.7.2",
        "numpy>=1.24.3",
        "transformers>=4.30.2",
        "torch>=2.0.1",
        "torchaudio>=2.0.2",
        "opencv-python>=4.8.0.74",
        "pdf2image>=1.16.3",
        "python-docx>=0.8.11",
        "librosa>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "speech2pdf=src.speech_to_text:main",
            "image2pdf=src.image_to_text:main",
            "converter=src.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert speech and images to text and generate PDFs",
    keywords="speech, text, image, OCR, PDF",
    url="https://github.com/yourusername/speech_text_image_converter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 