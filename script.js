// Wedding site interactions: language toggle, RSVP helper, lightbox, countdown.

(function () {
  const DEFAULT_LANG = "en";
  const PHONE_E164 = "+15097139030";

  function setLanguage(lang) {
    const safe = (lang === "es" || lang === "en") ? lang : DEFAULT_LANG;
    document.documentElement.setAttribute("data-language", safe);

    document.querySelectorAll(".lang-btn").forEach((btn) => {
      const isActive = btn.dataset.lang === safe;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });

    // Update RSVP select labels
    const attendingSelect = document.querySelector('select[name="attending"]');
    if (attendingSelect && attendingSelect.options && attendingSelect.options.length >= 3) {
      attendingSelect.options[0].textContent = (safe === "es") ? "Seleccionar" : "Select";
      attendingSelect.options[1].textContent = (safe === "es") ? "Sí" : "Yes";
      attendingSelect.options[2].textContent = "No";
    }


    try { localStorage.setItem("weddingLang", safe); } catch (e) {}
  }

  function getLanguage() {
    try {
      const saved = localStorage.getItem("weddingLang");
      if (saved === "en" || saved === "es") return saved;
    } catch (e) {}
    return DEFAULT_LANG;
  }

  // Initialize language
  setLanguage(getLanguage());

  // Wire up language buttons
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => setLanguage(btn.dataset.lang));
  });

  // Countdown
  const countdownEl = document.getElementById("countdownValue");
  if (countdownEl) {
    const target = new Date("2026-11-27T16:00:00-06:00");
    const tick = () => {
      const now = new Date();
      const ms = target.getTime() - now.getTime();
      const days = Math.max(0, Math.ceil(ms / (1000 * 60 * 60 * 24)));
      const lang = document.documentElement.getAttribute("data-language") || DEFAULT_LANG;
      countdownEl.textContent = (lang === "es") ? (days + " días") : (days + " days");
    };
    tick();
    setInterval(tick, 60_000);
  }

  // RSVP form helper
  const form = document.getElementById("rsvpForm");
  const out = document.getElementById("rsvpOutput");
  const box = document.getElementById("messageBox");
  const smsBtn = document.getElementById("smsBtn");
  const smsBtnEs = document.getElementById("smsBtnEs");
  const copyBtn = document.getElementById("copyBtn");
  const copyBtnEs = document.getElementById("copyBtnEs");

  function buildMessage(values, lang) {
    if (lang === "es") {
      return (
        "Hola! Soy " + values.name + ".\n" +
        "RSVP: " + values.attending + "\n" +
        "Invitados: " + values.guests + "\n" +
        (values.diet ? ("Restricciones: " + values.diet + "\n") : "") +
        "Gracias!"
      );
    }
    return (
      "Hi! This is " + values.name + ".\n" +
      "RSVP: " + values.attending + "\n" +
      "Guests: " + values.guests + "\n" +
      (values.diet ? ("Dietary notes: " + values.diet + "\n") : "") +
      "Thank you!"
    );
  }

  function smsHref(message) {
    const body = encodeURIComponent(message);
    return "sms:" + PHONE_E164 + "?&body=" + body;
  }

  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      return false;
    }
  }

  if (form && out && box) {
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();

      const lang = document.documentElement.getAttribute("data-language") || DEFAULT_LANG;

      const name = String(form.elements.namedItem("name").value || "").trim();
      const attending = String(form.elements.namedItem("attending").value || "").trim();
      const guests = String(form.elements.namedItem("guests").value || "1").trim();
      const diet = String(form.elements.namedItem("diet").value || "").trim();

      const msg = buildMessage({ name, attending, guests, diet }, lang);

      box.textContent = msg;
      out.hidden = false;

      if (smsBtn) smsBtn.href = smsHref(msg);
      if (smsBtnEs) smsBtnEs.href = smsHref(msg);

      const ok = await copyToClipboard(msg);
      if (ok) {
        const label = (lang === "es") ? "Copiado" : "Copied";
        if (copyBtn) copyBtn.textContent = label;
        if (copyBtnEs) copyBtnEs.textContent = label;
        setTimeout(() => {
          if (copyBtn) copyBtn.textContent = "Copy";
          if (copyBtnEs) copyBtnEs.textContent = "Copiar";
        }, 1400);
      }
    });

    if (copyBtn) {
      copyBtn.addEventListener("click", () => copyToClipboard(box.textContent || ""));
    }
    if (copyBtnEs) {
      copyBtnEs.addEventListener("click", () => copyToClipboard(box.textContent || ""));
    }
  }

  // Lightbox
  const dialog = document.getElementById("lightbox");
  const dialogImg = document.getElementById("lightboxImg");
  const closeBtn = document.getElementById("closeLightbox");

  function openLightbox(src, alt) {
    if (!dialog || !dialogImg) return;
    dialogImg.src = src;
    dialogImg.alt = alt || "";
    dialog.showModal();
  }

  function closeLightbox() {
    if (!dialog) return;
    dialog.close();
  }

  document.querySelectorAll(".polaroid").forEach((fig) => {
    fig.addEventListener("click", () => {
      const full = fig.getAttribute("data-full");
      const img = fig.querySelector("img");
      const alt = img ? img.getAttribute("alt") : "";
      if (full) openLightbox(full, alt);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
  if (dialog) {
    dialog.addEventListener("click", (ev) => {
      const rect = dialogImg ? dialogImg.getBoundingClientRect() : null;
      if (!rect) return;
      const inside = ev.clientX >= rect.left && ev.clientX <= rect.right && ev.clientY >= rect.top && ev.clientY <= rect.bottom;
      if (!inside) closeLightbox();
    });
  }
})();
