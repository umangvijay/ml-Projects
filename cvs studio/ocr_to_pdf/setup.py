from setuptools import setup, find_packages

setup(
    name="ocr_to_pdf",
    version="1.0.0",
    description="Extract text from images and add to PDFs using OCR",
    author="OCR to PDF Team",
    packages=find_packages(),
    install_requires=[
        "easyocr>=1.7.0",
        "numpy>=1.24.3",
        "Pillow>=10.0.0",
        "PyPDF2>=3.0.1",
        "reportlab>=3.6.13",
        "python-doctr>=0.7.0",
        "tqdm>=4.66.1",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ocr-to-pdf-cli=main:main",
            "ocr-to-pdf-gui=gui_app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 