// Wedding site interactions: language toggle, RSVP helper, lightbox, countdown, shared bindings.

(function () {
  const DEFAULT_LANG = "en";

  const CONFIG = (window.SITE_CONFIG && typeof window.SITE_CONFIG === "object") ? window.SITE_CONFIG : {};
  const CONTACT = CONFIG.contact || {};
  const VENUE = CONFIG.venue || {};

  const PHONE_E164 = CONTACT.phoneE164 || "+15097139030";
  const PHONE_DISPLAY = CONTACT.phoneDisplay || "509-713-9030";

  function safeLang(lang) {
    return (lang === "es" || lang === "en") ? lang : DEFAULT_LANG;
  }

  function getLanguage() {
    try {
      const saved = localStorage.getItem("weddingLang");
      if (saved === "en" || saved === "es") return saved;
    } catch (e) {}
    return DEFAULT_LANG;
  }

  function setLanguage(lang) {
    const safe = safeLang(lang);
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

  function rsvpDisplay(url) {
    const u = String(url || "").trim();
    if (!u) return "";
    return u.replace(/^https?:\/\//i, "").replace(/\/$/, "");
  }

  function fullAddressQuery() {
    const name = String(VENUE.name || "").trim();
    const lines = Array.isArray(VENUE.addressLines) ? VENUE.addressLines : [];
    const parts = [name].concat(lines).filter(Boolean);
    return parts.join(", ");
  }

  function makeGoogleMapsLink(query) {
    const q = encodeURIComponent(query);
    return "https://www.google.com/maps/search/?api=1&query=" + q;
  }

  function makeWazeLink(query) {
    const q = encodeURIComponent(query);
    return "https://waze.com/ul?q=" + q + "&navigate=yes";
  }

  function applyBindings() {
    const lang = safeLang(document.documentElement.getAttribute("data-language"));

    // Text bindings
    document.querySelectorAll("[data-bind]").forEach((el) => {
      const key = el.getAttribute("data-bind");
      const elLang = safeLang(el.getAttribute("data-lang") || lang);

      let value = "";

      if (key === "dateTime") {
        const dt = CONFIG.dateTime;
        if (dt && typeof dt === "object") value = dt[elLang] || dt[DEFAULT_LANG] || "";
      } else if (key === "venueName") {
        value = String(VENUE.name || "");
      } else if (key === "venueAddress1") {
        value = String((Array.isArray(VENUE.addressLines) ? VENUE.addressLines[0] : "") || "");
      } else if (key === "venueAddress2") {
        value = String((Array.isArray(VENUE.addressLines) ? VENUE.addressLines[1] : "") || "");
      } else if (key === "venueAddress3") {
        value = String((Array.isArray(VENUE.addressLines) ? VENUE.addressLines[2] : "") || "");
      } else if (key === "phoneDisplay") {
        value = PHONE_DISPLAY;
      } else if (key === "rsvpDisplay") {
        value = rsvpDisplay(CONTACT.rsvpUrl);
      } else if (key === "rsvpUrl") {
        value = String(CONTACT.rsvpUrl || "");
      }

      if (typeof value === "string" && value) {
        el.textContent = value;
      }
    });

    // Href bindings
    const query = fullAddressQuery();
    const hrefMap = {
      googleMaps: makeGoogleMapsLink(query),
      waze: makeWazeLink(query),
      tel: "tel:" + PHONE_E164,
      sms: "sms:" + PHONE_E164,
      rsvpUrl: String(CONTACT.rsvpUrl || ""),
      calendar: String(CONFIG.calendarPath || "assets/wedding.ics"),
      venueWebsite: String((VENUE.links || {}).website || ""),
      venueInstagram: String((VENUE.links || {}).instagram || ""),
      venueFacebook: String((VENUE.links || {}).facebook || "")
    };

    document.querySelectorAll("[data-bind-href]").forEach((a) => {
      const key = a.getAttribute("data-bind-href");
      const href = hrefMap[key] || "";
      if (href) a.setAttribute("href", href);
    });
  }

  // Initialize language and bindings
  setLanguage(getLanguage());
  applyBindings();

  // Wire up language buttons
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      setLanguage(btn.dataset.lang);
      applyBindings();
    });
  });

  // Build photo gallery (index page)
  const galleryEl = document.getElementById("photoGallery");
  const photos = Array.isArray(window.PHOTO_GALLERY) ? window.PHOTO_GALLERY : null;
  if (galleryEl && photos) {
    galleryEl.innerHTML = "";

    photos.forEach((p) => {
      const fig = document.createElement("figure");
      fig.className = "polaroid " + (p.tilt || "tilt1");
      fig.setAttribute("data-full", p.full);

      const img = document.createElement("img");
      img.src = p.thumb || p.full;
      img.loading = "lazy";
      img.alt = (p.alt && p.alt.en) ? p.alt.en : "";
      fig.appendChild(img);

      const capEn = document.createElement("figcaption");
      capEn.setAttribute("data-lang", "en");
      capEn.textContent = (p.caption && p.caption.en) ? p.caption.en : "";
      fig.appendChild(capEn);

      const capEs = document.createElement("figcaption");
      capEs.setAttribute("data-lang", "es");
      capEs.textContent = (p.caption && p.caption.es) ? p.caption.es : "";
      fig.appendChild(capEs);

      galleryEl.appendChild(fig);
    });
  }

  // Countdown
  const countdownEl = document.getElementById("countdownValue");
  if (countdownEl) {
    const target = new Date(String(CONFIG.startIso || "2026-11-27T16:00:00-06:00"));
    const tick = () => {
      const now = new Date();
      const ms = target.getTime() - now.getTime();
      const days = Math.max(0, Math.ceil(ms / (1000 * 60 * 60 * 24)));
      const lang = safeLang(document.documentElement.getAttribute("data-language"));
      countdownEl.textContent = (lang === "es") ? (days + " días") : (days + " days");
    };
    tick();
    setInterval(tick, 60_000);
  }

  // RSVP form helper (index page)
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

      const lang = safeLang(document.documentElement.getAttribute("data-language"));

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

  // Lightbox (index page)
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

  document.addEventListener("click", (ev) => {
    const fig = ev.target && ev.target.closest ? ev.target.closest(".polaroid") : null;
    if (!fig) return;

    const full = fig.getAttribute("data-full");
    const img = fig.querySelector("img");
    const alt = img ? img.getAttribute("alt") : "";
    if (full) openLightbox(full, alt);
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
