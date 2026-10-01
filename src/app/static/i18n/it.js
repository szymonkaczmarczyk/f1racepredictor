"use strict";

STRINGS.it = {
  "html.title": "Race Predictor",
  "model.loading": "caricamento del modello…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · addestrato fino al ${trained}`,
  "model.next": ({ race, date }) => ` · prossima: ${race}, ${date}`,
  "metric.hit": "podi indovinati",
  "metric.grid": "solo griglia",
  "btn.about": "Come funziona",
  "btn.theme": "Cambia tema",
  "btn.lang": "Lingua",

  "track.title": "Circuito e condizioni di gara",
  "track.season": "Stagione",
  "season.2026": "2026 (simulata)",
  "season.real": ({ year }) => `${year} (disputata)`,
  "track.select": "Circuito",
  "track.calendar": "Calendario di questa stagione",
  "track.other": "Altri circuiti con uno storico",
  "track.street": " · circuito cittadino",
  "track.no_map": "Nessun tracciato disegnato per questo circuito.<br>La previsione non cambia.",
  "track.layout": ({ name }) => `Tracciato di ${name}`,
  "ro.difficulty": "Difficoltà del circuito",
  "ro.difficulty_note": "densità di curve, incidenti, muri",
  "ro.deg": "Degrado gomme",
  "ro.deg_none": "nessun dato recente",
  "ro.deg_pitstops": ({ window }) => `pit stop ${window}`,
  "ro.deg_layout": "stimato dal tracciato",
  "ro.distance": "Distanza di gara",
  "ro.corners": "Curve",
  "ro.laps": "Giri",
  "weather.title": "Meteo",
  "weather.dry": "Asciutto",
  "weather.cloudy": "Nuvoloso",
  "weather.light_rain": "Pioggia leggera",
  "weather.mixed": "Misto / pista che si asciuga",
  "weather.heavy_rain": "Pioggia forte",

  "stat.sticky": "Podio dalle prime 3 posizioni in griglia",
  "stat.pole": "La pole diventa vittoria",
  "stat.dnf": "Tasso di ritiri",
  "stat.gained": "Posizioni guadagnate per gara",
  "stat.stops": "Pit stop per vettura",
  "stat.sc": "Safety car o bandiera rossa",
  "stat.sc_value": ({ pct, n }) => `${pct} su ${n} ${plural(n, ["gara", "gare"])}`,
  "stat.deg": "Tempo perso per giro di gomma",
  "stat.length": "Lunghezza del giro",
  "stat.measured": "Misurato su",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["partenza recente", "partenze recenti"])}`,

  "grid.title": "Griglia di partenza",
  "grid.col.grid": "Pos.",
  "grid.col.driver": "Pilota",
  "grid.col.team": "Squadra / vettura",
  "grid.col.history": "Su questo circuito",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["vettura", "vetture"])}.`,
  "grid.move_up": ({ name }) => `Sposta ${name} avanti`,
  "grid.move_down": ({ name }) => `Sposta ${name} indietro`,
  "history.none": "nessuna partenza qui",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["partenza", "partenze"])}`,
  "history.avg": ({ pos }) => `media <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podio", "podi"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["vittoria", "vittorie"])}`,
  "driver.career": (c) => `Carriera: ${c.races} partenze, ${c.wins} vittorie, ${c.podiums} podi, arrivo medio P${c.avg}, ritiri ${c.dnf}`,
  "driver.recent": (r) => `Stagioni ${r.seasons}: partenza media P${r.grid}, arrivo medio P${r.finish}, podio nel ${r.rate} delle gare`,
  "driver.season": (s) => `Questa stagione: ${s.races} partenze, ${s.points} punti, ${s.podiums} podi${s.best ? `, miglior risultato P${s.best}` : ""}`,

  "source.race": "Griglia reale",
  "source.race.hint": "Questa gara si è già corsa. La previsione usa solo ciò che si sapeva il giorno prima, e il risultato reale è mostrato accanto.",
  "source.starting_grid": "Griglia ufficiale",
  "source.starting_grid.hint": "La griglia di partenza ufficiale da OpenF1, con le penalità applicate.",
  "source.qualifying": "Dalle qualifiche",
  "source.qualifying.hint": "Ordine secondo il risultato ufficiale delle qualifiche. Le penalità vengono applicate quando esce la griglia ufficiale.",
  "source.openf1": "Dalle qualifiche (OpenF1)",
  "source.openf1.hint": "Ordine delle qualifiche su OpenF1; la fonte ufficiale non lo ha ancora.",
  "source.expected_practice": "Griglia prevista (con le libere)",
  "source.expected_practice.hint": "Le qualifiche non si sono ancora corse: l'ordine combina i distacchi recenti di ogni pilota in qualifica con il suo miglior giro nelle libere di questo weekend. Si aggiorna da sola dopo le qualifiche.",
  "source.expected": "Griglia prevista",
  "source.expected.hint": "Le qualifiche non si sono ancora corse: lo schieramento segue il distacco mediano di ogni pilota dalla pole nelle ultime tre qualifiche. Si aggiorna da sola dopo le qualifiche.",
  "source.what_if": "Griglia ipotetica",
  "source.what_if.hint": "Hai riordinato la griglia. Le previsioni con una griglia modificata non finiscono nello storico.",

  "btn.sync": "Aggiorna i dati",
  "btn.syncing": "Aggiornamento…",
  "sync.done": "Dati aggiornati!",
  "sync.failed": ({ msg }) => `Aggiornamento non riuscito: ${msg}`,
  "btn.reset": "Ripristina griglia",
  "btn.predict": "Prevedi il podio",
  "btn.predicting": "Calcolo…",
  "predict.failed": ({ msg }) => `Previsione non riuscita: ${msg}`,

  "results.title": "Risultato previsto",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · degrado ${deg}/10`,
  "results.backtest": " · come il giorno prima",
  "results.prequali": " · modello pre-qualifiche",
  "order.slot": ({ pct }) => `solo posizione in griglia ${pct}`,
  "place.1": "1°",
  "place.2": "2°",
  "place.3": "3°",
  "pod.from": ({ place, grid }) => `${place} · dalla P${grid}`,
  "pod.chance": "probabilità di podio",
  "order.pos": "Pos.",
  "order.driver": "Pilota",
  "order.team": "Squadra",
  "order.prob": "Probabilità di podio",
  "order.podium": "Podio",
  "order.win": "Vittoria",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `parte P${grid} · arrivo previsto ${finish}`,
  "order.range": ({ a, b }) => ` · di solito P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · in realtà P${pos}`,
  "order.actual_dnf": " · in realtà ritirato",
  "dnf.total": ({ pct }) => `Rischio di ritiro ${pct}`,
  "dnf.crash": ({ pct }) => `  incidente ${pct}`,
  "dnf.mech": ({ pct }) => `  guasto ${pct}`,
  "dnf.dsq": ({ pct }) => `  squalifica ${pct}`,

  "note.grid_front": ({ grid }) => `parte P${grid}`,
  "note.grid_deep": ({ grid }) => `molto indietro, P${grid}`,
  "note.form": ({ pos }) => `forma recente ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `vettura sul podio nel ${pctText(rate)} delle ultime gare`,
  "note.over_performs": ({ delta }) => `qui rende più del solito (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `qui di solito rende meno (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podio", "podi"])} su questo circuito`,
  "note.reliability": ({ rate }) => `rischio affidabilità (${pctText(rate)} di ritiri recenti)`,
  "note.crashed_here": ({ n }) => `ritirato qui per incidente ${n} ${plural(n, ["volta", "volte"])}`,
  "note.crash_risk": ({ rate }) => `rischio incidente elevato qui (${pctText(rate)})`,

  "btn.share": "Condividi il podio",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · DALLA P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · modello addestrato fino al ${trained}`,
  "share.text": ({ list }) => `Podio previsto: ${list}`,
  "share.saved": ({ name }) => `Salvato ${name}`,

  "champ.title": "Previsione del Mondiale",
  "champ.chip": "resto della stagione",
  "champ.hint": "Corre migliaia di volte ogni gara rimasta con il modello e somma i punti.",
  "champ.btn": "Simula il resto della stagione",
  "champ.running": "Simulazione…",
  "champ.retry": "Riprova",
  "champ.failed": ({ msg }) => `Simulazione non riuscita: ${msg}`,
  "champ.drivers": "Piloti",
  "champ.teams": "Costruttori",
  "champ.left": ({ races, sprints }) => `${plural(races, ["manca", "mancano"])} ${races} ${plural(races, ["gara", "gare"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprint"])}` : ""),
  "champ.done": "stagione conclusa",
  "champ.summary": ({ sims }) => `${sims} stagioni simulate a partire dalla classifica di oggi. Ogni gara usa la griglia prevista e le probabilità del modello; `,
  "champ.sprints": "le sprint sono calcolate con le stesse probabilità.",
  "champ.no_sprints": "non è stato possibile verificare i weekend sprint, quindi le sprint sono escluse.",
  "champ.final": "Non restano gare: questa è la classifica finale.",
  "champ.now": "Ora",
  "champ.driver": "Pilota",
  "champ.team": "Squadra",
  "champ.expected": "Previsti",
  "champ.title_col": "Titolo",
  "champ.range": ({ a, b }) => `L'80% delle stagioni simulate finisce tra ${a} e ${b} punti`,

  "record.title": "Storico",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["gara valutata", "gare valutate"])}: ${hit} dei posti sul podio indovinati (solo griglia: ${grid}), vincitore indovinato nel ${winner} dei casi.`,
  "record.empty": "Nessuna gara ancora valutata. L'app registra la sua previsione prima di ogni gara e la valuta quando arriva il risultato.",
  "record.by_source": "In base a quanto si sapeva del weekend quando è stata registrata la previsione:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} dei posti sul podio in ${n} ${plural(n, ["gara", "gare"])}`,
  "record.race": "Gara",
  "record.predicted": "Podio previsto",
  "record.actual": "Reale",
  "record.hits": "Indovinati",
  "record.not_run": "non ancora corsa",
  "record.winner": " · vincitore",

  "about.title": "Come viene previsto il podio",
  "about.close": "Chiudi",
  "about.body": ({ imp }) => `
    <p>Tre classificatori gradient boosting valutano ogni vettura in griglia: per la vittoria, il
    podio e la zona punti. Ogni valutazione viene poi ancorata a quanto è valsa storicamente una
    partenza da quella posizione, e l'intero schieramento passa attraverso 20.000 gare simulate.
    Ogni probabilità mostrata viene da quell'unica simulazione: per questo sono sempre coerenti
    tra loro e con l'ordine in cui compaiono.</p>

    <h3>Perché la griglia ha voce in capitolo</h3>
    <p>Lasciato a sé, il modello cambiava l'ordine della griglia circa una gara su due e aveva
    ragione nel 43% dei casi, contro il 57% che avrebbe ottenuto lasciando l'ordine com'era. I
    suoi disaccordi erano peggio che inutili. Per questo ogni valutazione viene ora miscelata, in
    log-odds, con il tasso reale di conversione di quella posizione; il modello sposta ancora una
    vettura, ma solo in proporzione a quanto dissente. Il peso della miscela è misurato su
    stagioni che il modello non ha mai visto, non scelto a mano.</p>

    <h3>Cosa mette fine a una gara</h3>
    <p>In ogni gara simulata si estraggono separatamente l'affidabilità e l'incidente. Il guasto
    dipende dalla vettura; l'incidente dipende dal pilota, dal circuito e soprattutto dalla parte
    dello schieramento che lotta per le posizioni. Per questo Monaco e Zandvoort danno allo
    stesso pilota probabilità molto diverse di vedere la bandiera a scacchi.</p>

    <h3>Cosa guarda</h3>
    <p>Posizione in griglia e distacco in qualifica; la forma recente del pilota, l'affidabilità
    e il confronto con il compagno di squadra; il passo della vettura e la sua frequenza di
    podi; lo storico del pilota su <em>questo</em> circuito; e ciò che il circuito tende a fare a
    una gara: quanto si rimescola l'ordine, quante volte vince la pole, quante vetture si
    ritirano. Le variabili più pesanti in questo momento:</p>
    <ul>${imp}</ul>

    <h3>Perché le gare vecchie contano meno</h3>
    <p>Lo sport non sta fermo, quindi ogni riga di addestramento pesa
    <code>0,5 ^ (anni fa / 8)</code>. Una gara del 2005 conta ancora, con circa il 16% del peso di
    una gara del mese scorso. La forma recente svanisce più in fretta, gara dopo gara e non anno
    dopo anno.</p>

    <h3>Validato stagione per stagione</h3>
    <p>Mai una divisione casuale: il modello impara solo dalle stagioni precedenti a quella su cui
    viene valutato, così nulla del futuro filtra. Ogni numero è confrontato con il leggere il
    podio dalle prime tre posizioni in griglia e la vittoria dalla pole, un'asticella molto più
    alta di quanto sembri nella Formula 1 moderna: una partenza nelle prime tre diventa podio nel
    68% dei casi, una partenza più indietro solo nel 6%.</p>`,
  "val.season": "Stagione",
  "val.races": "Gare",
  "val.hit": "Podi indovinati",
  "val.grid": "Solo griglia",
  "val.lift": "Vantaggio",
  "val.winner": "Vincitore",
  "val.pole": "Solo pole",

  "nav.skip": "Vai al contenuto",
  "nav.back": "Torna alle previsioni",
  "footer.tagline": "Previsioni del podio di Formula 1 da 30 anni di dati di gara.",
  "footer.nav": "Piè di pagina",
  "footer.home": "Previsioni",
  "footer.privacy": "Informativa sulla privacy",
  "footer.terms": "Termini d'uso",
  "footer.data": "Dati:",
  "footer.disclaimer": "Non affiliato alla Formula 1, alla FIA o ad alcuna squadra. F1 e Formula 1 sono marchi di Formula One Licensing B.V.",
  "notfound.title": "Fuori pista",
  "notfound.text": "Questa pagina non esiste o è stata spostata. Ma la gara continua.",
  "notfound.home": "Vai alle previsioni",
  "meta.title": "Race Predictor — previsioni del podio F1 per ogni Gran Premio",
  "meta.race": ({ race }) => `${race}: previsione del podio · Race Predictor`,
};
