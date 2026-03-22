let socket = null;
let username = "";

// 🔥 CONNECT FUNCTION
window.connect = function () {
    const usernameInput = document.getElementById("username").value.trim();
    
    if (!usernameInput) {
        alert("Enter username");
        return;
    }
    
    // Store globally for other functions to use
    username = usernameInput.toLowerCase();

    // Close old connection if exists before starting a new one
    if (socket) {
        socket.close();
    }

    console.log("Connecting as:", username);
    socket = new WebSocket(`ws://127.0.0.1:8000/ws/${username}`);

    socket.onopen = () => {
        console.log("✅ Connected");
        loadOnlineUsers();
    };

    socket.onerror = (err) => {
        console.error("❌ WebSocket Error:", err);
    };

    socket.onclose = () => {
        console.log("⚠️ Connection closed");
    };

    // ✅ RECEIVE MESSAGES
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Handle typing indicator
        if (data.type === "typing") {
            const typingDiv = document.getElementById("typing");
            typingDiv.innerText = `${data.sender} is typing...`;
            
            // Clear indicator after 1 second of no updates
            clearTimeout(typingDiv.timeout);
            typingDiv.timeout = setTimeout(() => {
                typingDiv.innerText = "";
            }, 1000);
            return;
        }

        // Handle incoming chat messages
        appendMessage(data.sender, data.content);
    };
};

// 🔥 SEND MESSAGE FUNCTION
window.sendMessage = function () {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert("Connect first!");
        return;
    }

    const receiver = document.getElementById("receiver").value.trim().toLowerCase();
    const messageInput = document.getElementById("message");
    const content = messageInput.value.trim();

    if (!receiver || !content) {
        alert("Enter receiver and message");
        return;
    }

    const msg = {
        sender: username,
        receiver: receiver,
        content: content
    };

    socket.send(JSON.stringify(msg));

    // Show own message in UI
    appendMessage("You", content);

    // Clear input
    messageInput.value = "";
};

// 🔥 HELPER: APPEND TO CHAT
function appendMessage(sender, content) {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<p><b>${sender}:</b> ${content}</p>`;
    chat.scrollTop = chat.scrollHeight;
}

// 🔥 LOAD ONLINE USERS
function loadOnlineUsers() {
    fetch("http://127.0.0.1:8000/online-users")
        .then(res => res.json())
        .then(data => {
            document.getElementById("users").innerText =
                "Online: " + (data.online_users ? data.online_users.join(", ") : "None");
        })
        .catch(err => console.error("Fetch Error:", err));
}

// 🔥 TYPING INDICATOR EVENT
document.getElementById("message").addEventListener("input", () => {
    const receiver = document.getElementById("receiver").value.trim();
    
    if (!socket || socket.readyState !== WebSocket.OPEN || !receiver) return;

    socket.send(JSON.stringify({
        type: "typing",
        sender: username,
        receiver: receiver.toLowerCase()
    }));
});