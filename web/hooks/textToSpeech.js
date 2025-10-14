// web/hooks/textToSpeech.js
// Browser-native speech synthesis with voice selection and state tracking.

let isSpeaking = false;
let availableVoices = [];

// --- Load voices (async on some browsers) ---
function loadVoices() {
  const voices = window.speechSynthesis.getVoices();
  if (voices && voices.length > 0) {
    availableVoices = voices;
  }
}
window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

// --- Core speak() function ---
export function speak(text) {
  if (!window.speechSynthesis) {
    console.error("Speech synthesis not supported in this browser.");
    return;
  }
  if (!text || !text.trim()) return;

  // Stop any current speech before starting a new one
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  // Try to choose a natural-sounding English female voice
  const femaleVoice =
    availableVoices.find(
      (v) => v.name === "Google US English" && v.lang === "en-US"
    ) ||
    availableVoices.find(
      (v) => v.lang === "en-US" && /female/i.test(v.name)
    ) ||
    availableVoices.find((v) => v.lang.startsWith("en")) ||
    null;

  utterance.voice = femaleVoice;
  utterance.lang = "en-US";
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  utterance.onstart = () => {
    isSpeaking = true;
    console.log("[DEBUG] Speaking started:", utterance.text);
  };
  utterance.onend = () => {
    isSpeaking = false;
    console.log("[DEBUG] Speaking finished.");
  };
  utterance.onerror = (e) => {
    isSpeaking = false;
    console.error("Speech synthesis error:", e.error);
  };

  window.speechSynthesis.speak(utterance);
}

// --- Query current speaking state (optional UI indicator) ---
export function getSpeakingStatus() {
  return isSpeaking || window.speechSynthesis.speaking;
}

// --- Stop any ongoing speech (optional manual control) ---
export function stopSpeaking() {
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    console.log("[DEBUG] Speech stopped manually.");
  }
}

// --- Clean up on unload ---
window.addEventListener("beforeunload", () => {
  if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();
});
