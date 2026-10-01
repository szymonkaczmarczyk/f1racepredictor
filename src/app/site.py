from __future__ import annotations

import json
from datetime import date
from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app, jsonify, render_template, request, send_from_directory, url_for

from src import pipeline
from src.config import LANGUAGES, LEGAL, SITE_NAME, SITE_URL

site = Blueprint("site", __name__)

PAGES = {"home": "/", "privacy": "/privacy", "terms": "/terms"}

OG_LOCALES = {
    "en": "en_GB", "pl": "pl_PL", "de": "de_DE", "es": "es_ES",
    "fr": "fr_FR", "it": "it_IT", "nl": "nl_NL", "pt": "pt_BR",
}

META = {
    "en": {
        "home": ("Race Predictor — F1 podium predictions for every Grand Prix",
                 "Who will finish on the podium? Win, podium and points odds for every Formula 1 driver from 20,000 simulated races, with form, track history, qualifying and weather, plus the championship outlook."),
        "privacy": ("Privacy policy · Race Predictor",
                    "How Race Predictor handles data: no accounts, no cookies, no tracking."),
        "terms": ("Terms of use · Race Predictor",
                  "Terms for using Race Predictor, a free Formula 1 prediction tool."),
        "notfound": ("Page not found · Race Predictor",
                     "This page does not exist. Go back to the F1 podium predictions."),
    },
    "pl": {
        "home": ("Race Predictor — prognozy podium F1 na każde Grand Prix",
                 "Kto stanie na podium? Szanse na wygraną, podium i punkty dla każdego kierowcy Formuły 1 z 20 000 symulowanych wyścigów: forma, historia toru, kwalifikacje i pogoda oraz prognoza mistrzostw."),
        "privacy": ("Polityka prywatności · Race Predictor",
                    "Jak Race Predictor obchodzi się z danymi: bez kont, bez cookies, bez śledzenia."),
        "terms": ("Regulamin · Race Predictor",
                  "Zasady korzystania z Race Predictor, bezpłatnego narzędzia do prognoz Formuły 1."),
        "notfound": ("Nie znaleziono strony · Race Predictor",
                     "Ta strona nie istnieje. Wróć do prognoz podium F1."),
    },
    "de": {
        "home": ("Race Predictor – F1-Podiumsprognosen für jeden Grand Prix",
                 "Wer steht auf dem Podium? Sieg-, Podiums- und Punktechancen für jeden Formel-1-Fahrer aus 20.000 simulierten Rennen – mit Form, Streckenhistorie, Qualifying und Wetter sowie der WM-Prognose."),
        "privacy": ("Datenschutzerklärung · Race Predictor",
                    "Wie Race Predictor mit Daten umgeht: keine Konten, keine Cookies, kein Tracking."),
        "terms": ("Nutzungsbedingungen · Race Predictor",
                  "Bedingungen für die Nutzung von Race Predictor, einem kostenlosen Formel-1-Prognosetool."),
        "notfound": ("Seite nicht gefunden · Race Predictor",
                     "Diese Seite gibt es nicht. Zurück zu den F1-Podiumsprognosen."),
    },
    "es": {
        "home": ("Race Predictor — predicciones del podio de F1 para cada Gran Premio",
                 "¿Quién subirá al podio? Probabilidades de victoria, podio y puntos para cada piloto de Fórmula 1 a partir de 20 000 carreras simuladas, con forma, historial del circuito, clasificación y meteorología, además de la previsión del Mundial."),
        "privacy": ("Política de privacidad · Race Predictor",
                    "Cómo trata Race Predictor los datos: sin cuentas, sin cookies, sin seguimiento."),
        "terms": ("Condiciones de uso · Race Predictor",
                  "Condiciones para usar Race Predictor, una herramienta gratuita de predicciones de Fórmula 1."),
        "notfound": ("Página no encontrada · Race Predictor",
                     "Esta página no existe. Vuelve a las predicciones del podio de F1."),
    },
    "fr": {
        "home": ("Race Predictor — pronostics du podium F1 pour chaque Grand Prix",
                 "Qui montera sur le podium ? Chances de victoire, de podium et de points pour chaque pilote de Formule 1 à partir de 20 000 courses simulées, avec la forme, l'historique du circuit, les qualifications et la météo, plus la prévision du championnat."),
        "privacy": ("Politique de confidentialité · Race Predictor",
                    "Comment Race Predictor traite les données : pas de compte, pas de cookies, pas de pistage."),
        "terms": ("Conditions d'utilisation · Race Predictor",
                  "Conditions d'utilisation de Race Predictor, un outil gratuit de pronostics de Formule 1."),
        "notfound": ("Page introuvable · Race Predictor",
                     "Cette page n'existe pas. Retour aux pronostics du podium F1."),
    },
    "it": {
        "home": ("Race Predictor — previsioni del podio F1 per ogni Gran Premio",
                 "Chi salirà sul podio? Probabilità di vittoria, podio e punti per ogni pilota di Formula 1 da 20.000 gare simulate, con forma, storico del circuito, qualifiche e meteo, più la previsione del Mondiale."),
        "privacy": ("Informativa sulla privacy · Race Predictor",
                    "Come Race Predictor tratta i dati: nessun account, nessun cookie, nessun tracciamento."),
        "terms": ("Termini d'uso · Race Predictor",
                  "Termini per l'uso di Race Predictor, uno strumento gratuito di previsioni di Formula 1."),
        "notfound": ("Pagina non trovata · Race Predictor",
                     "Questa pagina non esiste. Torna alle previsioni del podio F1."),
    },
    "nl": {
        "home": ("Race Predictor — F1-podiumvoorspellingen voor elke Grand Prix",
                 "Wie staat er op het podium? Kansen op winst, podium en punten voor elke Formule 1-coureur uit 20.000 gesimuleerde races, met vorm, circuithistorie, kwalificatie en weer, plus de kampioenschapsprognose."),
        "privacy": ("Privacybeleid · Race Predictor",
                    "Hoe Race Predictor met gegevens omgaat: geen accounts, geen cookies, geen tracking."),
        "terms": ("Gebruiksvoorwaarden · Race Predictor",
                  "Voorwaarden voor het gebruik van Race Predictor, een gratis Formule 1-voorspellingstool."),
        "notfound": ("Pagina niet gevonden · Race Predictor",
                     "Deze pagina bestaat niet. Terug naar de F1-podiumvoorspellingen."),
    },
    "pt": {
        "home": ("Race Predictor — previsões de pódio da F1 para cada Grande Prêmio",
                 "Quem vai ao pódio? Chances de vitória, pódio e pontos para cada piloto da Fórmula 1 a partir de 20.000 corridas simuladas, com fase, histórico no circuito, classificação e clima, além da previsão do campeonato."),
        "privacy": ("Política de privacidade · Race Predictor",
                    "Como o Race Predictor trata os dados: sem contas, sem cookies, sem rastreamento."),
        "terms": ("Termos de uso · Race Predictor",
                  "Termos para usar o Race Predictor, uma ferramenta gratuita de previsões da Fórmula 1."),
        "notfound": ("Página não encontrada · Race Predictor",
                     "Esta página não existe. Volte para as previsões de pódio da F1."),
    },
}


