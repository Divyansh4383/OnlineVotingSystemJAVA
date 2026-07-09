/* ============================================================
   AgentFlow — frontend logic
   Talks to the Flask API in webapp.py. No business logic lives
   here — just wiring the rail, inputs, and output panel to
   /api/* endpoints.
   ============================================================ */

const STAGES = [
  {
    id: "plan",
    label: "PLAN",
    title: "Plan",
    desc: "Turn a requirement into a structured implementation plan.",
    input: "requirement",
    endpoint: "/api/plan",
    runLabel: "Run plan",
    buildBody: () => ({ requirement: el("requirementInput").value.trim() }),
  },
  {
    id: "docs",
    label: "DOCS",
    title: "Docs",
    desc: "Generate technical documentation for a piece of code.",
    input: "code",
    endpoint: "/api/docs",
    runLabel: "Generate docs",
    buildBody: () => ({ code: el("codeInput").value, language: el("languageSelect").value }),
  },
  {
    id: "review",
    label: "REVIEW",
    title: "Review",
    desc: "Run an automated code review: correctness, security, style, performance.",
    input: "code",
    endpoint: "/api/review",
    runLabel: "Run review",
    buildBody: () => ({ code: el("codeInput").value, language: el("languageSelect").value }),
  },
  {
    id: "bugs",
    label: "BUGS",
    title: "Bug detection",
    desc: "Scan code specifically for logic errors, edge cases, and correctness bugs.",
    input: "code",
    endpoint: "/api/bugs",
    runLabel: "Find bugs",
    buildBody: () => ({ code: el("codeInput").value, language: el("languageSelect").value }),
  },
  {
    id: "improve",
    label: "IMPROVE",
    title: "Improvements",
    desc: "Get concrete suggestions for readability, structure, and performance.",
    input: "code",
    endpoint: "/api/improve",
    runLabel: "Suggest improvements",
    buildBody: () => ({ code: el("codeInput").value, language: el("languageSelect").value }),
  },
  {
    id: "chat",
    label: "CHAT",
    title: "Chat",
    desc: "Free-form conversation with memory — ask follow-ups about anything above.",
    input: "chat",
    endpoint: "/api/chat",
    runLabel: "Send",
    buildBody: () => ({ message: el("chatInput").value.trim() }),
  },
];

let currentStageId = "plan";

function el(id) { return document.getElementById(id); }

function currentStage() {
  return STAGES.find((s) => s.id === currentStageId);
}

function currentSession() {
  return el("sessionInput").value.trim();
}

/* ---------- Rail ---------- */

function renderRail() {
  const track = el("railTrack");
  track.innerHTML = "";
  STAGES.forEach((stage) => {
    const btn = document.createElement("button");
    btn.className = "rail-node" + (stage.id === currentStageId ? " active" : "");
    btn.innerHTML = `<span class="rail-node-dot"></span><span class="rail-node-label">${stage.label}</span>`;
    btn.addEventListener("click", () => selectStage(stage.id));
    track.appendChild(btn);
  });
}

function selectStage(id) {
  currentStageId = id;
  const stage = currentStage();

  el("stageTitle").textContent = stage.title;
  el("stageDesc").textContent = stage.desc;
  el("runBtnLabel").textContent = stage.runLabel;

  el("block-requirement").classList.toggle("hidden", stage.input !== "requirement");
  el("block-code").classList.toggle("hidden", stage.input !== "code");
  el("block-chat").classList.toggle("hidden", stage.input !== "chat");
  el("outputPanel").classList.toggle("hidden", stage.input === "chat");

  el("runStatus").textContent = "";
  renderRail();
}

/* ---------- Output rendering ---------- */

