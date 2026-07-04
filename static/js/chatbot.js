// static/js/chatbot.js
document.addEventListener("DOMContentLoaded", function () {
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    if (!sendBtn) return;

    function handleSend() {
        const query = userInput.value.trim();
        if (!query) return;

        // Append user query to chat window
        chatBox.innerHTML += `<p>👤 <strong>You:</strong> ${query}</p>`;
        userInput.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        // Fetch query response
        fetch("/chatbot/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: query })
        })
        .then(r => r.json())
        .then(data => {
            chatBox.innerHTML += `<p style="color: var(--accent-emerald);">🤖 <strong>System Assistant:</strong> ${data.response}</p>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(() => {
            chatBox.innerHTML += `<p style="color: var(--accent-crimson);">⚠️ <strong>Error:</strong> Failed to fetch response.</p>`;
        });
    }

    sendBtn.addEventListener("click", handleSend);
    userInput.addEventListener("keypress", function (e) {
        if (e.key === 'Enter') handleSend();
    });
});