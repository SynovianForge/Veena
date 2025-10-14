// main.js
import { startListening } from "./hooks/speechRecognition.js";
import { speak } from "./hooks/textToSpeech.js";

const API_URL = window.location.origin + "/chat";

// === DOM references ===
const textInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const responseText = document.getElementById("responseText");
const chatContainer = document.getElementById("chatInputContainer");

// === Helpers for updating UI ===

// Smoothly updates the text output area
function updateResponse(text) {
  responseText.style.opacity = 0;
  setTimeout(() => {
    responseText.innerText = text.trim();
    responseText.style.opacity = 1;
  }, 150);
}

// Optional "thinking" indicator
function showThinking() {
  responseText.innerText = "…";
  responseText.style.opacity = 0.6;
}

// Fade input bar during voice input/output
function onVoiceStart() {
  chatContainer.classList.add("hidden");
}

function onVoiceEnd() {
  chatContainer.classList.remove("hidden");
}

// === Core chat ===
async function sendMessage(text) {
  console.log("[DEBUG] sendMessage called with:", text);
  if (!text || !text.trim()) return;

  const userInput = text.trim();
  textInput.value = "";

  showThinking();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: userInput }),
    });

    console.log("[DEBUG] fetch response status:", response.status);
    const data = await response.json();
    console.log("[DEBUG] response JSON:", data);

    const reply = data.reply || data.output || "(no reply)";

    // Update left-side response area
    updateResponse(reply);

    // === Voice playback with fade ===
    if (typeof speak === "function" && reply.trim().length > 0) {
      onVoiceStart();

      // speak() is asynchronous only if it returns a Promise
      const maybePromise = speak(reply);

      // If speak() returns a promise, await it, otherwise use fallback timing
      if (maybePromise && typeof maybePromise.then === "function") {
        await maybePromise;
      } else {
        const fallbackMs = Math.min(reply.length * 40, 8000);
        await new Promise((res) => setTimeout(res, fallbackMs));
      }

      onVoiceEnd();
    }
  } catch (err) {
    console.error("[DEBUG] fetch failed:", err);
    updateResponse("⚠️ Error: " + err.message);
  }
}

// === Event listeners ===
sendBtn.onclick = () => {
  console.log("[DEBUG] Send button clicked");
  sendMessage(textInput.value);
};

textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    console.log("[DEBUG] Enter key pressed");
    sendMessage(textInput.value);
  }
});

micBtn.onclick = () => {
  console.log("[DEBUG] Mic button clicked");
  onVoiceStart();
  startListening((transcript) => {
    console.log("[DEBUG] Transcribed:", transcript);
    updateResponse("🎤 " + transcript);
    sendMessage(transcript);
    onVoiceEnd();
  });
};

// === Initial message ===
updateResponse("👋 System ready. Type or speak to begin.");
