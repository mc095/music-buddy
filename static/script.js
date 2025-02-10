const messagesContainer = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');

const waveBars = document.querySelectorAll('.wave-bar');
waveBars.forEach(bar => {
    bar.style.animationDuration = `${0.8 + Math.random() * 0.5}s`;
});


userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

userInput.addEventListener('keydown', async function (e) {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            return;
        }
        e.preventDefault();

        const message = this.value.trim();
        if (message) {
            await sendMessage(message);
            this.value = '';
            this.style.height = 'auto';
        }
    }
});


function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

    const profilePic = document.createElement('img');
    profilePic.className = 'profile-pic';
    profilePic.src = isUser ? '/api/placeholder/36/36' : document.getElementById('bot-profile').src;
    profilePic.alt = isUser ? 'User' : 'AI Assistant';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    if (isUser) {
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(profilePic);
    } else {
        messageDiv.appendChild(profilePic);
        messageDiv.appendChild(contentDiv);
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return messageDiv;
}

async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    const chatBox = document.getElementById('chat-messages');


    chatBox.innerHTML += `<div class="message user"><div class="message-content">${userInput}</div></div>`;

    document.getElementById('user-input').value = "";

    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot';
    const botMessageContent = document.createElement('div');
    botMessageContent.className = 'message-content';
    botMessageDiv.appendChild(botMessageContent);
    chatBox.appendChild(botMessageDiv);

    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value);
        botMessageContent.innerHTML = buffer;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}