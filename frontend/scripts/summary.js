function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        const chatContainer = document.querySelector(".chat-container");
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    });
}

function playStrikeAudio(audioFile) {
    console.log("playing strike audio");
    const audio = new Audio(`/static/audio_cache/${audioFile}`);
    audio.addEventListener("loadeddata", () => {
        console.log("Audio loaded:", audioFile);
        audio.play().then(() => {
            console.log("Audio playback started successfully.");
        }).catch(error => {
            console.error("Error playing audio:", error);
        });
    });
    audio.addEventListener("error", (error) => {
        console.error("Error loading audio:", audioFile, error);
    });
}

// Initialize lastStrikeCount from sessionStorage or set it to 0
let lastStrikeCount = parseInt(sessionStorage.getItem("lastStrikeCount")) || 0;

function checkForStrikes(userId) {
    fetch(`/strike/${userId}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success" && data.strikes > 0) {
            if (data.strikes > lastStrikeCount) {
                console.log(`New strike detected: ${data.strikes} strikes.`);
                playStrikeAudio(data.audio_file);
                lastStrikeCount = data.strikes; // Update the last strike count
                sessionStorage.setItem("lastStrikeCount", lastStrikeCount); // Persist in sessionStorage
            } else {
                console.log("No new strikes detected.");
            }
        } else {
            console.log("No strikes detected.");
        }
    })
    .catch(error => {
        console.error("Error checking for strikes:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const resultsDiv = document.getElementById("results");
    const title = document.querySelector('.title');
    const container = document.querySelector('.container');
    const inputContainer = document.querySelector('.input-container');
    let pdfData = null;
    let userId;

    // Request permission to play audio
    const audio = new Audio();
    audio.play().then(() => {
        console.log("Audio playback allowed by browser.");
    }).catch(error => {
        console.error("Autoplay blocked by browser:", error);
    });

    // Fetch user ID
    fetch('/get_user_id')
        .then(response => response.json())
        .then(data => {
            userId = data.user_id;
            console.log("User ID:", userId);

            // Fetch the current strike count from the backend
            fetch(`/strike/${userId}`, {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success" && data.strikes > 0) {
                    lastStrikeCount = data.strikes; // Initialize lastStrikeCount with the current strike count
                    sessionStorage.setItem("lastStrikeCount", lastStrikeCount); // Persist in sessionStorage
                }
            })
            .catch(error => {
                console.error("Error fetching current strike count:", error);
            });

            // Start polling for strikes every 5 seconds
            setInterval(() => {
                checkForStrikes(userId);
            }, 5000); // Check every 5 seconds
        });

    // Fetch PDF data
    fetch('/get_pdf_data')
        .then(response => response.json())
        .then(data => {
            if (data.pdf_data) {
                pdfData = data.pdf_data;
            } else {
                resultsDiv.innerHTML = `<div class="message">Please upload a PDF on the home page.</div>`;
                return;
            }
        })
        .catch(error => {
            console.error("Error fetching PDF data:", error);
            resultsDiv.innerHTML = `<div class="message">An error occurred fetching PDF data.</div>`;
            return;
        });

    // Handle message input
    document.querySelector(".send-btn").addEventListener("click", function () {
        const message = document.getElementById("messageInput").value;
        if (message && pdfData) {
            resultsDiv.innerHTML += `<div class="message user-message">${message}</div>`;
            scrollToBottom();

            document.getElementById("messageInput").value = "";

            if (resultsDiv.children.length === 1) {
                title.style.display = 'none';
                container.style.justifyContent = 'flex-end';
                inputContainer.classList.add('fixed');
            }

            fetch('/ask_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: message, pdf_data: pdfData }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.answer) {
                    let formattedAnswer = data.answer;

                    formattedAnswer = formattedAnswer.replace(/\*(.*?)\*/g, "<strong>$1</strong>");
                    formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
                    formattedAnswer = formattedAnswer.replace(/\* (.*?)\n/g, "<ul><li>$1</li></ul>");
                    formattedAnswer = formattedAnswer.replace(/\d+\. (.*?)\n/g, "<ol><li>$1</li></ol>");

                    resultsDiv.innerHTML += `<div class="message bot-message">${formattedAnswer}</div>`;
                    scrollToBottom();
                } else {
                    resultsDiv.innerHTML += `<div class="message">There was an error getting an answer.</div>`;
                }
            })
            .catch(error => {
                console.error("Error asking question:", error);
                resultsDiv.innerHTML += `<div class="message">An error occurred asking the question.</div>`;
            });
        }
    });

    // Handle message input height
    const messageInput = document.getElementById("messageInput");
    messageInput.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    // Handle Enter key press
    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            document.querySelector(".send-btn").click();
        }
    });

    const homeLink = document.querySelector('a[onclick="location.href=\'/home\'"]'); // Modified selector

    if (homeLink) {
        homeLink.addEventListener('click', (event) => {
            event.preventDefault();

            fetch('/stop_eye_tracker', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Eye tracker stopped.');
                    window.location.href = '/home'; // Redirect to /home
                } else {
                    console.error('Failed to stop eye tracker:', data.message);
                    window.location.href = '/home'; // Redirect even on error
                }
            })
            .catch(error => {
                console.error('Error stopping eye tracker:', error);
                window.location.href = '/home'; // Redirect even on error
            });
        });
    }
});