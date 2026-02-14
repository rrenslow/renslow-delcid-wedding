(() => {
  const RSVP_ENDPOINT = "https://script.google.com/macros/s/AKfycbzyprsojsk2mBHC5pjMeQG11Ppld04OPeKvo7pFDCci_IkB45GapuCPC0hIT2lK7KqyOQ/exec";

  function getLang(){
    return document.documentElement.getAttribute("data-language") || "en";
  }

  function getSubmitBtn(form){
    const lang = getLang();
    return (
      form.querySelector('button[type="submit"][data-lang="' + lang + '"]') ||
      form.querySelector('button[type="submit"]')
    );
  }

  async function postRsvp(payload){
    // Send-only, opaque response (no-cors)
    await fetch(RSVP_ENDPOINT, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  function setButtonConfirmed(form){
    const btn = getSubmitBtn(form);
    if (!btn) return;

    const lang = getLang();
    btn.textContent = (lang === "es") ? "RSVP Confirmado" : "RSVP Confirmed";
    btn.disabled = true;
  }

  function setButtonError(form){
    const btn = getSubmitBtn(form);
    if (!btn) return;

    const lang = getLang();
    btn.textContent = (lang === "es") ? "RSVP (error)" : "RSVP (error)";
    btn.disabled = false;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#rsvpForm");
    if (!form) return;

    form.addEventListener("submit", () => {
      // Let your existing initRsvpForm() run first (it generates the message box)
      setTimeout(async () => {
        const payload = {
          ts: new Date().toISOString(),
          lang: getLang(),
          name: form.querySelector('input[name="name"]')?.value || "",
          attending: form.querySelector('select[name="attending"]')?.value || "",
          guests: form.querySelector('input[name="guests"]')?.value || "",
          diet: form.querySelector('input[name="diet"]')?.value || "",
          page: location.href,
        };

        try {
          await postRsvp(payload);
          setButtonConfirmed(form);
        } catch (e) {
          console.warn("RSVP post failed:", e);
          setButtonError(form);
        }
      }, 0);
    });
  });
})();
