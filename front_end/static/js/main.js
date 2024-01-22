document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    let formData = new FormData();
    formData.append('file', document.getElementById('pdfFile').files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server responded with an error: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('summaryText').textContent = data.summary;
        document.getElementById('summaryBox').classList.remove('hidden');
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