function renderMarkdown(text) {
  if (window.marked) {
    return marked.parse(text);
  }
  // graceful fallback if the CDN script didn't load
  return `<pre>${escapeHtml(text)}</pre>`;
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function setOutput(html, state) {
  el("outputContent").innerHTML = html;
  const dot = document.querySelector(".output-dot");
  dot.className = "output-dot" + (state ? " " + state : "");
}

/* ---------- Rail flow animation while a request is in-flight ---------- */

function setFlowing(isFlowing) {
  el("railTrack").classList.toggle("flowing", isFlowing);
}

/* ---------- Running a stage ---------- */

async function runCurrentStage() {
  const stage = currentStage();

  if (stage.input === "chat") {
    await sendChatMessage();
    return;
  }

  const body = stage.buildBody();
  const emptyCheck = stage.input === "requirement" ? body.requirement : body.code;
  if (!emptyCheck) {
    el("runStatus").textContent = "Nothing to run yet — fill in the input above.";
    el("runStatus").classList.add("error");
    return;
  }
  body.session = currentSession();

  setRunning(true);
  setOutput('<p class="output-empty">Working…</p>');

  try {
    const res = await fetch(stage.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (data.ok) {
      setOutput(renderMarkdown(data.result), "done");
      el("runStatus").textContent = "Done.";
      el("runStatus").classList.remove("error");
    } else {
      setOutput(`<p class="output-empty">${escapeHtml(data.error)}</p>`, "error");
      el("runStatus").textContent = data.error;
      el("runStatus").classList.add("error");
    }
  } catch (err) {
    setOutput(`<p class="output-empty">Network error: could not reach the AgentFlow server.</p>`, "error");
    el("runStatus").textContent = "Network error.";
    el("runStatus").classList.add("error");
  } finally {
    setRunning(false);
  }
}

function setRunning(isRunning) {
  el("runBtn").disabled = isRunning;
  setFlowing(isRunning);
}

/* ---------- Chat ---------- */

function appendChatMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = "chat-msg " + role;
  wrap.innerHTML = role === "model" ? renderMarkdown(text) : escapeHtml(text);
  el("chatTranscript").appendChild(wrap);
  wrap.scrollIntoView({ behavior: "smooth", block: "end" });
}

async function sendChatMessage() {
  const input = el("chatInput");
  const message = input.value.trim();
  if (!message) return;

  appendChatMessage("user", message);
  input.value = "";
  setRunning(true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session: currentSession() || "chat" }),
    });
    const data = await res.json();
    if (data.ok) {
      appendChatMessage("model", data.result);
    } else {
      appendChatMessage("model", `_Error: ${data.error}_`);
    }
  } catch (err) {
    appendChatMessage("model", "_Network error: could not reach the AgentFlow server._");
  } finally {
    setRunning(false);
  }
}

/* ---------- Sessions ---------- */

async function loadSessions() {
  const list = el("sessionsList");
  try {
    const res = await fetch("/api/sessions");
    const data = await res.json();
    list.innerHTML = "";
    if (!data.sessions || data.sessions.length === 0) {
      list.innerHTML = '<div class="rail-sessions-empty">No saved sessions yet.</div>';
      return;
    }
    data.sessions.forEach((name) => {
      const item = document.createElement("div");
      item.className = "rail-sessions-list-item";
      item.textContent = name;
      item.addEventListener("click", () => {
        el("sessionInput").value = name;
        list.classList.add("hidden");
      });
      list.appendChild(item);
    });
  } catch (err) {
    list.innerHTML = '<div class="rail-sessions-empty">Could not load sessions.</div>';
  }
}

async function clearCurrentSession() {
  const name = currentSession() || "default";
  try {
    await fetch(`/api/sessions/${encodeURIComponent(name)}`, { method: "DELETE" });
    el("runStatus").textContent = `Session "${name}" cleared.`;
    el("runStatus").classList.remove("error");
    if (currentStageId === "chat") {
      el("chatTranscript").innerHTML = "";
    }
  } catch (err) {
    el("runStatus").textContent = "Could not clear session.";
    el("runStatus").classList.add("error");
  }
}

/* ---------- Wire up ---------- */

document.addEventListener("DOMContentLoaded", () => {
  renderRail();
  selectStage("plan");

  el("runBtn").addEventListener("click", runCurrentStage);

  el("chatInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runCurrentStage();
  });

  el("clearSessionBtn").addEventListener("click", clearCurrentSession);

  el("sessionsListBtn").addEventListener("click", () => {
    const list = el("sessionsList");
    list.classList.toggle("hidden");
    if (!list.classList.contains("hidden")) loadSessions();
  });

  document.addEventListener("click", (e) => {
    const list = el("sessionsList");
    if (!list.contains(e.target) && e.target.id !== "sessionsListBtn") {
      list.classList.add("hidden");
    }
  });
});
