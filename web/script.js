const API = "http://127.0.0.1:8001/api";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) }
    });
  } catch (netErr) {
    throw new Error(
      `Cannot connect to StudyBuddy API at ${API}. Please ensure uvicorn is running.`
    );
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    if (data && data.detail) {
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail.map(d => d.msg || d.message || JSON.stringify(d)).join(", ");
      } else {
        message = JSON.stringify(data.detail);
      }
    }
    throw new Error(message);
  }
  return data;
}

function showResult(id, message, error = false) {
  const element = document.getElementById(id);
  if (!element) return;
  element.textContent = message;
  element.classList.toggle("error", error);
}

// 1. Save Study Notes
document.getElementById("note-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const topic = document.getElementById("note-topic").value.trim();
  const text = document.getElementById("note-text").value.trim();

  if (!topic || !text) {
    showResult("note-result", "Please fill in both topic and notes.", true);
    return;
  }

  showResult("note-result", "Saving...");
  try {
    const data = await request("/notes", {
      method: "POST",
      body: JSON.stringify({ topic, text })
    });
    showResult("note-result", data.result);
    document.getElementById("quiz-topic").value = topic;
    const viewTopicEl = document.getElementById("view-topic");
    if (viewTopicEl) viewTopicEl.value = topic;
    await loadTopics();
  } catch (error) {
    showResult("note-result", error.message, true);
  }
});

// 2. View Study Notes
async function viewNotes(topic) {
  const cleanTopic = (topic || "").trim();
  if (!cleanTopic) {
    showResult("view-notes-result", "Please enter a topic to view.", true);
    return;
  }
  showResult("view-notes-result", `Loading notes for "${cleanTopic}"...`);
  try {
    const data = await request(`/notes?topic=${encodeURIComponent(cleanTopic)}`);
    showResult("view-notes-result", data.result);
  } catch (error) {
    showResult("view-notes-result", error.message, true);
  }
}

const viewNotesForm = document.getElementById("view-notes-form");
if (viewNotesForm) {
  viewNotesForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const topic = document.getElementById("view-topic").value;
    await viewNotes(topic);
  });
}

// 3. Quiz Me
document.getElementById("quiz-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const topic = document.getElementById("quiz-topic").value.trim();
  const numQuestions = Number(document.getElementById("question-count").value);

  if (!topic) {
    showResult("quiz-result", "Please enter a topic for the quiz.", true);
    return;
  }

  showResult("quiz-result", "Preparing your quiz...");
  try {
    const data = await request("/quiz", {
      method: "POST",
      body: JSON.stringify({ topic, num_questions: numQuestions })
    });
    showResult("quiz-result", data.result);
  } catch (error) {
    showResult("quiz-result", error.message, true);
  }
});

// 4. Revision Planner
document.getElementById("plan-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const examDate = document.getElementById("exam-date").value;
  const rawTopics = document.getElementById("plan-topics").value;
  const topics = rawTopics.split(",").map(x => x.trim()).filter(Boolean);

  if (!examDate) {
    showResult("plan-result", "Please select an exam date.", true);
    return;
  }
  if (topics.length === 0) {
    showResult("plan-result", "Please enter at least one topic (e.g. OS, Networks).", true);
    return;
  }

  showResult("plan-result", "Building your plan...");
  try {
    const data = await request("/plan", {
      method: "POST",
      body: JSON.stringify({ exam_date: examDate, topics })
    });
    showResult("plan-result", data.result);
  } catch (error) {
    showResult("plan-result", error.message, true);
  }
});

// 5. Topics listing and interactive chips
async function loadTopics() {
  const chipsContainer = document.getElementById("topics-chips");
  try {
    const data = await request("/topics");
    const text = data.result || "";
    
    if (chipsContainer) {
      chipsContainer.innerHTML = "";
      // Parse topics from "Available topics:\n- OS\n- Networks"
      const lines = text.split("\n")
        .map(l => l.trim())
        .filter(l => l.startsWith("- "))
        .map(l => l.replace(/^[-\s*•]+/, "").trim())
        .filter(Boolean);

      if (lines.length === 0) {
        chipsContainer.innerHTML = `<span class="empty-topics-msg">No saved topics yet. Save a note above to get started!</span>`;
      } else {
        lines.forEach(topic => {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "topic-chip";
          chip.textContent = topic;
          chip.title = `Click to view notes and practice "${topic}"`;
          chip.addEventListener("click", () => {
            const viewInput = document.getElementById("view-topic");
            const quizInput = document.getElementById("quiz-topic");
            const noteInput = document.getElementById("note-topic");
            if (viewInput) viewInput.value = topic;
            if (quizInput) quizInput.value = topic;
            if (noteInput) noteInput.value = topic;
            viewNotes(topic);
          });
          chipsContainer.appendChild(chip);
        });
      }
    }
  } catch (error) {
    if (chipsContainer) {
      chipsContainer.innerHTML = `<span class="empty-topics-msg">${error.message}</span>`;
    }
  }
}

document.getElementById("refresh-topics").addEventListener("click", loadTopics);

// Set default and min date on exam date input
const examInput = document.getElementById("exam-date");
if (examInput) {
  const today = new Date().toISOString().split("T")[0];
  examInput.min = today;
  if (!examInput.value) {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    examInput.value = nextWeek.toISOString().split("T")[0];
  }
}

// Auto-load topics on page start
loadTopics();

// Voice input support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const mic = document.createElement("button");
  mic.type = "button";
  mic.className = "secondary-button";
  mic.textContent = "🎙 Fill note with voice";
  mic.style.marginTop = "10px";
  document.getElementById("note-form").appendChild(mic);

  mic.addEventListener("click", () => {
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = navigator.language || "en-US";
      recognition.interimResults = false;

      mic.textContent = "🎙 Listening... (speak now)";
      recognition.onresult = (event) => {
        const spoken = event.results[0][0].transcript;
        const textBox = document.getElementById("note-text");
        textBox.value = `${textBox.value}${textBox.value ? " " : ""}${spoken}`;
      };
      recognition.onerror = () => {
        showResult("note-result", "Voice input was unavailable. You can type your notes instead.", true);
        mic.textContent = "🎙 Fill note with voice";
      };
      recognition.onend = () => {
        mic.textContent = "🎙 Fill note with voice";
      };
      recognition.start();
    } catch (err) {
      showResult("note-result", "Voice input could not be started.", true);
      mic.textContent = "🎙 Fill note with voice";
    }
  });
}
