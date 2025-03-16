// JavaScript for OCR to PDF web app
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const uploadButton = document.getElementById('upload-button');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const resultCard = document.getElementById('result-card');
    const extractedText = document.getElementById('extracted-text');
    const createPdfButton = document.getElementById('create-pdf-button');
    const pdfCard = document.getElementById('pdf-card');
    const pdfMessage = document.getElementById('pdf-message');
    const downloadLink = document.getElementById('download-link');
    const ocrStatus = document.getElementById('ocr-status');
    
    // Check OCR status periodically
    function checkOCRStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                ocrStatus.textContent = data.status;
                ocrStatus.className = data.status === 'ready' ? 'status-ready' : 'status-initializing';
                
                if (data.status === 'initializing') {
                    setTimeout(checkOCRStatus, 2000); // Check again in 2 seconds
                }
            })
            .catch(error => console.error('Error checking OCR status:', error));
    }
    
    // Check immediately on page load
    if (ocrStatus.textContent === 'initializing') {
        checkOCRStatus();
    }
    
    // Drag and drop handling
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    // Handle selected files
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Check if file is an image
            if (!file.type.match('image.*')) {
                alert('Please select an image file');
                return;
            }
            
            fileInfo.textContent = `${file.name} (${formatSize(file.size)})`;
            uploadButton.disabled = false;
        }
    }
    
    // Format file size
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // Handle upload button click
    uploadButton.addEventListener('click', uploadFile);
    
    function uploadFile() {
        const file = fileInput.files[0];
        if (!file) return;
        
        // Prepare FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Show progress
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        uploadButton.disabled = true;
        
        // Create request
        const xhr = new XMLHttpRequest();
        
        // Handle upload progress
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
            }
        });
        
        // Handle response
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Show extracted text
                    extractedText.value = response.text;
                    resultCard.style.display = 'block';
                    
                    // Scroll to result card
                    resultCard.scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('Error: ' + response.error);
                }
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    alert('Error: ' + response.error);
                } catch (e) {
                    alert('Error: ' + xhr.statusText);
                }
            }
            
            // Reset upload form
            progressContainer.style.display = 'none';
            uploadButton.disabled = false;
        });
        
        // Handle errors
        xhr.addEventListener('error', function() {
            alert('Upload failed. Please try again.');
            progressContainer.style.display = 'none';
            uploadButton.disabled = false;
        });
        
        // Send the request
        xhr.open('POST', '/upload');
        xhr.send(formData);
    }
    
    // Handle create PDF button click
    createPdfButton.addEventListener('click', createPDF);
    
    function createPDF() {
        createPdfButton.disabled = true;
        createPdfButton.textContent = 'Creating PDF...';
        
        fetch('/create-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pdfMessage.textContent = data.message;
                downloadLink.href = data.pdf_url;
                pdfCard.style.display = 'block';
                
                // Scroll to PDF card
                pdfCard.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + data.error);
            }
            
            createPdfButton.disabled = false;
            createPdfButton.textContent = 'Create PDF';
        })
        .catch(error => {
            console.error('Error creating PDF:', error);
            alert('Error creating PDF. Please try again.');
            createPdfButton.disabled = false;
            createPdfButton.textContent = 'Create PDF';
        });
    }
});
