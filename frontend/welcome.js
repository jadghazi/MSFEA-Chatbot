(() => {
  const dialog = document.getElementById("pilot-intro");
  const reopen = document.getElementById("pilot-intro-open");
  const start = dialog.querySelector(".pilot-intro-start");
  const storageKey = "msfea-pilot-intro-seen-v1";
  let openedFromBadge = false;

  function openIntro(fromBadge) {
    openedFromBadge = fromBadge;
    dialog.showModal();
    start.focus();
  }

  dialog.querySelector(".pilot-intro-close").addEventListener("click", () => dialog.close());
  start.addEventListener("click", () => dialog.close());
  reopen.addEventListener("click", () => openIntro(true));

  dialog.addEventListener("close", () => {
    try { localStorage.setItem(storageKey, "1"); } catch (_) { /* Browsing still works without storage. */ }
    const destination = openedFromBadge
      ? reopen
      : document.querySelector("#chat-app .msfea-dept") || document.getElementById("chat-app");
    destination.focus();
  });

  let seen = false;
  try { seen = localStorage.getItem(storageKey) === "1"; } catch (_) { /* Show the introduction when storage is unavailable. */ }
  if (!seen) openIntro(false);
})();
