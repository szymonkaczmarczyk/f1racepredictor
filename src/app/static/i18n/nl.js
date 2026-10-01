"use strict";

STRINGS.nl = {
  "html.title": "Race Predictor",
  "model.loading": "model laden…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · getraind tot ${trained}`,
  "model.next": ({ race, date }) => ` · volgende: ${race}, ${date}`,
  "metric.hit": "podium goed voorspeld",
  "metric.grid": "alleen startopstelling",
  "btn.about": "Hoe het werkt",
  "btn.theme": "Thema wisselen",
  "btn.lang": "Taal",

  "track.title": "Circuit en raceomstandigheden",
  "track.season": "Seizoen",
  "season.2026": "2026 (gesimuleerd)",
  "season.real": ({ year }) => `${year} (verreden)`,
  "track.select": "Circuit",
  "track.calendar": "Kalender van dit seizoen",
  "track.other": "Andere circuits met historie",
  "track.street": " · stratencircuit",
  "track.no_map": "Geen getekende baan voor dit circuit.<br>De voorspelling verandert daar niet door.",
  "track.layout": ({ name }) => `Baan van ${name}`,
  "ro.difficulty": "Moeilijkheid van het circuit",
  "ro.difficulty_note": "bochtdichtheid, incidenten, muren",
  "ro.deg": "Bandenslijtage",
  "ro.deg_none": "geen recente gegevens",
  "ro.deg_pitstops": ({ window }) => `pitstops ${window}`,
  "ro.deg_layout": "geschat uit de baanindeling",
  "ro.distance": "Raceafstand",
  "ro.corners": "Bochten",
  "ro.laps": "Ronden",
  "weather.title": "Weer",
  "weather.dry": "Droog",
  "weather.cloudy": "Bewolkt",
  "weather.light_rain": "Lichte regen",
  "weather.mixed": "Wisselend / opdrogend",
  "weather.heavy_rain": "Zware regen",

  "stat.sticky": "Podium uit de top 3 van de start",
  "stat.pole": "Pole wordt een zege",
  "stat.dnf": "Uitvalpercentage",
  "stat.gained": "Gewonnen plaatsen per race",
  "stat.stops": "Pitstops per auto",
  "stat.sc": "Safety car of rode vlag",
  "stat.sc_value": ({ pct, n }) => `${pct} van ${n} ${plural(n, ["race", "races"])}`,
  "stat.deg": "Tijdverlies per bandenronde",
  "stat.length": "Rondelengte",
  "stat.measured": "Gemeten over",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["recente start", "recente starts"])}`,

  "grid.title": "Startopstelling",
  "grid.col.grid": "Plek",
  "grid.col.driver": "Coureur",
  "grid.col.team": "Team / auto",
  "grid.col.history": "Op dit circuit",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["auto", "auto's"])}.`,
  "grid.move_up": ({ name }) => `${name} naar voren`,
  "grid.move_down": ({ name }) => `${name} naar achteren`,
  "history.none": "nog geen starts hier",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["start", "starts"])}`,
  "history.avg": ({ pos }) => `gem. <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podium", "podiums"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["zege", "zeges"])}`,
  "driver.career": (c) => `Carrière: ${c.races} starts, ${c.wins} zeges, ${c.podiums} podiums, gem. finish P${c.avg}, uitval ${c.dnf}`,
  "driver.recent": (r) => `Seizoenen ${r.seasons}: gem. start P${r.grid}, gem. finish P${r.finish}, podium in ${r.rate} van de races`,
  "driver.season": (s) => `Dit seizoen: ${s.races} starts, ${s.points} punten, ${s.podiums} podiums${s.best ? `, beste P${s.best}` : ""}`,

  "source.race": "Werkelijke startopstelling",
  "source.race.hint": "Deze race is al verreden. De voorspelling gebruikt alleen wat de dag ervoor bekend was; de echte uitslag staat ernaast.",
  "source.starting_grid": "Officiële startopstelling",
  "source.starting_grid.hint": "De officiële startopstelling van OpenF1, inclusief gridstraffen.",
  "source.qualifying": "Uit de kwalificatie",
  "source.qualifying.hint": "Volgorde volgens de officiële kwalificatie-uitslag. Straffen worden verwerkt zodra de officiële startopstelling er is.",
  "source.openf1": "Uit de kwalificatie (OpenF1)",
  "source.openf1.hint": "Volgorde uit de kwalificatie op OpenF1; de officiële bron heeft hem nog niet.",
  "source.expected_practice": "Verwachte startopstelling (met trainingen)",
  "source.expected_practice.hint": "De kwalificatie moet nog komen: de volgorde combineert de recente kwalificatieachterstand van elke coureur met zijn snelste ronde in de vrije trainingen van dit weekend. Hij werkt zichzelf bij na de kwalificatie.",
  "source.expected": "Verwachte startopstelling",
  "source.expected.hint": "De kwalificatie moet nog komen: het veld staat op volgorde van de mediane achterstand op pole in de laatste drie kwalificaties. Hij werkt zichzelf bij na de kwalificatie.",
  "source.what_if": "Wat-als-opstelling",
  "source.what_if.hint": "Je hebt de startopstelling aangepast. Voorspellingen met een aangepaste opstelling gaan niet in de staat van dienst.",

  "btn.sync": "Live gegevens ophalen",
  "btn.syncing": "Ophalen…",
  "sync.done": "Live gegevens bijgewerkt!",
  "sync.failed": ({ msg }) => `Bijwerken mislukt: ${msg}`,
  "btn.reset": "Opstelling herstellen",
  "btn.predict": "Voorspel het podium",
  "btn.predicting": "Berekenen…",
  "predict.failed": ({ msg }) => `Voorspelling mislukt: ${msg}`,

  "results.title": "Voorspelde uitslag",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · slijtage ${deg}/10`,
  "results.backtest": " · stand van de dag ervoor",
  "results.prequali": " · model vóór de kwalificatie",
  "order.slot": ({ pct }) => `alleen startplek ${pct}`,
  "place.1": "1e",
  "place.2": "2e",
  "place.3": "3e",
  "pod.from": ({ place, grid }) => `${place} · vanaf P${grid}`,
  "pod.chance": "kans op podium",
  "order.pos": "Pos.",
  "order.driver": "Coureur",
  "order.team": "Team",
  "order.prob": "Kans op podium",
  "order.podium": "Podium",
  "order.win": "Zege",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `start P${grid} · verwachte finish ${finish}`,
  "order.range": ({ a, b }) => ` · meestal P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · werd P${pos}`,
  "order.actual_dnf": " · viel uit",
  "dnf.total": ({ pct }) => `Kans op uitval ${pct}`,
  "dnf.crash": ({ pct }) => `  crash ${pct}`,
  "dnf.mech": ({ pct }) => `  technisch defect ${pct}`,
  "dnf.dsq": ({ pct }) => `  diskwalificatie ${pct}`,

  "note.grid_front": ({ grid }) => `start op P${grid}`,
  "note.grid_deep": ({ grid }) => `ver achterin op P${grid}`,
  "note.form": ({ pos }) => `recente vorm ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `auto in ${pctText(rate)} van de recente starts op het podium`,
  "note.over_performs": ({ delta }) => `presteert hier beter dan normaal (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `hier meestal zwakker (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podium", "podiums"])} op dit circuit`,
  "note.reliability": ({ rate }) => `betrouwbaarheidsrisico (${pctText(rate)} recente uitval)`,
  "note.crashed_here": ({ n }) => `hier ${n} ${plural(n, ["keer", "keer"])} uitgevallen na een crash`,
  "note.crash_risk": ({ rate }) => `verhoogd crashrisico hier (${pctText(rate)})`,

  "btn.share": "Deel het podium",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · VANAF P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · model getraind tot ${trained}`,
  "share.text": ({ list }) => `Voorspeld podium: ${list}`,
  "share.saved": ({ name }) => `${name} opgeslagen`,

  "champ.title": "Kampioenschapsprognose",
  "champ.chip": "rest van het seizoen",
  "champ.hint": "Rijdt elke resterende race duizenden keren met het model en telt de punten op.",
  "champ.btn": "Simuleer de rest van het seizoen",
  "champ.running": "Simuleren…",
  "champ.retry": "Opnieuw proberen",
  "champ.failed": ({ msg }) => `Simulatie mislukt: ${msg}`,
  "champ.drivers": "Coureurs",
  "champ.teams": "Constructeurs",
  "champ.left": ({ races, sprints }) => `nog ${races} ${plural(races, ["race", "races"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprints"])}` : ""),
  "champ.done": "seizoen voorbij",
  "champ.summary": ({ sims }) => `${sims} gesimuleerde seizoenen vanaf de huidige stand. Elke race gebruikt de verwachte startopstelling en de kansen van het model; `,
  "champ.sprints": "sprints worden met dezelfde kansen gescoord.",
  "champ.no_sprints": "sprintweekenden konden niet worden gecontroleerd, dus sprints tellen niet mee.",
  "champ.final": "Geen races meer: dit is de eindstand.",
  "champ.now": "Nu",
  "champ.driver": "Coureur",
  "champ.team": "Team",
  "champ.expected": "Verwacht",
  "champ.title_col": "Titel",
  "champ.range": ({ a, b }) => `80% van de gesimuleerde seizoenen eindigt tussen ${a} en ${b} punten`,

  "record.title": "Staat van dienst",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["race beoordeeld", "races beoordeeld"])}: ${hit} van de podiumplaatsen goed (alleen startopstelling: ${grid}), winnaar goed in ${winner} van de gevallen.`,
  "record.empty": "Nog geen race beoordeeld. De app legt voor elke race zijn voorspelling vast en beoordeelt die zodra de uitslag er is.",
  "record.by_source": "Naar hoeveel van het weekend bekend was toen de voorspelling werd vastgelegd:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} van de podiumplaatsen over ${n} ${plural(n, ["race", "races"])}`,
  "record.race": "Race",
  "record.predicted": "Voorspeld podium",
  "record.actual": "Werkelijk",
  "record.hits": "Raak",
  "record.not_run": "nog niet verreden",
  "record.winner": " · winnaar",

  "about.title": "Hoe het podium wordt voorspeld",
  "about.close": "Sluiten",
  "about.body": ({ imp }) => `
    <p>Drie gradient-boosting-classificatoren beoordelen elke auto in de startopstelling: op een
    zege, een podium en een puntenfinish. Elke score wordt daarna verankerd aan wat een start
    vanaf die plek historisch waard was, en het hele veld gaat door 20.000 gesimuleerde races.
    Elke kans hier komt uit die ene simulatie; daarom kloppen ze altijd met elkaar en met de
    volgorde waarin ze staan.</p>

    <h3>Waarom de startopstelling meetelt</h3>
    <p>Aan zichzelf overgelaten veranderde het model ongeveer elke tweede race de startvolgorde
    en had het in 43% van de gevallen gelijk, tegenover 57% als het de volgorde had gelaten. Zijn
    afwijkingen waren erger dan nutteloos. Daarom wordt elke score nu, in log-odds, gemengd met
    het werkelijke slagingspercentage van die startplek; het model verschuift nog steeds een
    auto, maar alleen naar verhouding van hoe sterk het het oneens is. Het mengewicht wordt
    gemeten op seizoenen die het model nooit heeft gezien, niet met de hand gekozen.</p>

    <h3>Wat een race beëindigt</h3>
    <p>In elke gesimuleerde race wordt apart geloot op betrouwbaarheid en op een crash. Kapotgaan
    hoort bij de auto; crashen hoort bij de coureur, bij het specifieke circuit en vooral bij het
    deel van het veld dat om posities vecht. Daarom geven Monaco en Zandvoort dezelfde coureur
    heel verschillende kansen om de finishvlag te zien.</p>

    <h3>Waar het naar kijkt</h3>
    <p>Startplek en kwalificatieachterstand; de recente vorm van de coureur, zijn
    betrouwbaarheid en zijn stand tegen de teamgenoot; het tempo van de auto en hoe vaak die op
    het podium staat; de eigen historie van de coureur op <em>dit</em> circuit; en wat het
    circuit zelf met een race doet: hoeveel de volgorde husselt, hoe vaak pole wint, hoeveel
    auto's uitvallen. De zwaarst wegende kenmerken op dit moment:</p>
    <ul>${imp}</ul>

    <h3>Waarom oude races minder tellen</h3>
    <p>De sport staat niet stil, dus elke trainingsrij weegt
    <code>0,5 ^ (jaren geleden / 8)</code>. Een race uit 2005 telt nog mee, met ongeveer 16% van
    het gewicht van een race van vorige maand. Recente vorm vervaagt sneller, per race in plaats
    van per jaar.</p>

    <h3>Seizoen voor seizoen gevalideerd</h3>
    <p>Nooit een willekeurige splitsing: het model leert alleen van seizoenen vóór het seizoen
    waarop het wordt beoordeeld, zodat er niets uit de toekomst doorlekt. Elk getal wordt
    afgezet tegen het podium aflezen van de eerste drie startplekken en de zege van pole; in de
    moderne Formule 1 is dat een veel hogere lat dan het klinkt: een start in de top drie wordt
    in 68% van de gevallen een podium, een start daarachter in maar 6%.</p>`,
  "val.season": "Seizoen",
  "val.races": "Races",
  "val.hit": "Podium raak",
  "val.grid": "Alleen grid",
  "val.lift": "Winst",
  "val.winner": "Winnaar",
  "val.pole": "Alleen pole",

  "nav.skip": "Naar de inhoud",
  "nav.back": "Terug naar de voorspellingen",
  "footer.tagline": "Formule 1-podiumvoorspellingen uit 30 jaar racegegevens.",
  "footer.nav": "Voettekst",
  "footer.home": "Voorspellingen",
  "footer.privacy": "Privacybeleid",
  "footer.terms": "Gebruiksvoorwaarden",
  "footer.data": "Gegevens:",
  "footer.disclaimer": "Niet verbonden aan de Formule 1, de FIA of een team. F1 en Formula 1 zijn merken van Formula One Licensing B.V.",
  "notfound.title": "Van de baan",
  "notfound.text": "Deze pagina bestaat niet of is verplaatst. De race gaat gewoon door.",
  "notfound.home": "Naar de voorspellingen",
  "meta.title": "Race Predictor — F1-podiumvoorspellingen voor elke Grand Prix",
  "meta.race": ({ race }) => `${race}: podiumvoorspelling · Race Predictor`,
};
