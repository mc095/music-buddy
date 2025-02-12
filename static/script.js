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

    

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;

    if (isUser) {
        messageDiv.appendChild(contentDiv);
    } else {
        messageDiv.appendChild(contentDiv);
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return messageDiv;
}

async function sendMessage(message) {
    const chatBox = document.getElementById('chat-messages');

    // Add user message to the chat
    addMessage(message, true);

    // Create a placeholder for the bot message
    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot';
    const botMessageContent = document.createElement('div');
    botMessageContent.className = 'message-content';
    botMessageDiv.appendChild(botMessageContent);
    chatBox.appendChild(botMessageDiv);

    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value);

        // Debug: Log the buffer to see what the API is returning
        console.log("Buffer:", buffer);

        // Check if the response contains a YouTube URL
        const videoUrlMatch = buffer.match(/https:\/\/www\.youtube\.com\/embed\/([a-zA-Z0-9_-]+)/);
        if (videoUrlMatch) {
            const videoUrl = videoUrlMatch[0];
            console.log("YouTube URL detected:", videoUrl); // Debug: Log the detected URL
            appendVideoMessage(videoUrl, botMessageContent);
        } else {
            botMessageContent.innerHTML = buffer;
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

function appendVideoMessage(videoUrl, botMessageContent) {
    videoUrl = "https://www.youtube.com/embed/BY_XwvKogC8?autoplay=1"; // Hardcoded URL for testing
    console.log("Appending video:", videoUrl);

    botMessageContent.innerHTML = '';

    const videoContainer = document.createElement('div');
    videoContainer.style.position = 'relative';
    videoContainer.style.width = '100%';
    videoContainer.style.paddingTop = '56.25%'; // 16:9 Aspect Ratio
    videoContainer.style.backgroundColor = '#000'; // Add a background color for visibility

    const iframe = document.createElement('iframe');
    iframe.style.position = 'absolute';
    iframe.style.top = '0';
    iframe.style.left = '0';
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.src = videoUrl;
    iframe.frameBorder = '0';
    iframe.allow = 'autoplay; encrypted-media';
    iframe.allowFullscreen = true;

    videoContainer.appendChild(iframe);
    botMessageContent.appendChild(videoContainer);

    console.log("Video iframe created:", iframe);
}

function onPlayerReady(event) {
    event.target.playVideo();
}

function onPlayerError(event) {
    botMessageContent.innerHTML = 'Video unavailable. <a href="https://youtu.be/' + videoId + '" target="_blank">Watch on YouTube</a>';
}

// Ensure the YouTube API script is loaded
if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://www.youtube.com/iframe_api';
    script.onload = onYouTubeIframeAPIReady;
    document.body.appendChild(script);
} else {
    // If the API is already loaded, initialize the player immediately
    onYouTubeIframeAPIReady();
}

// Initialize the YouTube API
function onYouTubeIframeAPIReady() {
    window.onYouTubeIframeAPIReady = function () {
        // This function will be called when the API is ready
    };
}