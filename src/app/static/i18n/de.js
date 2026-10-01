"use strict";

STRINGS.de = {
  "html.title": "Race Predictor",
  "model.loading": "Modell wird geladen…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · trainiert bis ${trained}`,
  "model.next": ({ race, date }) => ` · als Nächstes: ${race}, ${date}`,
  "metric.hit": "Podium-Trefferquote",
  "metric.grid": "nur Startaufstellung",
  "btn.about": "So funktioniert's",
  "btn.theme": "Design wechseln",
  "btn.lang": "Sprache",

  "track.title": "Strecke und Rennbedingungen",
  "track.season": "Saison",
  "season.2026": "2026 (simuliert)",
  "season.real": ({ year }) => `${year} (gefahren)`,
  "track.select": "Strecke",
  "track.calendar": "Kalender dieser Saison",
  "track.other": "Weitere Strecken mit Historie",
  "track.street": " · Stadtkurs",
  "track.no_map": "Für diese Strecke gibt es keinen Streckenplan.<br>Die Prognose ist davon nicht betroffen.",
  "track.layout": ({ name }) => `Streckenplan ${name}`,
  "ro.difficulty": "Streckenschwierigkeit",
  "ro.difficulty_note": "Kurvendichte, Unfälle, Mauern",
  "ro.deg": "Reifenverschleiß",
  "ro.deg_none": "keine aktuellen Daten",
  "ro.deg_pitstops": ({ window }) => `Boxenstopps ${window}`,
  "ro.deg_layout": "aus dem Streckenlayout geschätzt",
  "ro.distance": "Renndistanz",
  "ro.corners": "Kurven",
  "ro.laps": "Runden",
  "weather.title": "Wetter",
  "weather.dry": "Trocken",
  "weather.cloudy": "Bewölkt",
  "weather.light_rain": "Leichter Regen",
  "weather.mixed": "Wechselhaft / abtrocknend",
  "weather.heavy_rain": "Starkregen",

  "stat.sticky": "Podium aus den Top 3 der Startaufstellung",
  "stat.pole": "Pole-Position wird zum Sieg",
  "stat.dnf": "Ausfallquote",
  "stat.gained": "Gewonnene Plätze pro Rennen",
  "stat.stops": "Boxenstopps pro Auto",
  "stat.sc": "Safety-Car oder rote Flagge",
  "stat.sc_value": ({ pct, n }) => `${pct} von ${n} ${plural(n, ["Rennen", "Rennen"])}`,
  "stat.deg": "Zeitverlust pro Reifenrunde",
  "stat.length": "Rundenlänge",
  "stat.measured": "Gemessen über",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["Start", "Starts"])} zuletzt`,

  "grid.title": "Startaufstellung",
  "grid.col.grid": "Platz",
  "grid.col.driver": "Fahrer",
  "grid.col.team": "Team / Auto",
  "grid.col.history": "Auf dieser Strecke",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["Auto", "Autos"])}.`,
  "grid.move_up": ({ name }) => `${name} nach vorne`,
  "grid.move_down": ({ name }) => `${name} nach hinten`,
  "history.none": "noch keine Starts hier",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["Start", "Starts"])}`,
  "history.avg": ({ pos }) => `Ø <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["Podium", "Podien"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["Sieg", "Siege"])}`,
  "driver.career": (c) => `Karriere: ${c.races} Starts, ${c.wins} Siege, ${c.podiums} Podien, Ø Ziel P${c.avg}, Ausfälle ${c.dnf}`,
  "driver.recent": (r) => `Saisons ${r.seasons}: Ø Startplatz P${r.grid}, Ø Ziel P${r.finish}, Podiumsquote ${r.rate}`,
  "driver.season": (s) => `Diese Saison: ${s.races} Starts, ${s.points} Punkte, ${s.podiums} Podien${s.best ? `, bestes Ergebnis P${s.best}` : ""}`,

  "source.race": "Tatsächliche Startaufstellung",
  "source.race.hint": "Dieses Rennen ist bereits gefahren. Die Prognose nutzt nur, was am Vortag bekannt war; das echte Ergebnis steht daneben.",
  "source.starting_grid": "Offizielle Startaufstellung",
  "source.starting_grid.hint": "Die offizielle Startaufstellung von OpenF1, mit allen Startplatzstrafen.",
  "source.qualifying": "Aus dem Qualifying",
  "source.qualifying.hint": "Reihenfolge laut offiziellem Qualifying-Ergebnis. Strafen werden berücksichtigt, sobald die offizielle Startaufstellung veröffentlicht ist.",
  "source.openf1": "Aus dem Qualifying (OpenF1)",
  "source.openf1.hint": "Reihenfolge aus dem Qualifying bei OpenF1; die offizielle Quelle hat sie noch nicht.",
  "source.expected_practice": "Erwartete Startaufstellung (mit Training)",
  "source.expected_practice.hint": "Das Qualifying steht noch aus: Die Reihenfolge kombiniert die letzten Qualifying-Abstände jedes Fahrers mit seiner besten Runde im Training dieses Wochenendes. Sie aktualisiert sich nach dem Qualifying von selbst.",
  "source.expected": "Erwartete Startaufstellung",
  "source.expected.hint": "Das Qualifying steht noch aus: Das Feld ist nach dem mittleren Rückstand auf die Pole in den letzten drei Qualifyings sortiert. Sie aktualisiert sich nach dem Qualifying von selbst.",
  "source.what_if": "Was-wäre-wenn-Aufstellung",
  "source.what_if.hint": "Du hast die Startaufstellung umgestellt. Prognosen aus einer bearbeiteten Aufstellung werden nicht in die Bilanz übernommen.",

  "btn.sync": "Live-Daten abrufen",
  "btn.syncing": "Wird abgerufen…",
  "sync.done": "Live-Daten erfolgreich aktualisiert!",
  "sync.failed": ({ msg }) => `Aktualisierung fehlgeschlagen: ${msg}`,
  "btn.reset": "Aufstellung zurücksetzen",
  "btn.predict": "Podium vorhersagen",
  "btn.predicting": "Wird berechnet…",
  "predict.failed": ({ msg }) => `Prognose fehlgeschlagen: ${msg}`,

  "results.title": "Prognostiziertes Ergebnis",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · Reifen ${deg}/10`,
  "results.backtest": " · Stand am Vortag",
  "results.prequali": " · Modell vor dem Qualifying",
  "order.slot": ({ pct }) => `nur Startplatz ${pct}`,
  "place.1": "1. Platz",
  "place.2": "2. Platz",
  "place.3": "3. Platz",
  "pod.from": ({ place, grid }) => `${place} · von P${grid}`,
  "pod.chance": "Podiumschance",
  "order.pos": "Pos.",
  "order.driver": "Fahrer",
  "order.team": "Team",
  "order.prob": "Podiumswahrscheinlichkeit",
  "order.podium": "Podium",
  "order.win": "Sieg",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `Start P${grid} · erwartetes Ziel ${finish}`,
  "order.range": ({ a, b }) => ` · meist P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · tatsächlich P${pos}`,
  "order.actual_dnf": " · tatsächlich ausgefallen",
  "dnf.total": ({ pct }) => `Ausfallrisiko ${pct}`,
  "dnf.crash": ({ pct }) => `  Unfall ${pct}`,
  "dnf.mech": ({ pct }) => `  Technikdefekt ${pct}`,
  "dnf.dsq": ({ pct }) => `  Disqualifikation ${pct}`,

  "note.grid_front": ({ grid }) => `startet von P${grid}`,
  "note.grid_deep": ({ grid }) => `weit hinten auf P${grid}`,
  "note.form": ({ pos }) => `aktuelle Form ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `Auto in ${pctText(rate)} der letzten Starts auf dem Podium`,
  "note.over_performs": ({ delta }) => `hier stärker als sonst (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `hier meist schwächer (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["Podium", "Podien"])} auf dieser Strecke`,
  "note.reliability": ({ rate }) => `Zuverlässigkeitsrisiko (${pctText(rate)} Ausfälle zuletzt)`,
  "note.crashed_here": ({ n }) => `hier ${n} ${plural(n, ["Mal", "Mal"])} per Unfall ausgeschieden`,
  "note.crash_risk": ({ rate }) => `erhöhtes Unfallrisiko hier (${pctText(rate)})`,

  "btn.share": "Podium teilen",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · VON P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · Modell trainiert bis ${trained}`,
  "share.text": ({ list }) => `Prognostiziertes Podium: ${list}`,
  "share.saved": ({ name }) => `${name} gespeichert`,

  "champ.title": "WM-Prognose",
  "champ.chip": "Rest der Saison",
  "champ.hint": "Spielt jedes verbleibende Rennen tausendfach mit dem Modell durch und zählt die Punkte zusammen.",
  "champ.btn": "Rest der Saison simulieren",
  "champ.running": "Wird simuliert…",
  "champ.retry": "Erneut versuchen",
  "champ.failed": ({ msg }) => `Simulation fehlgeschlagen: ${msg}`,
  "champ.drivers": "Fahrer",
  "champ.teams": "Konstrukteure",
  "champ.left": ({ races, sprints }) => `noch ${races} ${plural(races, ["Rennen", "Rennen"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["Sprint", "Sprints"])}` : ""),
  "champ.done": "Saison beendet",
  "champ.summary": ({ sims }) => `${sims} simulierte Saisons ab dem heutigen Stand. Jedes Rennen nutzt die erwartete Startaufstellung und die Zielchancen des Modells; `,
  "champ.sprints": "Sprints werden aus denselben Chancen gewertet.",
  "champ.no_sprints": "Sprint-Wochenenden ließen sich nicht prüfen, daher bleiben Sprints außen vor.",
  "champ.final": "Keine Rennen mehr: Das ist der Endstand.",
  "champ.now": "Jetzt",
  "champ.driver": "Fahrer",
  "champ.team": "Team",
  "champ.expected": "Erwartet",
  "champ.title_col": "Titel",
  "champ.range": ({ a, b }) => `80 % der simulierten Saisons enden zwischen ${a} und ${b} Punkten`,

  "record.title": "Bilanz",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["Rennen", "Rennen"])} gewertet: ${hit} der Podiumsplätze getroffen (nur Startaufstellung: ${grid}), Sieger in ${winner} der Fälle getroffen.`,
  "record.empty": "Noch kein Rennen gewertet. Die App hält vor jedem Rennen ihre Prognose fest und wertet sie, sobald das Ergebnis vorliegt.",
  "record.by_source": "Je nachdem, wie viel vom Wochenende beim Festhalten der Prognose bekannt war:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} der Podiumsplätze in ${n} ${plural(n, ["Rennen", "Rennen"])}`,
  "record.race": "Rennen",
  "record.predicted": "Prognostiziertes Podium",
  "record.actual": "Tatsächlich",
  "record.hits": "Treffer",
  "record.not_run": "noch nicht gefahren",
  "record.winner": " · Sieger",

  "about.title": "Wie das Podium vorhergesagt wird",
  "about.close": "Schließen",
  "about.body": ({ imp }) => `
    <p>Drei Gradient-Boosting-Klassifikatoren bewerten jedes Auto in der Startaufstellung: für
    einen Sieg, ein Podium und eine Punkteplatzierung. Jede Bewertung wird dann daran verankert,
    was ein Start von diesem Platz historisch wert war, und das ganze Feld läuft durch 20.000
    simulierte Rennen. Jede Wahrscheinlichkeit hier stammt aus dieser einen Simulation; deshalb
    passen sie immer zueinander und zur angezeigten Reihenfolge.</p>

    <h3>Warum die Startaufstellung mitentscheidet</h3>
    <p>Sich selbst überlassen, hat das Modell die Startreihenfolge etwa in jedem zweiten Rennen
    umgestellt und lag dabei in 43 % der Fälle richtig, gegenüber 57 %, wenn es die Reihenfolge
    belassen hätte. Seine Widersprüche waren schlimmer als nutzlos. Deshalb wird jede Bewertung
    nun in Log-Odds mit der tatsächlichen Erfolgsquote dieses Startplatzes gemischt; das Modell
    verschiebt ein Auto weiterhin, aber nur so stark, wie es widerspricht. Das Mischungsgewicht
    wird an Saisons gemessen, die das Modell nie gesehen hat, nicht von Hand gewählt.</p>

    <h3>Was ein Rennen beendet</h3>
    <p>In jedem simulierten Rennen wird getrennt ausgewürfelt, ob das Auto hält und ob es einen
    Unfall gibt. Defekte gehören zum Auto; Unfälle gehören zum Fahrer, zur jeweiligen Strecke
    und vor allem zum Teil des Feldes, der um Positionen kämpft. Deshalb geben Monaco und
    Zandvoort demselben Fahrer sehr unterschiedliche Chancen, die Zielflagge zu sehen.</p>

    <h3>Worauf es schaut</h3>
    <p>Startplatz und Qualifying-Rückstand; die aktuelle Form des Fahrers, seine Zuverlässigkeit
    und seine Bilanz gegen den Teamkollegen; Tempo und Podiumsquote des Autos; die eigene
    Historie des Fahrers auf <em>dieser</em> Strecke; und was die Strecke selbst mit einem Rennen
    macht: wie sehr sich die Reihenfolge mischt, wie oft die Pole gewinnt, wie viele Autos
    ausfallen. Derzeit am stärksten gewichtete Merkmale:</p>
    <ul>${imp}</ul>

    <h3>Warum alte Rennen weniger zählen</h3>
    <p>Der Sport steht nicht still, daher wird jede Trainingszeile mit
    <code>0,5 ^ (Jahre zurück / 8)</code> gewichtet. Ein Rennen von 2005 zählt noch mit, mit etwa
    16 % des Gewichts eines Rennens vom letzten Monat. Die laufende Form klingt schneller ab,
    pro Rennen statt pro Jahr.</p>

    <h3>Saison für Saison validiert</h3>
    <p>Nie eine zufällige Aufteilung: Das Modell lernt nur aus Saisons vor der, an der es gemessen
    wird, sodass nichts aus der Zukunft einfließt. Jede Zahl wird an der Grundlinie gemessen, das
    Podium aus den ersten drei Startplätzen und den Sieg von der Pole abzulesen. In der modernen
    Formel 1 ist das eine viel höhere Hürde, als es klingt: Ein Start aus den Top 3 wird in 68 %
    der Fälle zum Podium, ein Start dahinter nur in 6 %.</p>`,
  "val.season": "Saison",
  "val.races": "Rennen",
  "val.hit": "Podium-Treffer",
  "val.grid": "Nur Startplatz",
  "val.lift": "Vorsprung",
  "val.winner": "Sieger",
  "val.pole": "Nur Pole",

  "nav.skip": "Zum Inhalt springen",
  "nav.back": "Zurück zu den Prognosen",
  "footer.tagline": "Formel-1-Podiumsprognosen aus 30 Jahren Renndaten.",
  "footer.nav": "Fußzeile",
  "footer.home": "Prognosen",
  "footer.privacy": "Datenschutzerklärung",
  "footer.terms": "Nutzungsbedingungen",
  "footer.data": "Daten:",
  "footer.disclaimer": "Nicht verbunden mit der Formel 1, der FIA oder einem Team. F1 und Formula 1 sind Marken der Formula One Licensing B.V.",
  "notfound.title": "Von der Strecke abgekommen",
  "notfound.text": "Diese Seite gibt es nicht oder sie wurde verschoben. Das Rennen läuft aber weiter.",
  "notfound.home": "Zu den Prognosen",
  "meta.title": "Race Predictor – F1-Podiumsprognosen für jeden Grand Prix",
  "meta.race": ({ race }) => `${race}: Podiumsprognose · Race Predictor`,
};
