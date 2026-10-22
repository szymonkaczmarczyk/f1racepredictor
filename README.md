# Race Predictor

**Polski** · [English](README.en.md)

<img src="src/app/static/brand/logo-light.png" alt="Race Predictor" width="220">

> Przewiduje podium Grand Prix Formuły 1 na podstawie trzech dekad prawdziwych wyników i pokazuje, skąd bierze każdą liczbę.

Race Predictor to aplikacja webowa, która przed każdym wyścigiem F1 liczy szanse każdego kierowcy na wygraną,
podium, punkty i nieukończenie wyścigu. Bierze pod uwagę pole startowe, aktualną formę kierowcy i bolidu, historię
kierowcy na danym torze, charakter toru, pogodę i treningi z weekendu. Wszystkie prawdopodobieństwa pochodzą z
20 000 symulowanych wyścigów, więc zawsze są ze sobą spójne. Do tego prognoza mistrzostw do końca sezonu,
scenariusze „co jeśli” i historia trafności, w której aplikacja sama ocenia swoje wcześniejsze predykcje.

Pod spodem: Python, Flask i scikit-learn, a frontend w czystym HTML, CSS i JavaScript, bez frameworka i bez kroku
budowania. Dane pobierają się same z publicznych źródeł (Jolpica-F1, OpenF1, FastF1, Open-Meteo), a aplikacja
w tle pilnuje kalendarza, pobiera wyniki i douczy model po każdym wyścigu. Interfejs jest w ośmiu językach.

![Strona główna Race Predictor: tor Sepang, warunki wyścigu i przewidywane pola startowe](docs/screenshots/home.png)

## Dla kogo

- **Dla kibiców F1**, którzy przed weekendem chcą wiedzieć, kto realnie walczy o podium i dlaczego. Każdy
  kierowca ma krótkie uzasadnienie: forma, tempo bolidu, wyniki na tym torze, ryzyko awarii.
- **Dla osób uczących się data science**, które szukają uczciwie zwalidowanego modelu na danych czasowych:
  bez przecieków z przyszłości, z walidacją sezon po sezonie i porównaniem z prostym punktem odniesienia.
  Pełny opis modelu jest w [`docs/model.md`](docs/model.md).
- **Dla integratorów**, którzy chcą pobierać predykcje przez API — dokumentacja w
  [`docs/api-documentation.pdf`](docs/api-documentation.pdf).

Nie jest to narzędzie bukmacherskie ani porada do zakładów. Model nie „przechytrzy” kwalifikacji: w F1 pole
startowe jest najsilniejszym pojedynczym sygnałem, a aplikacja dokłada do niego skalibrowane prawdopodobieństwa.
To też nie jest oficjalny produkt Formuły 1.

## Jak to działa

```
Jolpica-F1  ─┐
OpenF1      ─┤                                       ┌─► features.csv ──────────┐
FastF1      ─┼─► scripts/01*_fetch ─► data/raw ─► 02_build_features              ├─► 03_train ─► models/podium_model.joblib
Open-Meteo  ─┤                                       └─► features_prequali.csv ─┘
f1-circuits ─┘

Przeglądarka ──► Flask (src/app/server.py)
                   ├──► /             interfejs (HTML + CSS + JS, 8 języków)
                   ├──► /api/*        JSON API: kalendarz, grid, predykcja, mistrzostwa, historia trafności
                   └──► wątek w tle   co 15 min: synchronizacja danych (src/pipeline.py)
                                      i zapis predykcji przed wyścigiem (data/ledger/)
```

**Dane.** Skrypty `01*` pobierają wyniki, kwalifikacje, sprinty, pit stopy, treningi, przebieg wyścigów, safety
cary i pogodę od 1996 roku, z pamięcią podręczną w `data/raw`. `02_build_features` przechodzi przez historię
chronologicznie i dla każdego bolidu w każdym wyścigu buduje 72 cechy z tego, co było wiadomo **przed startem**.
`03_train` trenuje model i waliduje go sezon po sezonie.

