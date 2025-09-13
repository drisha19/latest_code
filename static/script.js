let lastBlinkTime = 0;
let selectedBtn = null;
let selectionEnabled = false;
let recognition;

// Speak function
function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
}

// Simulated GenAI response generator
function getGenAIOptions(question) {
    const q = question.toLowerCase();

    if (q.includes("water")) {
        return [
            "Give me water please.",
            "I'm feeling thirsty.",
            "Call caregiver for water.",
            "Show me how to ask for water."
        ];
    } else if (q.includes("pain")) {
        return [
            "I have a headache.",
            "My legs hurt.",
            "Call doctor please.",
            "Give me medicine."
        ];
    } else if (q.includes("hungry")) {
        return [
            "I need food.",
            "I'm feeling very hungry.",
            "Bring me a snack.",
            "Call someone for food."
        ];
    } else {
        return [
            "Yes, I need help.",
            "No, I'm okay.",
            "Call my caregiver.",
            "Please check on me."
        ];
    }
}

// Update buttons with GenAI options
function handleSpokenQuestion(question) {
    document.getElementById("questionDisplay").textContent = "You asked: " + question;
    const options = getGenAIOptions(question);

    if (options.length === 4) {
        document.getElementById("btn1").textContent = options[0];
        document.getElementById("btn2").textContent = options[1];
        document.getElementById("btn3").textContent = options[2];
        document.getElementById("btn4").textContent = options[3];
    } else {
        console.error("Expected 4 options, got:", options);
    }
}

// Face direction processing
function updateSelection(noseX, noseY, blink) {
    const yes = document.getElementById("btn1");
    const no = document.getElementById("btn2");
    const go = document.getElementById("btn3");
    const come = document.getElementById("btn4");

      // Reset all
    [yes, no, go, come].forEach(btn => {
        btn.style.backgroundColor = "";
        btn.classList.remove("selected");
    });

    if (noseX > 0.5 && noseY < 0.5) {
        yes.style.backgroundColor = "#0a7f27";
        yes.classList.add("selected");
        selectedBtn = yes.textContent;
    } else if (noseX < 0.5 && noseY < 0.5) {
        no.style.backgroundColor = "#b30000";
        no.classList.add("selected");
        selectedBtn = no.textContent;
    } else if (noseX > 0.5 && noseY > 0.5) {
        go.style.backgroundColor = "#e6a200";
        go.classList.add("selected");
        selectedBtn = go.textContent;
    } else if (noseX < 0.5 && noseY > 0.5) {
        come.style.backgroundColor = "#e65c00";
        come.classList.add("selected");
        selectedBtn = come.textContent;
    }

    // Blink detection to confirm selection
    if (selectionEnabled && blink && Date.now() - lastBlinkTime > 1000) {
        console.log("Selected:", selectedBtn);
        speak(selectedBtn);

        fetch("/button_clicked", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ button: selectedBtn })
        });

        lastBlinkTime = Date.now();
        selectionEnabled = false;

        // Automatically restart mic for next question
        recognition.start();
    }
}

// Start polling for face direction
function startTracking() {
    setInterval(() => {
        fetch("/get_direction")
            .then(res => res.json())
            .then(data => {
                const [x, y, b] = data.direction.split(",").map(parseFloat);
                updateSelection(x, y, b);
            })
            .catch(err => console.error("Direction fetch error", err));
    }, 500);
}

// Init everything on load
window.onload = () => {
    startTracking();

    const micBtn = document.getElementById("mic-btn");
    const questionText = document.getElementById("question");

    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();

        recognition.lang = "en-US";
        recognition.interimResults = false;

        recognition.onstart = () => {
            questionText.innerText = "Listening...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            questionText.innerText = transcript;
            selectionEnabled = true;

            // Trigger GenAI suggestion logic
            handleSpokenQuestion(transcript);
        };

        recognition.onerror = (e) => {
            console.error("Speech error", e.error);
        };

        recognition.onend = () => {
            console.log("Speech recognition ended.");
        };

        micBtn.addEventListener("click", () => {
            recognition.start();
        });
    } else {
        alert("Speech recognition not supported");
    }
};
