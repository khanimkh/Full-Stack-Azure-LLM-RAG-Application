const form = document.getElementById("chat-form");
const messagesEl = document.getElementById("messages");
const questionInput = document.getElementById("question");
const modeSelect = document.getElementById("mode");
const tempInput = document.getElementById("temperature");
const metaEl = document.getElementById("meta");
const initIndexBtn = document.getElementById("init-index");
const loadSampleBtn = document.getElementById("load-sample");

const history = [];

function addMessage(role, content) {
  history.push({ role, content });
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  row.textContent = `${role.toUpperCase()}: ${content}`;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendQuestion(event) {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  addMessage("user", question);
  questionInput.value = "";

  const endpoint = modeSelect.value === "rag" ? "/api/rag/chat" : "/api/chat";
  const payload = {
    question,
    history: history.slice(-10),
    temperature: Number(tempInput.value || 0.2),
  };

  metaEl.textContent = "Thinking...";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }
    addMessage("assistant", data.answer);
    metaEl.textContent = JSON.stringify({ mode: modeSelect.value, sources: data.sources || [] }, null, 2);
  } catch (error) {
    addMessage("assistant", `Error: ${error.message}`);
    metaEl.textContent = JSON.stringify({ error: error.message }, null, 2);
  }
}

async function initIndex() {
  const response = await fetch("/api/rag/index/init", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await response.json();
  metaEl.textContent = JSON.stringify(data, null, 2);
}

async function loadSample() {
  const response = await fetch("/api/rag/index/load-sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await response.json();
  metaEl.textContent = JSON.stringify(data, null, 2);
}

form.addEventListener("submit", sendQuestion);
initIndexBtn.addEventListener("click", initIndex);
loadSampleBtn.addEventListener("click", loadSample);
