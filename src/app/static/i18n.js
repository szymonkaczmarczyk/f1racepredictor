"use strict";

const STRINGS = {};

const LANGUAGES = [
  { code: "en", name: "English", locale: "en-GB" },
  { code: "pl", name: "Polski", locale: "pl-PL" },
  { code: "de", name: "Deutsch", locale: "de-DE" },
  { code: "es", name: "Español", locale: "es-ES" },
  { code: "fr", name: "Français", locale: "fr-FR" },
  { code: "it", name: "Italiano", locale: "it-IT" },
  { code: "nl", name: "Nederlands", locale: "nl-NL" },
  { code: "pt", name: "Português (Brasil)", locale: "pt-BR" },
];
const LANG_CODES = LANGUAGES.map((l) => l.code);

const I18N = {
  lang: (() => {
    const requested = new URLSearchParams(location.search).get("lang");
    if (LANG_CODES.includes(requested)) {
      try { localStorage.setItem("lang", requested); } catch (e) {}
      return requested;
    }
    try {
      const saved = localStorage.getItem("lang");
      if (LANG_CODES.includes(saved)) return saved;
    } catch (e) {}
    const wanted = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (const tag of wanted) {
      const code = String(tag).toLowerCase().split("-")[0];
      if (LANG_CODES.includes(code)) return code;
    }
    return "en";
  })(),
};

function locale() {
  return (LANGUAGES.find((l) => l.code === I18N.lang) || LANGUAGES[0]).locale;
}

const pluralRules = {};

function plural(n, forms) {
  const tag = locale();
  pluralRules[tag] = pluralRules[tag] || new Intl.PluralRules(tag);
  const category = pluralRules[tag].select(n);
  const last = forms.length - 1;
  if (category === "one") return forms[0];
  if (category === "few" && forms.length > 2) return forms[1];
  return forms[last];
}

function t(key, vars = {}) {
  const entry = (STRINGS[I18N.lang] || {})[key] ?? STRINGS.en[key];
  if (entry === undefined) return key;
  return typeof entry === "function" ? entry(vars) : entry;
}

function setLang(lang) {
  I18N.lang = LANG_CODES.includes(lang) ? lang : "en";
  try { localStorage.setItem("lang", I18N.lang); } catch (e) {}
  applyStaticText();
}

function applyStaticText() {
  document.documentElement.lang = I18N.lang;
  for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = t(el.dataset.i18n);
  for (const el of document.querySelectorAll("[data-i18n-title]")) {
    el.title = t(el.dataset.i18nTitle);
    el.setAttribute("aria-label", t(el.dataset.i18nTitle));
  }
}

function pctText(v, digits = 0) {
  return v == null ? "—" : `${(v * 100).toFixed(digits)}%`;
}

function signedNum(v) {
  return `${v >= 0 ? "+" : ""}${v.toFixed(1)}`;
}
