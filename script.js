/* Wedding site interactions:
   - Language toggle (data-language on <html>)
   - Data bindings from window.SITE_CONFIG
   - Photo gallery from window.PHOTO_GALLERY
   - Countdown (days)
   - RSVP message helper
   - Lightbox
*/

(function () {
  "use strict";

  const DEFAULT_LANG = "en";

  function safeLang(x) {
    return (x === "es") ? "es" : "en";
  }

  function getSavedLang() {
    try {
      const v = localStorage.getItem("siteLang");
      return safeLang(v);
    } catch (e) {
      return DEFAULT_LANG;
    }
  }

  function saveLang(lang) {
    try { localStorage.setItem("siteLang", lang); } catch (e) {}
  }

  function setLanguage(lang) {
    const v = safeLang(lang);
    document.documentElement.setAttribute("data-language", v);

    const btns = Array.from(document.querySelectorAll(".lang-btn"));
    btns.forEach((b) => b.setAttribute("aria-pressed", (b.dataset.lang === v) ? "true" : "false"));

    // RSVP select label fixups (optional)
    const attending = document.querySelector('select[name="attending"]');
    if (attending && attending.options && attending.options.length >= 3) {
      attending.options[0].textContent = (v === "es") ? "Seleccionar" : "Select";
      attending.options[1].textContent = (v === "es") ? "Sí" : "Yes";
      attending.options[2].textContent = "No";
    }

    saveLang(v);
    return v;
  }

  const CONFIG = (window.SITE_CONFIG && typeof window.SITE_CONFIG === "object") ? window.SITE_CONFIG : {};
  const CONTACT = (CONFIG.contact && typeof CONFIG.contact === "object") ? CONFIG.contact : {};
  const VENUE = (CONFIG.venue && typeof CONFIG.venue === "object") ? CONFIG.venue : {};

  const PHONE_E164 = CONTACT.phoneE164 || "+15097139030";
  const PHONE_DISPLAY = CONTACT.phoneDisplay || "509-713-9030";

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
    return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(query);
  }

  function makeWazeLink(query) {
    return "https://waze.com/ul?q=" + encodeURIComponent(query) + "&navigate=yes";
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
      venueWebsite: String(((VENUE.links || {}).website) || ""),
      venueInstagram: String(((VENUE.links || {}).instagram) || ""),
      venueFacebook: String(((VENUE.links || {}).facebook) || "")
    };

    document.querySelectorAll("[data-bind-href]").forEach((a) => {
      const key = a.getAttribute("data-bind-href");
      const href = hrefMap[key] || "";
      if (href) a.setAttribute("href", href);
    });
  }

  function initGallery() {
    const galleryEl = document.getElementById("photoGallery");
    if (!galleryEl) return;

    const photos = Array.isArray(window.PHOTO_GALLERY) ? window.PHOTO_GALLERY : [];

    const norm = photos
      .filter((p) => p && typeof p === "object" && typeof p.full === "string" && typeof p.thumb === "string")
      .map((p) => {
        const alt = (p.alt && typeof p.alt === "object") ? p.alt : {};
        const cap = (p.caption && typeof p.caption === "object") ? p.caption : {};
        return {
          full: p.full,
          thumb: p.thumb,
          alt: { en: String(alt.en || "Photo"), es: String(alt.es || "Foto") },
          caption: { en: String(cap.en || ""), es: String(cap.es || "") },
          tilt: typeof p.tilt === "string" ? p.tilt : "tilt2"
        };
      });

    if (!norm.length) return;

    // Replace fallback content
    galleryEl.innerHTML = "";

    norm.forEach((p) => {
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

    // Lightbox wiring
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
      const t = ev.target;
      const fig = (t && t.closest) ? t.closest(".polaroid") : null;
      if (!fig) return;
      const full = fig.getAttribute("data-full");
      const img = fig.querySelector("img");
      const alt = img ? img.getAttribute("alt") : "";
      if (full) openLightbox(full, alt);
    });

    if (closeBtn) closeBtn.addEventListener("click", closeLightbox);
    if (dialog) {
      dialog.addEventListener("click", (ev) => {
        if (!dialogImg) return;
        const rect = dialogImg.getBoundingClientRect();
        const inside = ev.clientX >= rect.left && ev.clientX <= rect.right && ev.clientY >= rect.top && ev.clientY <= rect.bottom;
        if (!inside) closeLightbox();
      });
    }
  }

  function initCountdown() {
    const daysEl = document.getElementById("countdownValue"); // matches index.html
    if (!daysEl) return;

    const target = new Date(String(CONFIG.startIso || "2026-11-27T16:00:00-06:00"));

    function tick() {
      const now = new Date();
      const ms = target.getTime() - now.getTime();
      const days = Math.max(0, Math.ceil(ms / (1000 * 60 * 60 * 24)));
      daysEl.textContent = String(days);
    }

    tick();
    setInterval(tick, 60 * 1000);
  }

  function initRsvpForm() {
    const form = document.getElementById("rsvpForm");
    const out = document.getElementById("rsvpOutput");
    const box = document.getElementById("messageBox");
    const smsBtn = document.getElementById("smsBtn");
    const smsBtnEs = document.getElementById("smsBtnEs");
    const copyBtn = document.getElementById("copyBtn");
    const copyBtnEs = document.getElementById("copyBtnEs");

    if (!form || !out || !box) return;

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
      return "sms:" + PHONE_E164 + "?&body=" + encodeURIComponent(message);
    }

    async function copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (e) {
        return false;
      }
    }

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

    if (copyBtn) copyBtn.addEventListener("click", () => copyToClipboard(box.textContent || ""));
    if (copyBtnEs) copyBtnEs.addEventListener("click", () => copyToClipboard(box.textContent || ""));
  }

  // Boot
  document.addEventListener("DOMContentLoaded", () => {
    const lang = setLanguage(getSavedLang());

    // Wire up language buttons
    const btns = Array.from(document.querySelectorAll(".lang-btn"));
    btns.forEach((b) => b.addEventListener("click", () => {
      setLanguage(b.dataset.lang);
      applyBindings();
    }));

    applyBindings();
    initCountdown();
    initRsvpForm();

    try { initGallery(); } catch (e) { /* fail soft */ }
  });

})();

