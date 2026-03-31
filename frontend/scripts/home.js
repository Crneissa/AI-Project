document.querySelector('.upload-btn').addEventListener('click', function() {
    const featuresSection = document.querySelector('.features');
    featuresSection.scrollIntoView({ behavior: 'smooth' });
});

document.addEventListener('DOMContentLoaded', () => {
    const pdfUpload = document.getElementById('pdfUpload');
    const summaryLink = document.getElementById('summary-link');
    const quizLink = document.getElementById('quiz-link');

    summaryLink.addEventListener('click', (event) => {
        event.preventDefault();
        if (confirm('This program will use your camera. Do you want to continue?')) {
            window.location.href = '/summary';
        }
    });

    quizLink.addEventListener('click', (event) => {
        event.preventDefault();
        if (confirm('This program will use your camera. Do you want to continue?')) {
            window.location.href = '/quiz';
        }
    });

    pdfUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('pdf', file);

            fetch('/upload_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                } else {
                    alert("Error uploading PDF.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred.");
            });
        } else {
            alert("Please select a PDF file.");
        }
    });
});