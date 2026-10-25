(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const entryView = $("entry-view");
  const letterView = $("letter-view");
  const form = $("entry-form");
  const input = $("secret-name");
  const errorBox = $("entry-error");
  const greeting = $("greeting");
  const envelope = $("envelope");
  const addressName = $("address-name");
  const seal = $("seal");
  const letter = $("letter");
  const letterHeading = $("letter-heading");
  const recipientEl = $("recipient");

  const normalize = (value) => value.normalize("NFC").trim().replace(/\s+/g, " ").toLocaleLowerCase();
  const isText = (v) => typeof v === "string" && normalize(v) !== "";

  let current = null;

  function buildLookup(secrets, assignments) {
    if (!Array.isArray(secrets) || !secrets.length || !assignments || typeof assignments !== "object") {
      throw new Error("Malformed data");
    }
    const lookup = new Map();
    for (const entry of secrets) {
      if (!isText(entry?.realName) || !isText(entry?.secretName)) throw new Error("Malformed secrets");
      const recipient = assignments[entry.realName];
      if (!isText(recipient) || recipient === entry.realName) throw new Error("Malformed assignments");
      if (!secrets.some((s) => s.realName === recipient)) throw new Error("Unknown recipient");
      lookup.set(normalize(entry.secretName), { realName: entry.realName, recipient });
    }
    if (lookup.size !== secrets.length) throw new Error("Duplicate secret names");
    return lookup;
  }

  let lookup = null;
  try {
    lookup = buildLookup(window.SECRETS, window.ASSIGNMENTS);
  } catch {
    // Reported on submit so the form still renders.
  }

  function showError(message) {
    errorBox.textContent = message;
    input.setAttribute("aria-invalid", "true");
    input.focus();
  }

  function clearError() {
    errorBox.textContent = "";
    input.removeAttribute("aria-invalid");
  }

  function showLetterView(entry) {
    current = entry;
    greeting.textContent = `Merry Christmas, ${entry.realName}!`;
    addressName.textContent = entry.realName;
    input.value = "";
    sealLetter();
    entryView.hidden = true;
    letterView.hidden = false;
    greeting.focus();
  }

  function openLetter() {
    if (!current) return;
    letterHeading.textContent = `Dear ${current.realName},`;
    recipientEl.textContent = current.recipient;
    envelope.classList.add("is-open");
    seal.disabled = true;
    letter.hidden = false;
    letterHeading.focus();
  }

  function sealLetter() {
    envelope.classList.remove("is-open");
    seal.disabled = false;
    letter.hidden = true;
    letterHeading.textContent = "";
    recipientEl.textContent = "";
  }

  function reset() {
    current = null;
    sealLetter();
    greeting.textContent = "";
    addressName.textContent = "";
    clearError();
    letterView.hidden = true;
    entryView.hidden = false;
    input.focus();
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearError();
    const key = normalize(input.value);
    if (!key) {
      showError("Type your secret Christmas name first.");
      return;
    }
    if (!lookup) {
      showError("The elves lost the list. Please reload the page and try again.");
      return;
    }
    const entry = lookup.get(key);
    if (entry) {
      showLetterView(entry);
    } else {
      showError("The elves don't recognise that name. Check the spelling and try again.");
    }
  });

  input.addEventListener("input", clearError);
  seal.addEventListener("click", openLetter);
  $("reseal").addEventListener("click", () => {
    sealLetter();
    seal.focus();
  });
  $("reset").addEventListener("click", reset);

  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const snow = $("snow");
    for (let i = 0; i < 28; i++) {
      const flake = document.createElement("span");
      flake.className = "flake";
      flake.style.left = `${Math.random() * 100}%`;
      flake.style.setProperty("--size", `${2 + Math.random() * 4}px`);
      flake.style.setProperty("--dur", `${9 + Math.random() * 10}s`);
      flake.style.setProperty("--delay", `${-Math.random() * 18}s`);
      flake.style.setProperty("--drift", `${-30 + Math.random() * 60}px`);
      snow.appendChild(flake);
    }
  }
})();
