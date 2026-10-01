"use strict";

STRINGS.pl = {
  "html.title": "Race Predictor",
  "model.loading": "wczytywanie modelu…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · model trenowany do ${trained}`,
  "model.next": ({ race, date }) => ` · następny: ${race}, ${date}`,
  "metric.hit": "trafność podium",
  "metric.grid": "sama kolejność startowa",
  "btn.about": "Jak to działa",
  "btn.theme": "Zmień motyw",
  "btn.lang": "Język",

  "track.title": "Tor i warunki wyścigu",
  "track.season": "Sezon",
  "season.2026": "2026 (symulacja)",
  "season.real": ({ year }) => `${year} (rozegrany)`,
  "track.select": "Tor",
  "track.calendar": "Kalendarz tego sezonu",
  "track.other": "Inne tory z historią",
  "track.street": " · tor uliczny",
  "track.no_map": "Brak obrysu tego toru.<br>Nie wpływa to na predykcję.",
  "track.layout": ({ name }) => `Układ toru ${name}`,
  "ro.difficulty": "Trudność toru",
  "ro.difficulty_note": "gęstość zakrętów, incydenty, bandy",
  "ro.deg": "Zużycie opon",
  "ro.deg_none": "brak świeżych danych",
  "ro.deg_pitstops": ({ window }) => `pit stopy ${window}`,
  "ro.deg_layout": "oszacowane z układu toru",
  "ro.distance": "Dystans wyścigu",
  "ro.corners": "Zakręty",
  "ro.laps": "Okrążenia",
  "weather.title": "Pogoda",
  "weather.dry": "Sucho",
  "weather.cloudy": "Pochmurno",
  "weather.light_rain": "Lekki deszcz",
  "weather.mixed": "Zmienna / przesychający tor",
  "weather.heavy_rain": "Ulewa",

  "stat.sticky": "Podium z pierwszych trzech pól",
  "stat.pole": "Pole position kończy się wygraną",
  "stat.dnf": "Odsetek nieukończonych wyścigów",
  "stat.gained": "Zyskane pozycje na wyścig",
  "stat.stops": "Pit stopy na bolid",
  "stat.sc": "Safety car lub czerwona flaga",
  "stat.sc_value": ({ pct, n }) => `${pct} z ${n} ${plural(n, ["wyścigu", "wyścigów", "wyścigów"])}`,
  "stat.deg": "Spadek tempa na okrążenie opony",
  "stat.length": "Długość okrążenia",
  "stat.measured": "Na podstawie",
  "stat.starts": ({ n }) => `ostatnich startów: ${n}`,

  "grid.title": "Pola startowe",
  "grid.col.grid": "Pole",
  "grid.col.driver": "Kierowca",
  "grid.col.team": "Zespół / bolid",
  "grid.col.history": "Na tym torze",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["bolid", "bolidy", "bolidów"])}.`,
  "grid.move_up": ({ name }) => `Przesuń ${name} w górę`,
  "grid.move_down": ({ name }) => `Przesuń ${name} w dół`,
  "history.none": "brak startów tutaj",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["start", "starty", "startów"])}`,
  "history.avg": ({ pos }) => `śr. <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podium", "podia", "podiów"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["wygrana", "wygrane", "wygranych"])}`,
  "driver.career": (c) => `Kariera: starty ${c.races}, wygrane ${c.wins}, podia ${c.podiums}, średnio na mecie P${c.avg}, DNF ${c.dnf}`,
  "driver.recent": (r) => `Sezony ${r.seasons}: średnio na starcie P${r.grid}, na mecie P${r.finish}, podium w ${r.rate} wyścigów`,
  "driver.season": (s) => `Ten sezon: starty ${s.races}, punkty ${s.points}, podia ${s.podiums}${s.best ? `, najlepiej P${s.best}` : ""}`,

  "source.race": "Faktyczne pola startowe",
  "source.race.hint": "Ten wyścig już się odbył. Predykcja korzysta tylko z tego, co było wiadomo dzień wcześniej, a obok widać prawdziwy wynik.",
  "source.starting_grid": "Oficjalne pola startowe",
  "source.starting_grid.hint": "Oficjalna kolejność startowa z OpenF1, z uwzględnionymi karami.",
  "source.qualifying": "Z kwalifikacji",
  "source.qualifying.hint": "Kolejność według oficjalnego wyniku kwalifikacji. Kary zostaną uwzględnione, gdy pojawi się oficjalna kolejność startowa.",
  "source.openf1": "Z kwalifikacji (OpenF1)",
  "source.openf1.hint": "Kolejność z kwalifikacji w OpenF1; oficjalne źródło jeszcze jej nie podało.",
  "source.expected_practice": "Przewidywane pola (z treningami)",
  "source.expected_practice.hint": "Kwalifikacje jeszcze się nie odbyły: kolejność łączy ostatnie straty kierowców w kwalifikacjach z ich najlepszym okrążeniem w treningach tego weekendu. Zaktualizuje się sama po kwalifikacjach.",
  "source.expected": "Przewidywane pola",
  "source.expected.hint": "Kwalifikacje jeszcze się nie odbyły: stawka jest ułożona według mediany straty do pole position z trzech ostatnich kwalifikacji. Zaktualizuje się sama po kwalifikacjach.",
  "source.what_if": "Scenariusz „co jeśli”",
  "source.what_if.hint": "Kolejność została zmieniona ręcznie. Predykcje z edytowanej kolejności nie trafiają do historii trafności.",

  "btn.sync": "Synchronizuj dane",
  "btn.syncing": "Synchronizuję…",
  "sync.done": "Dane zostały zsynchronizowane.",
  "sync.failed": ({ msg }) => `Synchronizacja nie powiodła się: ${msg}`,
  "btn.reset": "Przywróć kolejność",
  "btn.predict": "Przewiduj podium",
  "btn.predicting": "Liczę…",
  "predict.failed": ({ msg }) => `Predykcja nie powiodła się: ${msg}`,

  "results.title": "Przewidywany wynik",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · zużycie opon ${deg}/10`,
  "results.backtest": " · stan z dnia przed wyścigiem",
  "results.prequali": " · model przedkwalifikacyjny",
  "order.slot": ({ pct }) => `samo pole startowe ${pct}`,
  "place.1": "1. miejsce",
  "place.2": "2. miejsce",
  "place.3": "3. miejsce",
  "pod.from": ({ place, grid }) => `${place} · start z P${grid}`,
  "pod.chance": "szansa na podium",
  "order.pos": "Poz.",
  "order.driver": "Kierowca",
  "order.team": "Zespół",
  "order.prob": "Szansa na podium",
  "order.podium": "Podium",
  "order.win": "Wygrana",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `start z P${grid} · oczekiwana meta ${finish}`,
  "order.range": ({ a, b }) => ` · zwykle P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · faktycznie P${pos}`,
  "order.actual_dnf": " · faktycznie nie ukończył",
  "dnf.total": ({ pct }) => `Ryzyko nieukończenia ${pct}`,
  "dnf.crash": ({ pct }) => `  wypadek ${pct}`,
  "dnf.mech": ({ pct }) => `  awaria bolidu ${pct}`,
  "dnf.dsq": ({ pct }) => `  dyskwalifikacja ${pct}`,

  "note.grid_front": ({ grid }) => `startuje z P${grid}`,
  "note.grid_deep": ({ grid }) => `daleko w stawce, P${grid}`,
  "note.form": ({ pos }) => `ostatnia forma ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `bolid na podium w ${pctText(rate)} ostatnich startów`,
  "note.over_performs": ({ delta }) => `tu jeździ lepiej niż zwykle (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `tu zwykle słabiej (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podium", "podia", "podiów"])} na tym torze`,
  "note.reliability": ({ rate }) => `ryzyko awarii (${pctText(rate)} ostatnich startów bez mety)`,
  "note.crashed_here": ({ n }) => `odpadł tu po wypadku ${n} ${plural(n, ["raz", "razy", "razy"])}`,
  "note.crash_risk": ({ rate }) => `podwyższone ryzyko wypadku (${pctText(rate)})`,

  "btn.share": "Udostępnij podium",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · START Z P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · model trenowany do ${trained}`,
  "share.text": ({ list }) => `Przewidywane podium: ${list}`,
  "share.saved": ({ name }) => `Zapisano ${name}`,

  "champ.title": "Prognoza mistrzostw",
  "champ.chip": "reszta sezonu",
  "champ.hint": "Rozgrywa każdy pozostały wyścig tysiące razy modelem i sumuje punkty.",
  "champ.btn": "Symuluj resztę sezonu",
  "champ.running": "Symuluję…",
  "champ.retry": "Spróbuj ponownie",
  "champ.failed": ({ msg }) => `Symulacja nie powiodła się: ${msg}`,
  "champ.drivers": "Kierowcy",
  "champ.teams": "Konstruktorzy",
  "champ.left": ({ races, sprints }) => `zostało: ${races} ${plural(races, ["wyścig", "wyścigi", "wyścigów"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprinty", "sprintów"])}` : ""),
  "champ.done": "sezon zakończony",
  "champ.summary": ({ sims }) => `${sims} symulowanych sezonów od dzisiejszej klasyfikacji. Każdy wyścig korzysta z przewidywanych pól startowych i szans z modelu; `,
  "champ.sprints": "sprinty są liczone z tych samych szans.",
  "champ.no_sprints": "nie udało się sprawdzić weekendów ze sprintem, więc sprinty są pominięte.",
  "champ.final": "Nie zostały żadne wyścigi: to końcowa klasyfikacja.",
  "champ.now": "Teraz",
  "champ.driver": "Kierowca",
  "champ.team": "Zespół",
  "champ.expected": "Prognoza",
  "champ.title_col": "Tytuł",
  "champ.range": ({ a, b }) => `80% symulowanych sezonów kończy się między ${a} a ${b} pkt`,

  "record.title": "Historia trafności",
  "record.headline": ({ n, hit, grid, winner }) => `Ocenione wyścigi: ${n}. Trafione miejsca na podium: ${hit} (sama kolejność startowa: ${grid}), trafiony zwycięzca: ${winner}.`,
  "record.empty": "Żaden wyścig nie został jeszcze oceniony. Aplikacja zapisuje predykcję przed każdym wyścigiem i ocenia ją, gdy pojawi się wynik.",
  "record.by_source": "W zależności od tego, ile było wiadomo w chwili zapisu predykcji:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} trafionych miejsc na podium w ${n} ${plural(n, ["wyścigu", "wyścigach", "wyścigach"])}`,
  "record.race": "Wyścig",
  "record.predicted": "Przewidywane podium",
  "record.actual": "Faktyczne",
  "record.hits": "Trafienia",
  "record.not_run": "jeszcze się nie odbył",
  "record.winner": " · zwycięzca",

  "about.title": "Jak aplikacja przewiduje podium",
  "about.close": "Zamknij",
  "about.body": ({ imp }) => `
  <p>Trzy klasyfikatory gradient boosting oceniają każdy bolid na polach startowych: szansę
  na wygraną, na podium i na punkty. Każda ocena jest potem zakotwiczona w tym, ile
  historycznie był wart start z danego pola, a cała stawka przechodzi przez 20 000
  symulowanych wyścigów. Każde prawdopodobieństwo w aplikacji pochodzi z tej jednej
  symulacji, dlatego zawsze zgadzają się ze sobą i z kolejnością, w jakiej są pokazane.</p>

  <h3>Dlaczego pola startowe mają głos</h3>
  <p>Pozostawiony sam sobie model zmieniał kolejność startową mniej więcej co drugi wyścig
  i miał rację w 43% przypadków, a gdyby zostawił kolejność w spokoju, miałby ją w 57%.
  Jego sprzeciwy były gorsze niż bezużyteczne. Dlatego każda ocena jest teraz łączona,
  w skali log-odds, z rzeczywistą skutecznością danego pola startowego; model wciąż
  przesuwa bolid, ale tylko proporcjonalnie do tego, jak mocno się nie zgadza. Waga
  tego połączenia jest mierzona na sezonach, których model nie widział, a nie dobierana ręcznie.</p>

  <h3>Co kończy wyścig</h3>
  <p>W każdym symulowanym wyścigu osobno losowana jest awaria i osobno wypadek. Awaria
  zależy od bolidu; wypadek od kierowcy, od konkretnego toru i głównie od tego, czy jedzie
  w części stawki walczącej o pozycje. Dlatego Monako i Zandvoort dają temu samemu
  kierowcy bardzo różne szanse na dojechanie do mety.</p>

  <h3>Na co patrzy model</h3>
  <p>Pole startowe i strata w kwalifikacjach; ostatnia forma kierowcy, niezawodność
  i bilans z partnerem z zespołu; tempo bolidu i to, jak często staje na podium; historia
  kierowcy na <em>tym</em> torze; oraz to, co sam tor zwykle robi z wyścigiem: jak bardzo
  miesza kolejność, jak często pole position kończy się wygraną, ile bolidów odpada.
  Najważniejsze cechy w tej chwili:</p>
  <ul>${imp}</ul>

  <h3>Dlaczego stare wyścigi liczą się mniej</h3>
  <p>Sport się zmienia, więc każdy wiersz treningowy ma wagę
  <code>0,5 ^ (lata wstecz / 8)</code>. Wyścig z 2005 roku wciąż się liczy, mniej więcej
  z 16% wagi wyścigu sprzed miesiąca. Bieżąca forma wygasa szybciej, z każdym wyścigiem,
  a nie z każdym rokiem.</p>

  <h3>Walidacja sezon po sezonie</h3>
  <p>Nigdy losowy podział: model uczy się wyłącznie na sezonach wcześniejszych niż ten,
  na którym jest oceniany, więc nic z przyszłości nie przecieka. Każda liczba jest
  porównana z punktem odniesienia, czyli odczytaniem podium z trzech pierwszych pól
  startowych, a zwycięzcy z pole position. We współczesnej Formule 1 to znacznie wyżej
  zawieszona poprzeczka, niż się wydaje: start z pierwszej trójki kończy się podium
  w 68% przypadków, start spoza niej tylko w 6%.</p>`,
  "val.season": "Sezon",
  "val.races": "Wyścigi",
  "val.hit": "Trafione podium",
  "val.grid": "Sam grid",
  "val.lift": "Przewaga",
  "val.winner": "Zwycięzca",
  "val.pole": "Samo pole",

  "nav.skip": "Przejdź do treści",
  "nav.back": "Wróć do prognoz",
  "footer.tagline": "Prognozy podium Formuły 1 z 30 lat danych wyścigowych.",
  "footer.nav": "Stopka",
  "footer.home": "Prognozy",
  "footer.privacy": "Polityka prywatności",
  "footer.terms": "Regulamin",
  "footer.data": "Dane:",
  "footer.disclaimer": "Serwis niezwiązany z Formułą 1, FIA ani żadnym zespołem. F1 i Formula 1 są znakami towarowymi Formula One Licensing B.V.",
  "notfound.title": "Wypadłeś z toru",
  "notfound.text": "Ta strona nie istnieje albo została przeniesiona. Ale wyścig trwa dalej.",
  "notfound.home": "Przejdź do prognoz",
  "meta.title": "Race Predictor — prognozy podium F1 na każde Grand Prix",
  "meta.race": ({ race }) => `${race}: prognoza podium · Race Predictor`,
};
