"use strict";

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => (
  { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
));

const SERVER_RENDERED_PAGES = ["privacy", "terms"];

function localizedHref(path, code) {
  return code === "en" ? path : `${path}?lang=${code}`;
}

function localizeLinks() {
  for (const link of document.querySelectorAll("a[data-path]")) {
    link.setAttribute("href", localizedHref(link.dataset.path, I18N.lang));
  }
}

function syncUrlLanguage() {
  const url = new URL(location.href);
  if (I18N.lang === "en") url.searchParams.delete("lang");
  else url.searchParams.set("lang", I18N.lang);
  history.replaceState(history.state, "", url);
}

function buildLanguageSelect() {
  const sel = $("lang-select");
  sel.innerHTML = LANGUAGES.map((l) => `<option value="${l.code}" lang="${l.code}">${esc(l.name)}</option>`).join("");
  sel.value = I18N.lang;
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("theme", next); } catch (e) {}
}

function setBusy(button, busy, label) {
  if (!button) return;
  button.classList.toggle("is-loading", busy);
  button.setAttribute("aria-busy", busy ? "true" : "false");
  button.disabled = busy;
  if (label !== undefined) button.textContent = label;
}

function initSite(onLanguageChange) {
  const page = document.body.dataset.page;
  if (SERVER_RENDERED_PAGES.includes(page) && I18N.lang !== document.body.dataset.pageLang) {
    location.replace(localizedHref(location.pathname, I18N.lang) + location.hash);
    return false;
  }
  buildLanguageSelect();
  applyStaticText();
  localizeLinks();
  if (page === "notfound") document.title = `${t("notfound.title")} · Race Predictor`;
  $("btn-theme").onclick = toggleTheme;
  $("lang-select").onchange = (e) => {
    const code = e.target.value;
    if (!onLanguageChange) {
      setLang(code);
      location.href = localizedHref(location.pathname, I18N.lang);
      return;
    }
    setLang(code);
    $("lang-select").value = I18N.lang;
    syncUrlLanguage();
    localizeLinks();
    onLanguageChange();
  };
  return true;
}

if (!["home"].includes(document.body.dataset.page)) initSite();