**Predykcja** jednego wyścigu przebiega tak:

1. Aplikacja ustala pola startowe: przed kwalifikacjami przewidywane (mediana straty do pole z trzech ostatnich
   kwalifikacji, po treningach połączona z tempem z treningów), po kwalifikacjach ich wynik, a gdy OpenF1 opublikuje
   oficjalny grid — kolejność z karami.
2. Trzy klasyfikatory gradient boosting oceniają każdy bolid: szansa na wygraną, podium i punkty.
3. Każda ocena jest łączona z tym, ile historycznie był wart start z danego pola. Przed kwalifikacjami działa osobny
   model, trenowany na przewidywanych gridach, który mocniej waży formę i historię toru.
4. Całość przechodzi przez 20 000 symulowanych wyścigów z losowaniem awarii, wypadków i dyskwalifikacji. Z tej
   jednej symulacji pochodzą wszystkie liczby na ekranie.

**Weekend wyścigowy** obsługuje się sam:

1. Tydzień przed wyścigiem aplikacja zapisuje pierwszą predykcję w historii trafności.
2. Po treningach (piątek) zapisuje nową wersję z gridem uwzględniającym treningi.
3. Po kwalifikacjach (sobota) — wersję z wynikiem kwalifikacji, a gdy pojawią się kary — z oficjalnym gridem.
4. W chwili startu predykcja zostaje zamrożona.
5. Po wyścigu synchronizacja pobiera wynik, douczy model i ocenia każdą wersję predykcji osobno.

## Model w skrócie

- **Cechy** (72): pole startowe i strata w kwalifikacjach; forma kierowcy i bolidu z wygasaniem (0,93 na wyścig);
  bilans z partnerem z zespołu; historia kierowcy na tym torze względem jego zwykłej formy; charakter toru (jak
  bardzo miesza kolejność, jak często wygrywa pole, ile bolidów odpada); pogoda mierzona w archiwum Open-Meteo;
  tempo z treningów; pozycja względem reszty stawki (ile szybszych bolidów startuje przed tobą).
- **Starsze wyścigi liczą się mniej:** waga `0,5 ^ (lata wstecz / 8)`. Na początku każdej nowej ery przepisów
  technicznych forma zespołów jest wygaszana do 30%.
- **Walidacja** zawsze „do przodu”: model dla sezonu S uczy się tylko na sezonach przed S. Wyniki 2014–2026
  (267 wyścigów):

| | model | sama kolejność startowa |
|---|---|---|
| trafione miejsca na podium | **69,7%** | 68,9% |
| trafiony zwycięzca | **55,8%** | 54,3% (pole position) |
| dokładnie trafione podium | **30,0%** | 28,1% |

- **Przed kwalifikacjami** (grid przewidywany, nie znany):

| | model przedkwalifikacyjny | model po kwalifikacjach | sam przewidywany grid |
|---|---|---|---|
| trafione miejsca na podium | **60,0%** | 59,2% | 58,8% |
| trafiony zwycięzca | **42,1%** | 37,1% | 35,9% |
| podium inne niż na gridzie | 24% wyścigów | 7% wyścigów | — |

- **Sprawdzone i odrzucone**, bo walidacja nie pokazała poprawy: ciągłość historii zespołów po zmianie nazwy
  (np. Sauber → Audi), wyniki sprintów, częstość safety cara jako cecha modelu, ograniczenia monotoniczne.

Wszystkie szczegóły, liczby i powody decyzji: [`docs/model.md`](docs/model.md).

## Funkcje

**Interfejs**

