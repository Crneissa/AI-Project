function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
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

document.addEventListener("DOMContentLoaded", () => {
    const numQuestionsInput = document.getElementById("num-questions");
    const startQuizButton = document.getElementById("start-quiz");
    const quizPrompt = document.getElementById("quiz-prompt");
    const quizContent = document.getElementById("quiz-content");
    const questionText = document.getElementById("question-text");
    const optionsContainer = document.getElementById("options-container");
    const progressBar = document.getElementById("progress-bar");
    const prevButton = document.getElementById("prev-question");
    const nextButton = document.getElementById("next-question");

    let questions = [];
    let currentQuestion = 0;
    let userAnswers = [];

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

    startQuizButton.addEventListener("click", () => {
        const numQuestions = parseInt(numQuestionsInput.value, 10);
        if (isNaN(numQuestions) || numQuestions <= 0) {
            alert("Please enter a valid number of questions.");
            return;
        }

        fetch('/generate_quiz?num_questions=' + numQuestions)
            .then(response => response.json())
            .then(data => {
                console.log("Data Received:", data);

                if (data.error) {
                    alert(data.error);
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                    return;
                } else if (data.questions) {
                    questions = data.questions;
                    currentQuestion = 0;
                    userAnswers = new Array(questions.length).fill(null);
                    showQuestion(currentQuestion);

                    quizPrompt.style.display = "none";
                    quizContent.style.display = "block";
                    progressBar.parentNode.style.display = "block";
                    prevButton.parentNode.style.display = "flex";
                } else {
                    alert("Invalid JSON: 'questions' key missing or not a list");
                }
            })
            .catch(error => {
                console.error("Error fetching quiz questions:", error);
                alert("An error occurred while generating the quiz.");
            });
    });

    function showQuestion(index) {
        if (index < 0 || index >= questions.length) return;

        const question = questions[index];
        questionText.textContent = question.text;
        optionsContainer.innerHTML = "";

        question.options.forEach((option, i) => {
            const optionButton = document.createElement("button");
            optionButton.classList.add("option");
            optionButton.textContent = option;

            if (userAnswers[index] === option) {
                optionButton.classList.add("selected");
            }
            console.log("Question Correct Answer:", question.correctAnswer);

            optionButton.addEventListener("click", () => {
                userAnswers[index] = option;
                showQuestion(index);

                handleAnswerSelection(option, question.correctAnswer, optionButton);
            });
            optionsContainer.appendChild(optionButton);
        });

        updateProgress();
    }

    
    
    

    function handleAnswerSelection(selectedOption, correctAnswer, optionButton) {
        console.log("Selected Option:", selectedOption);
        console.log("Correct Answer:", correctAnswer);

        const options = optionsContainer.querySelectorAll(".option");

        // Reset borders
        options.forEach(option => {
            option.style.border = "2px solid transparent";
        });

        // Highlight selected (default incorrect)
        optionButton.style.border = "2px solid red";

        // Get correct option index
        const correctAnswerIndex = correctAnswer.charCodeAt(0) - 65;
        const correctOption = options[correctAnswerIndex];

        // Highlight correct answer
        correctOption.style.border = "4px solid green";

        let isCorrect = false;

        // Check correctness
        if (selectedOption.trim().toLowerCase() === correctOption.textContent.trim().toLowerCase()) {
            optionButton.style.border = "2px solid green";
            isCorrect = true;
        }

        // 🔥 SEND RESULT TO BACKEND
        fetch('/submit_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_correct: isCorrect })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Updated quiz state:", data);

            // Optional: show live stats
            if (data.quiz_state) {
                console.log("Score:", data.quiz_state.score);
                console.log("Correct streak:", data.quiz_state.correct_streak);
                console.log("Wrong streak:", data.quiz_state.wrong_streak);
            }
        })
        .catch(error => {
            console.error("Error sending answer:", error);
        });
    }  
        
    
    
    
    
    
    
    function updateProgress() {
        const progressPercentage = ((currentQuestion + 1) / questions.length) * 100;
        progressBar.style.width = progressPercentage + "%";
        progressBar.textContent = Math.round(progressPercentage) + "%";
    }

    prevButton.addEventListener("click", () => {
        currentQuestion--;
        if (currentQuestion < 0) currentQuestion = 0;
        showQuestion(currentQuestion);
    });

    nextButton.addEventListener("click", () => {
        currentQuestion++;
        if (currentQuestion >= questions.length) {
            handleQuizCompletion();
            currentQuestion = questions.length - 1;
        }
        showQuestion(currentQuestion);
    });

    const sidebarLinks = document.querySelectorAll(".sidebar nav a");
    sidebarLinks.forEach(link => {
        link.addEventListener("click", () => {
            toggleSidebar();
        });
    });

    function handleQuizCompletion() {
        fetch('/reset_strikes')
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    console.log("Strikes reset successfully.");
                    lastStrikeCount = 0; // Reset lastStrikeCount
                    sessionStorage.setItem("lastStrikeCount", lastStrikeCount); // Update sessionStorage
                } else {
                    console.error("Error resetting strikes.");
                }
            })
            .catch(error => {
                console.error("Error resetting strikes:", error);
            });
    }

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