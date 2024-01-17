document.getElementById("send-btn").addEventListener("click", function() {
    let userInput = document.getElementById("user-input").value;
    if (userInput) {
        addToChat(userInput, "user");
        sendToBackend(userInput);
        document.getElementById("user-input").value = ""; // Clear input field
    }
});


document.getElementById("upload-btn").addEventListener("click", function() {
    let fileInput = document.getElementById("pdf-upload");
    let file = fileInput.files[0];
    if (file) {
        uploadPDF(file);
    }
});

document.getElementById("generate-embeddings-btn").addEventListener("click", function() {
    generateEmbeddings();
});

function uploadPDF(file) {
    let formData = new FormData();
    formData.append("pdf", file);

    fetch('http://127.0.0.1:5000/upload_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(error => console.error('Error:', error));
}

function generateEmbeddings() {
    fetch('http://127.0.0.1:5000/generate_embeddings', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(error => console.error('Error:', error));
}

function addToChat(message, sender) {
    let chatBox = document.getElementById("chat-box");
    let messageElement = document.createElement("p");
    messageElement.textContent = message;
    messageElement.className = sender;
    chatBox.appendChild(messageElement);
}

function sendToBackend(message) {
    let apiUrl = 'http://127.0.0.1:5000/api/ask';  // Local Flask server URL

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: message })
    })
    .then(response => response.json())
    .then(data => {
        addToChat(data.reply, "bot");
    })
    .catch(error => console.error('Error:', error));
}