def page_lang() -> str:
    lang = request.args.get("lang")
    return lang if lang in LANGUAGES else "en"


def localized(path: str, lang: str) -> str:
    return SITE_URL + path + ("" if lang == "en" else f"?lang={lang}")


def absolute_static(filename: str) -> str:
    return SITE_URL + url_for("static", filename=filename)


def page_context(page: str, lang: str) -> dict:
    title, description = META[lang][page]
    path = PAGES.get(page)
    return {
        "page": page,
        "lang": lang,
        "title": title,
        "description": description,
        "canonical": localized(path, lang) if path else None,
        "alternates": [(code, localized(path, code)) for code in LANGUAGES] if path else [],
        "x_default": SITE_URL + path if path else None,
        "og_locale": OG_LOCALES[lang],
        "og_alternates": [OG_LOCALES[code] for code in LANGUAGES if code != lang],
        "og_image": absolute_static("brand/og-image.png"),
        "og_image_alt": META[lang]["home"][0],
        "site_name": SITE_NAME,
        "site_url": SITE_URL,
        "structured_data": structured_data(lang) if page == "home" else None,
        "legal": LEGAL,
        "year": date.today().year,
        "languages": LANGUAGES,
    }


def structured_data(lang: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": SITE_NAME,
        "url": SITE_URL + "/",
        "description": META[lang]["home"][1],
        "applicationCategory": "SportsApplication",
        "operatingSystem": "Web",
        "inLanguage": list(LANGUAGES),
        "image": absolute_static("brand/og-image.png"),
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
    }
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


@site.get("/")
def home():
    return render_template("index.html", **page_context("home", page_lang()))


@site.get("/privacy")
def privacy():
    return render_template("legal.html", doc="privacy", **page_context("privacy", page_lang()))


@site.get("/terms")
def terms():
    return render_template("legal.html", doc="terms", **page_context("terms", page_lang()))


@site.get("/favicon.ico")
def favicon():
    return send_from_directory(current_app.static_folder, "brand/favicon.ico", mimetype="image/vnd.microsoft.icon")


@site.get("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@site.get("/sitemap.xml")
def sitemap():
    synced = (pipeline.last_state().get("last_success_utc") or "")[:10] or date.today().isoformat()
    modified = {"home": synced, "privacy": LEGAL["updated"], "terms": LEGAL["updated"]}
    rows = []
    for page, path in PAGES.items():
        links = "".join(
            f'<xhtml:link rel="alternate" hreflang="{code}" href="{escape(localized(path, code))}"/>'
            for code in LANGUAGES
        ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{escape(SITE_URL + path)}"/>'
        for code in LANGUAGES:
            rows.append(
                f"<url><loc>{escape(localized(path, code))}</loc><lastmod>{modified[page]}</lastmod>"
                f"<changefreq>{'daily' if page == 'home' else 'yearly'}</changefreq>"
                f"<priority>{'1.0' if page == 'home' and code == 'en' else '0.5'}</priority>{links}</url>"
            )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(rows) + "</urlset>\n"
    )
    return Response(body, mimetype="application/xml")


@site.app_errorhandler(404)
def not_found(exc):
    if request.path.startswith("/api/"):
        return jsonify({"error": exc.description or "not found"}), 404
    return render_template("404.html", **page_context("notfound", page_lang())), 404
