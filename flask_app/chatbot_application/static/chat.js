function sendMessage() {
    const inputField = document.getElementById('user-input');
    const message = inputField.value.trim();
    if (message) {
        displayMessage(message, 'user');

        inputField.value = ''; // Clear input field

         fetch('/sendMessage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({message: message}),
        })
        .then(response => response.json())
        .then(data => {
            // Display the response message
            displayMessage(data.response, 'bot');
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
}

var userText = document.getElementById("user-input");

userText.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {  //checks whether the pressed key is "Enter"
        sendMessage();
    }
});




function displayMessage(message, sender) {
    const chatBox = document.getElementById('chatbox');
    const msgDiv = document.createElement('div');
    if (sender == "bot"){
    msgDiv.innerHTML = `<img src="static/bot.png" alt="bot" style="width: 20px; height: 20px; vertical-align: middle; margin-right: 5px;"> <b> eMentalHealth.ca Chatbot: </b>` + message;
    }
    else{
        msgDiv.innerHTML = "<b> You: </b>"  + message;
    }

    msgDiv.className = sender+"-message"; // Use this class to style messages differently based on the sender

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message
}

displayMessage("How can I help?", "bot");