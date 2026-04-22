const form = document.getElementById("chat-form");
const messagesEl = document.getElementById("messages");
const questionInput = document.getElementById("question");
const modeSelect = document.getElementById("mode");
const tempInput = document.getElementById("temperature");
const metaEl = document.getElementById("meta");
const metaContainer = document.getElementById("meta-container");
const chatTitle = document.getElementById("chat-title");

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

  const payload = {
    question,
    history: history.slice(-10),
    temperature: Number(tempInput.value || 0.2),
  };
  const endpoint = modeSelect.value === "rag" ? "/api/rag/chat" : "/api/chat";

  metaContainer.style.display = "block";
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
    if (modeSelect.value === "rag" && data.docs && data.docs.length > 0) {
      renderDocs(data.docs);
    } else {
      metaEl.textContent = JSON.stringify({ mode: modeSelect.value, sources: data.sources || [] }, null, 2);
    }
  } catch (error) {
    addMessage("assistant", `Error: ${error.message}`);
    metaEl.textContent = JSON.stringify({ error: error.message }, null, 2);
  }
}

function renderDocs(docs) {
  metaEl.innerHTML = "";
  docs.forEach((doc, i) => {
    const card = document.createElement("div");
    card.className = "doc-card";

    const heading = document.createElement("div");
    heading.className = "doc-card-heading";
    heading.textContent = `[${i + 1}] ${doc.title || "Untitled"}`;
    card.appendChild(heading);

    const fields = Object.entries(doc).filter(([k]) => k !== "title" && k !== "content" && k !== "source");
    if (fields.length > 0) {
      const meta = document.createElement("div");
      meta.className = "doc-card-meta";
      meta.textContent = fields.map(([k, v]) => `${k}: ${v}`).join("  |  ");
      card.appendChild(meta);
    }

    const content = document.createElement("div");
    content.className = "doc-card-content";
    content.textContent = doc.content || "";
    card.appendChild(content);

    metaEl.appendChild(card);
  });
}

function updateModeUI() {
  const isRagMode = modeSelect.value === "rag";
  chatTitle.textContent = isRagMode ? "RAG Chat" : "Chat";

  // Clear messages and meta when switching modes
  messagesEl.innerHTML = "";
  metaContainer.style.display = "none";
  metaEl.innerHTML = "";
  history.length = 0;
}

modeSelect.addEventListener("change", updateModeUI);
form.addEventListener("submit", sendQuestion);
