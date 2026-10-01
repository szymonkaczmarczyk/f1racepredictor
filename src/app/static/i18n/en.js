"use strict";

STRINGS.en = {
  "html.title": "Race Predictor",
  "model.loading": "loading model…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · trained through ${trained}`,
  "model.next": ({ race, date }) => ` · next up: ${race}, ${date}`,
  "metric.hit": "podium hit rate",
  "metric.grid": "grid order alone",
  "btn.about": "How it works",
  "btn.theme": "Switch theme",
  "btn.lang": "Language",

  "track.title": "Track and Race Conditions",
  "track.season": "Select Season",
  "season.2026": "2026 (Simulated)",
  "season.real": ({ year }) => `${year} (Real)`,
  "track.select": "Select Track",
  "track.calendar": "This season's calendar",
  "track.other": "Other circuits with history",
  "track.street": " · street circuit",
  "track.no_map": "No traced layout for this circuit.<br>Predictions are unaffected.",
  "track.layout": ({ name }) => `${name} layout`,
  "ro.difficulty": "Track Difficulty",
  "ro.difficulty_note": "corner density, incidents, walls",
  "ro.deg": "Tyre Degradation",
  "ro.deg_none": "no recent data",
  "ro.deg_pitstops": ({ window }) => `pit stops ${window}`,
  "ro.deg_layout": "estimated from layout",
  "ro.distance": "Race Distance",
  "ro.corners": "Corners",
  "ro.laps": "Laps",
  "weather.title": "Weather Conditions",
  "weather.dry": "Dry",
  "weather.cloudy": "Cloudy",
  "weather.light_rain": "Light rain",
  "weather.mixed": "Mixed / drying",
  "weather.heavy_rain": "Heavy rain",

  "stat.sticky": "Podium sticks to top-3 grid",
  "stat.pole": "Pole converts to a win",
  "stat.dnf": "Retirement rate",
  "stat.gained": "Places gained per race",
  "stat.stops": "Pit stops per car",
  "stat.sc": "Safety car or red flag",
  "stat.sc_value": ({ pct, n }) => `${pct} of ${n} ${plural(n, ["race", "races"])}`,
  "stat.deg": "Lap time lost per tyre lap",
  "stat.length": "Lap length",
  "stat.measured": "Measured over",
  "stat.starts": ({ n }) => `${n} recent ${plural(n, ["start", "starts"])}`,

  "grid.title": "Starting Grid",
  "grid.col.grid": "Grid",
  "grid.col.driver": "Driver",
  "grid.col.team": "Team / car",
  "grid.col.history": "At this track",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["car", "cars"])}.`,
  "grid.move_up": ({ name }) => `Move ${name} up`,
  "grid.move_down": ({ name }) => `Move ${name} down`,
  "history.none": "no starts here",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["start", "starts"])}`,
  "history.avg": ({ pos }) => `avg <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podium", "podiums"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["win", "wins"])}`,
  "driver.career": (c) => `Career: ${c.races} starts, ${c.wins} wins, ${c.podiums} podiums, avg finish P${c.avg}, DNF ${c.dnf}`,
  "driver.recent": (r) => `Last ${r.seasons}: avg grid P${r.grid}, avg finish P${r.finish}, podium rate ${r.rate}`,
  "driver.season": (s) => `This season: ${s.races} starts, ${s.points} pts, ${s.podiums} podiums${s.best ? `, best P${s.best}` : ""}`,

  "source.race": "Actual starting grid",
  "source.race.hint": "This race has been run. The prediction uses only what was known the day before it, and the real result is shown next to it.",
  "source.starting_grid": "Starting grid",
  "source.starting_grid.hint": "The official starting grid, with grid penalties applied, from OpenF1.",
  "source.qualifying": "From qualifying",
  "source.qualifying.hint": "Starting order from the official qualifying result. Grid penalties are applied once the official starting grid is published.",
  "source.openf1": "From qualifying (OpenF1)",
  "source.openf1.hint": "Starting order from the qualifying session on OpenF1; the official feed has not caught up yet.",
  "source.expected_practice": "Expected grid (with practice)",
  "source.expected_practice.hint": "Qualifying has not run yet: the order blends each driver's recent qualifying gaps with their best lap in this weekend's practice. It updates by itself once qualifying is done.",
  "source.expected": "Expected grid",
  "source.expected.hint": "Qualifying has not run yet: the field is ordered by each driver's median gap to pole over their last three qualifying sessions. It updates by itself once qualifying is done.",
  "source.what_if": "What-if grid",
  "source.what_if.hint": "You have rearranged the grid. Predictions from an edited grid are not written to the track record.",

  "btn.sync": "Sync live data",
  "btn.syncing": "Syncing…",
  "sync.done": "Live data successfully synchronized!",
  "sync.failed": ({ msg }) => `Sync failed: ${msg}`,
  "btn.reset": "Reset grid",
  "btn.predict": "Predict the podium",
  "btn.predicting": "Predicting…",
  "predict.failed": ({ msg }) => `Prediction failed: ${msg}`,

  "results.title": "Predicted result",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · deg ${deg}/10`,
  "results.backtest": " · as of the day before",
  "results.prequali": " · pre-qualifying model",
  "order.slot": ({ pct }) => `grid slot alone ${pct}`,
  "place.1": "1st",
  "place.2": "2nd",
  "place.3": "3rd",
  "pod.from": ({ place, grid }) => `${place} · from P${grid}`,
  "pod.chance": "podium chance",
  "order.pos": "Pos",
  "order.driver": "Driver",
  "order.team": "Team",
  "order.prob": "Podium probability",
  "order.podium": "Podium",
  "order.win": "Win",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `started P${grid} · expected finish ${finish}`,
  "order.range": ({ a, b }) => ` · usually P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · actually finished P${pos}`,
  "order.actual_dnf": " · actually did not finish",
  "dnf.total": ({ pct }) => `Retirement risk ${pct}`,
  "dnf.crash": ({ pct }) => `  crashes out ${pct}`,
  "dnf.mech": ({ pct }) => `  car fails ${pct}`,
  "dnf.dsq": ({ pct }) => `  disqualified ${pct}`,

  "note.grid_front": ({ grid }) => `starts P${grid}`,
  "note.grid_deep": ({ grid }) => `deep in the field at P${grid}`,
  "note.form": ({ pos }) => `recent form ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `car on the podium ${pctText(rate)} of recent starts`,
  "note.over_performs": ({ delta }) => `over-performs here (${signedNum(delta)} vs usual)`,
  "note.weaker_here": ({ delta }) => `historically weaker here (${signedNum(delta)} vs usual)`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podium", "podiums"])} at this circuit`,
  "note.reliability": ({ rate }) => `reliability risk (${pctText(rate)} recent DNF rate)`,
  "note.crashed_here": ({ n }) => `crashed out here ${n} ${plural(n, ["time", "times"])}`,
  "note.crash_risk": ({ rate }) => `elevated crash risk here (${pctText(rate)})`,

  "btn.share": "Share podium",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · FROM P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · model trained through ${trained}`,
  "share.text": ({ list }) => `Predicted podium: ${list}`,
  "share.saved": ({ name }) => `Saved ${name}`,

  "champ.title": "Championship outlook",
  "champ.chip": "rest of the season",
  "champ.hint": "Runs every remaining race thousands of times with the model and adds up the points.",
  "champ.btn": "Simulate the rest of the season",
  "champ.running": "Simulating…",
  "champ.retry": "Try again",
  "champ.failed": ({ msg }) => `Simulation failed: ${msg}`,
  "champ.drivers": "Drivers",
  "champ.teams": "Constructors",
  "champ.left": ({ races, sprints }) => `${races} ${plural(races, ["race", "races"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprints"])}` : "") + " left",
  "champ.done": "season complete",
  "champ.summary": ({ sims }) => `${sims} simulated seasons from today's standings. Each race uses the expected grid and the model's finishing odds; `,
  "champ.sprints": "sprints are scored from the same odds.",
  "champ.no_sprints": "sprint weekends could not be checked, so sprints are left out.",
  "champ.final": "No races left: these are the final standings.",
  "champ.now": "Now",
  "champ.driver": "Driver",
  "champ.team": "Team",
  "champ.expected": "Expected",
  "champ.title_col": "Title",
  "champ.range": ({ a, b }) => `80% of simulated seasons end between ${a} and ${b} points`,

  "record.title": "Track record",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["race", "races"])} scored: ${hit} of podium places called (grid order alone: ${grid}), winner called ${winner} of the time.`,
  "record.empty": "No race scored yet. The app records its prediction before each race and scores it once the result is in.",
  "record.by_source": "By how much of the weekend was known when the prediction was written:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} of podium places over ${n} ${plural(n, ["race", "races"])}`,
  "record.race": "Race",
  "record.predicted": "Predicted podium",
  "record.actual": "Actual",
  "record.hits": "Hits",
  "record.not_run": "not run yet",
  "record.winner": " · winner",

  "about.title": "How this predicts a podium",
  "about.close": "Close",
  "about.body": ({ imp }) => `
  <p>Three gradient boosting classifiers score every car on the grid — for a win, a
  podium and a points finish. Each score is then anchored against what a start from
  that slot has historically been worth, and the whole field is run through 20,000
  simulated races. Every probability here is read off that one simulation, which is
  why they always agree with each other and with the order they are printed in.</p>

  <h3>Why the grid gets a vote</h3>
  <p>Left to itself the model overrode grid order about once every two races, and was
  right 43% of the time — against the 57% it would have managed by leaving the order
  alone. Its disagreements were worse than useless. So each score is now blended, in
  log-odds, with the empirical conversion rate for that grid slot; the model still
  moves a car, but only in proportion to how strongly it disagrees. The blend weight
  is measured on seasons the model had never seen, not chosen by hand.</p>

  <h3>What ends a race</h3>
  <p>Each simulated race rolls for reliability and for crashing out, separately.
  Breaking down belongs to the car; crashing belongs to the driver, at a particular
  circuit, and mostly to the part of the field fighting for position — which is why
  Monaco and Zandvoort give the same driver very different odds of seeing the flag.</p>

  <h3>What it looks at</h3>
  <p>Grid slot and qualifying gap; the driver's recent form, reliability and record
  against their own team mate; the car's pace and podium rate; the driver's own
  history at <em>this</em> circuit; and what the circuit itself tends to do to a race
  — how much the order shuffles, how often pole converts, how many cars retire.
  Heaviest-weighted features right now:</p>
  <ul>${imp}</ul>

  <h3>Why old races count less</h3>
  <p>The sport does not stand still, so every training row is weighted by
  <code>0.5 ^ (years ago / 8)</code>. A race from 2005 still contributes, at roughly
  16% of the weight of a race from last month. Rolling form decays faster, by race
  rather than by year.</p>

  <h3>Validated season by season</h3>
  <p>Never a random split — the model is trained only on seasons before the one it is
  scored on, so nothing from the future leaks in. Every number is measured against the
  baseline of reading the podium off the top three grid slots and the win off pole,
  which in modern Formula 1 is a much harder bar than it sounds: a top-three start
  converts to a podium 68% of the time, a start outside it just 6%.</p>`,
  "val.season": "Season",
  "val.races": "Races",
  "val.hit": "Podium hit",
  "val.grid": "Grid only",
  "val.lift": "Lift",
  "val.winner": "Winner",
  "val.pole": "Pole only",

  "nav.skip": "Skip to content",
  "nav.back": "Back to predictions",
  "footer.tagline": "Formula 1 podium predictions from 30 years of race data.",
  "footer.nav": "Footer",
  "footer.home": "Predictions",
  "footer.privacy": "Privacy policy",
  "footer.terms": "Terms of use",
  "footer.data": "Data:",
  "footer.disclaimer": "Not affiliated with Formula 1, the FIA or any team. F1 and Formula 1 are trade marks of Formula One Licensing B.V.",
  "notfound.title": "Off the track",
  "notfound.text": "This page does not exist, or it has been moved. The race is still on, though.",
  "notfound.home": "Go to the predictions",
  "meta.title": "Race Predictor — F1 podium predictions for every Grand Prix",
  "meta.race": ({ race }) => `${race}: podium prediction · Race Predictor`,
};