| Część | Co robi |
|---|---|
| Tor i warunki wyścigu | Wybór sezonu i toru, mapa toru z numerami zakrętów, trudność, zużycie opon, dystans, pogoda (z prognozy dla najbliższego wyścigu), statystyki toru, w tym safety car |
| Pola startowe | Grid ustawiany automatycznie, z etykietą źródła; pasek w kolorze zespołu; historia kierowcy na tym torze; przyciski ▲/▼ do scenariuszy „co jeśli” |
| Przewidywany wynik | Podium z szansami, pełna kolejność, szansa na wygraną i DNF, „samo pole startowe” dla porównania, krótkie uzasadnienie przy każdym kierowcy |
| Udostępnij podium | Obrazek 1200×630 do mediów społecznościowych (na telefonie menu udostępniania, na komputerze plik PNG) |
| Prognoza mistrzostw | 20 000 symulowanych sezonów: oczekiwane punkty, zakres i szansa na tytuł dla kierowców i konstruktorów |
| Jak to działa | Opis modelu, walidacja sezon po sezonie, historia trafności z podziałem na etapy weekendu |
| Wyścig rozegrany | Predykcja „z dnia przed wyścigiem” obok faktycznego wyniku |

Do tego ciemny i jasny motyw (zapamiętywany), osiem języków (polski, angielski, niemiecki, hiszpański,
francuski, włoski, niderlandzki, portugalski brazylijski), pełna obsługa telefonu z przyklejonym przyciskiem
„Przewiduj podium” na dole ekranu oraz szkielety ładowania i wskaźniki postępu przy każdym wczytywaniu.

**Strony**

| Adres | Co to jest |
|---|---|
| `/` | Aplikacja z prognozami |
| `/privacy` | Polityka prywatności (8 języków) |
| `/terms` | Regulamin (8 języków) |
| każdy inny adres | Strona 404 „Wypadłeś z toru” z powrotem do prognoz |
| `/robots.txt`, `/sitemap.xml` | Dla wyszukiwarek: wszystkie strony we wszystkich językach z wersjami `hreflang` |

Każda strona ma własny tytuł, opis, adres kanoniczny i znaczniki Open Graph / Twitter z obrazkiem 1200×630
([`og-image.png`](src/app/static/brand/og-image.png)), w każdym z 8 języków (`?lang=pl`, `?lang=de`…). Strona główna
ma dane strukturalne schema.org (`WebApplication`), a tytuł karty zmienia się z wybranym wyścigiem. Wszystkie strony
mają wspólny nagłówek z wyborem języka i motywu oraz stopkę z linkami do polityki prywatności, regulaminu,
źródeł danych i zastrzeżeniem o znakach towarowych.

**API**

| Endpoint | Co zwraca |
|---|---|
| `GET /api/bootstrap` | Tory, kierowcy, zespoły, kalendarz, najbliższy wyścig z pogodą, stan synchronizacji, wyniki walidacji |
| `GET /api/track/{circuit_id}` | Pełny opis toru z obrysem do mapy |
| `GET /api/lineup` | Pola startowe dla wyścigu i ich źródło |
| `GET /api/driver/{driver_id}` | Profil kierowcy z wynikami na każdym torze |
| `POST /api/predict` | Predykcja wyścigu dla podanego gridu |
| `GET /api/championship` | Prognoza mistrzostw do końca sezonu |
| `GET /api/ledger` | Historia trafności |
| `POST /api/sync` | Ręczna synchronizacja danych |

## Zrzuty ekranu

| Pola startowe | Przewidywany wynik |
|---|---|
| ![Mapa toru Sepang, warunki wyścigu i przewidywane pola startowe z kolorami zespołów](docs/screenshots/home.png) | ![Podium z szansami i pełna przewidywana kolejność z uzasadnieniami](docs/screenshots/results.png) |

| Prognoza mistrzostw | Scenariusz „co jeśli” |
|---|---|
| ![Oczekiwane punkty, zakres i szanse na tytuł kierowców i konstruktorów](docs/screenshots/championship.png) | ![Grid zmieniony ręcznie: Verstappen z pole position, Russell na P10, etykieta „What-if grid”](docs/screenshots/whatif.png) |

| Wyścig rozegrany, jasny motyw | Jak to działa |
|---|---|
| ![Predykcja Baku z dnia przed wyścigiem obok faktycznych wyników](docs/screenshots/backtest-light.png) | ![Walidacja sezon po sezonie i historia trafności](docs/screenshots/about.png) |

