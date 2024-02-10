document.getElementById('askButton').addEventListener('click', function() {
    const userQuery = document.getElementById('userQuery').value;
    fetchResponse(userQuery);
});

async function fetchResponse(query) {
    const responseElement = document.getElementById('response');
    try {
        const result = await fetch('https://api.openai.com/v1/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_OPENAI_API_KEY'
            },
            body: JSON.stringify({
                model: "text-davinci-003",
                prompt: "Provide information on what to do before, during, and after attending a sports event at Fenway Park. " + query,
                temperature: 0.5,
                max_tokens: 100,
                top_p: 1.0,
                frequency_penalty: 0.0,
                presence_penalty: 0.0
            })
        });
        const data = await result.json();
        responseElement.textContent = data.choices[0].text.trim();
    } catch (error) {
        responseElement.textContent = 'Failed to fetch response: ' + error.message;
    }
}