| Telefon — start | Telefon — wynik |
|---|---|
| ![Widok na telefonie: nagłówek, wybór języka, tor i przyklejony przycisk Predict the podium](docs/screenshots/mobile-home.png) | ![Widok na telefonie: podium i kolejność](docs/screenshots/mobile-results.png) |

| Polityka prywatności | Strona 404 |
|---|---|
| ![Polityka prywatności z nagłówkiem, wyborem języka i stopką](docs/screenshots/privacy.png) | ![Strona 404 Off the track z przyciskiem powrotu do prognoz](docs/screenshots/notfound.png) |

Zrzuty pokazują interfejs w wersji angielskiej (język zmienia się w nagłówku, dostępny jest też polski) i prawdziwy
sezon 2026 w stanie na 1 października 2026 (przed Grand Prix w Sepang).

## Uruchomienie

Wymagany Python 3.12. [uv](https://docs.astral.sh/uv/) instaluje go bez uprawnień administratora:

```bash
pip install uv
uv venv .venv --python 3.12
uv pip install --python .venv -r requirements.txt
```

Pierwsze uruchomienie pobiera całą historię i trenuje model (ok. godziny, głównie przez limity źródeł danych;
skrypty można przerwać i wznowić). `py` oznacza `.venv/bin/python`:

```bash
py scripts/01_fetch_data.py            # wyścigi, wyniki, kwalifikacje, sprinty, pogoda (~5 min)
py scripts/01b_fetch_pitstops.py       # pit stopy od 2011 (~15 min)
py scripts/01c_fetch_practice.py       # treningi od 2018 (~25 min)
py scripts/01d_fetch_race_laps.py      # przebieg wyścigów, ostatnie 3 sezony (~10 min)
py scripts/01e_fetch_track_status.py   # safety cary i czerwone flagi od 2018 (~2 min)
py scripts/02_build_features.py        # katalog torów i macierz cech
py scripts/03_train.py                 # trening i walidacja
py scripts/run_app.py                  # http://127.0.0.1:5050
```

Potem aplikacja sama aktualizuje dane co 15 minut, gdy jest taka potrzeba (wyścig bez wyników, kwalifikacje bez
gridu albo ostatnia synchronizacja starsza niż 12 godzin).

| Skrypt | Co robi |
|---|---|
| `scripts/run_app.py` | Uruchamia aplikację z synchronizacją w tle |
| `scripts/sync.py` | Jednorazowa synchronizacja; `--full` z pełną walidacją modelu |
| `scripts/weekend_status.py` | Stan najbliższego weekendu: treningi, źródło gridu, zapis predykcji, synchronizacja; `--record` zapisuje predykcję |
| `scripts/06_smoke_test.py` | Sprawdza wszystkie endpointy używane przez interfejs |
| `scripts/04_tune.py` | Porównanie konfiguracji modelu |
| `scripts/05_diagnose.py` | Gdzie model zmienia kolejność względem gridu i czy ma rację |
| `scripts/make_brand_assets.py` | Logo, favicon i ikony z plików w `branding/` |
| `py -m unittest discover -s tests` | Testy (kilka sekund) |

### Docker

```bash
cp .env.example .env    # ustaw F1_TRUSTED_HOSTS na swoją domenę
docker compose up -d --build
```

Dwa kontenery z jednego obrazu (Python 3.12, gunicorn, użytkownik bez uprawnień roota): `web` tylko serwuje
aplikację na `127.0.0.1:8000`, `sync` co 15 minut uruchamia `scripts/sync.py`. Dzielą katalogi `data/` i `models/`.
Na serwerze publicznym ustaw reverse proxy z HTTPS; na Linuksie daj użytkownikowi kontenera (uid 10001) prawo
zapisu do tych katalogów.

## Konfiguracja

Zmienne środowiskowe (dla `docker compose` w pliku `.env`, wzór w `.env.example`):

| Zmienna | Domyślnie | Opis |
|---|---|---|
| `F1_TRUSTED_HOSTS` | `127.0.0.1,localhost` | Hosty, którym serwer odpowiada. **Ustaw na swoją domenę przed wdrożeniem.** |
| `F1_PORT` | `5050` | Port dla `scripts/run_app.py` |
| `F1_AUTO_SYNC` | `1` | Synchronizacja w tle wewnątrz aplikacji (w Dockerze wyłączona, robi to kontener `sync`) |
| `F1_SYNC_ENDPOINT` | `1` | Czy wolno wywołać `POST /api/sync` (w Dockerze wyłączone) |
| `F1_SEASON` | bieżący rok | Nadpisanie sezonu, do testów |
| `F1_SITE_URL` | `https://f1racepredictor.com` | Adres strony: adresy kanoniczne, Open Graph, sitemap |
| `F1_OPERATOR_NAME`, `F1_OPERATOR_ADDRESS` | `[OPERATOR NAME]`… | Administrator danych i usługodawca w polityce prywatności i regulaminie. **Uzupełnij przed publikacją.** |
| `F1_CONTACT_EMAIL` | `[CONTACT EMAIL]` | E-mail kontaktowy na stronach prawnych |
| `F1_GOVERNING_COUNTRY` | `[COUNTRY]` | Prawo właściwe w regulaminie |
| `F1_HOSTING_PROVIDER` | `[HOSTING PROVIDER]` | Dostawca hostingu w polityce prywatności |
| `F1_LOG_RETENTION_DAYS` | `30` | Po ilu dniach usuwasz logi serwera (tak musi być też u hostingu) |
| `F1_LEGAL_UPDATED` | `2026-10-01` | Data ostatniej aktualizacji stron prawnych |

Aplikacja nie potrzebuje żadnych kluczy API ani bazy danych: wszystko jest w plikach w `data/` i `models/`.

## Struktura

```
src/
  config.py            okno danych, tempo wygasania formy, sezony walidacji
  pipeline.py          synchronizacja: pobranie, przebudowa cech, douczenie modelu
  ledger.py            historia trafności: zapis predykcji i ocena po wyścigu
  ingest/              pobieranie danych: Jolpica, OpenF1, FastF1, Open-Meteo, kalendarz, tory
  features/            cechy: chronologiczny przebieg, wygasanie, grid przedkwalifikacyjny, profile
  models/              trening i walidacja, symulacja wyścigu, predykcja, mistrzostwa, backtest
  app/
    server.py          API
    site.py            strony, meta w 8 językach, robots.txt, sitemap.xml, strona 404
    security.py        zabezpieczenia i nagłówki
    templates/         base.html (nagłówek, meta, stopka), strona główna, strony prawne, 404
    templates/legal/   treść polityki prywatności i regulaminu, po jednym pliku na język
    static/            app.js (aplikacja), site.js (wspólne dla stron), i18n.js, app.css
    static/i18n/       teksty interfejsu w 8 językach
    static/brand/      logo, favicon, ikony, obrazek Open Graph
    static/fonts/      czcionka Titillium Web (WOFF) z licencją OFL
scripts/               pobieranie danych, trening, synchronizacja, narzędzia
tests/                 testy jednostkowe i API
branding/              źródłowe pliki logo i czcionki (TTF)
data/                  dane pobrane i przetworzone, obrysy torów, historia trafności (w repo tylko obrysy)
models/                wytrenowany model i raporty walidacji (w repo tylko raporty)
docs/
  api-documentation.pdf / .html   dokumentacja API
  model.md                        szczegółowy opis danych, cech, modelu i walidacji (po angielsku)
  screenshots/                    zrzuty ekranu do README (wersja angielska interfejsu)
```

## Bezpieczeństwo

- Serwer odpowiada tylko hostom z `F1_TRUSTED_HOSTS`; obce nagłówki `Host` dostają `400`.
- Żądania POST z innej strony są odrzucane (`Origin` / `Sec-Fetch-Site`), limit treści to 64 kB.
- Nagłówki: Content Security Policy (skrypty tylko z serwera aplikacji i z sumą kontrolną), `X-Frame-Options: DENY`,
  `nosniff`, `Referrer-Policy: no-referrer`; API z `Cache-Control: no-store`.
- Walidacja wszystkich danych wejściowych predykcji; wszystko, co trafia do HTML, jest escapowane.
- Synchronizacja ma blokadę plikową (nigdy dwie naraz) i minimalny odstęp 60 sekund przy wywołaniu ręcznym.
- Aplikacja nie zbiera danych osobowych, nie ma kont, nie ustawia cookies i nie ma analityki. Wszystkie pliki
  (skrypty, czcionki, obrazy) idą z własnego serwera, więc przeglądarka odwiedzającego nie łączy się z nikim innym.
- `robots.txt` wyłącza `/api/` z indeksowania; strona 404 ma `noindex`.

## Wydajność

Czcionki są przycięte do znaków łacińskich (ok. 25 KB na wagę) i wczytywane wstępnie, z `font-display: swap`.
Predykcja jednego wyścigu to ułamek sekundy. Prognoza mistrzostw liczy się ok. 5 sekund i jest trzymana w pamięci,
dopóki nie zmienią się dane albo model. Predykcja wyścigu rozegranego za pierwszym razem trenuje model „z dnia przed
wyścigiem” i zapisuje go w `models/backtest/`, kolejne są natychmiastowe. Pobrane dane są w pamięci podręcznej,
więc synchronizacja ściąga tylko bieżący sezon.

## Licencje i zastrzeżenia — przed publikacją

- **Formuła 1, F1 i nazwy zespołów** są znakami towarowymi ich właścicieli. Aplikacja nie używa oficjalnych logo,
  zdjęć ani czcionek F1; kolory zespołów służą tylko do rozróżnienia. Nie jest powiązana z Formula One Group ani FIA.
- **Źródła danych** mają własne warunki: Jolpica-F1, OpenF1 i dane czasowe F1 przez FastF1 są nieoficjalne;
  Open-Meteo wymaga podania źródła (CC BY 4.0) i bezpłatnie jest przeznaczone do użytku niekomercyjnego; obrysy
  torów pochodzą z [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits). Przed komercyjnym użyciem
  sprawdź aktualne warunki każdego z nich.
- **Polityka prywatności i regulamin** mają placeholdery (`[OPERATOR NAME]`, `[CONTACT EMAIL]`, `[COUNTRY]`,
  `[HOSTING PROVIDER]`) — uzupełnij je w `.env` (patrz *Konfiguracja*). Teksty opisują aplikację w obecnym kształcie;
  jeśli dodasz analitykę, cookies albo formularze, trzeba je zaktualizować. Przed publikacją warto, żeby przejrzał
  je prawnik — to rzetelny punkt wyjścia, a nie porada prawna.
- **Czcionka Titillium Web** jest na licencji SIL Open Font License; plik licencji leży obok czcionek
  (`static/fonts/OFL.txt`, `branding/fonts/OFL.txt`).
- Licencja MIT obejmuje tylko kod tego repozytorium. Nie obejmuje danych z zewnętrznych źródeł, nazw i znaków
  towarowych F1 ani fontów, które mają własne licencje.

## Dokumentacja

- [`README.en.md`](README.en.md) - ten dokument po angielsku.
- [`docs/api-documentation.pdf`](docs/api-documentation.pdf) — wszystkie endpointy: parametry, przykłady żądań i
  odpowiedzi, kody błędów.
- [`docs/model.md`](docs/model.md) — źródła danych, wszystkie cechy, trening, walidacja, odrzucone eksperymenty,
  symulacja wyścigu, logika kalendarza i ograniczenia modelu.

## Licencja

[MIT](LICENSE) © 2026 Szymon Kaczmarczyk
