"use strict";

const state = {
  tracks: [],
  drivers: [],
  driversById: new Map(),
  teams: {},
  calendar: [],
  model: {},
  track: null,
  trackHistory: {},
  entries: [],
  original: [],
  edited: false,
  season: "2026",
};

const weatherLabel = (preset) => t(`weather.${preset}`);

const TEAM_COLOURS = {
  mercedes: "#27F4D2", ferrari: "#E8002D", mclaren: "#FF8000", red_bull: "#3671C6",
  aston_martin: "#229971", alpine: "#FF87BC", williams: "#64C4FF", rb: "#6692FF",
  haas: "#B6BABD", sauber: "#52E252",
};
const teamColour = (constructorId) => TEAM_COLOURS[constructorId] || "var(--muted)";
const teamStyle = (constructorId) => `--team:${teamColour(constructorId)}`;
const driverCode = (driverId) => {
  const d = state.driversById.get(driverId);
  return d && d.code ? d.code : "";
};


async function loadSeasonData() {
  const data = await fetch(`/api/bootstrap?season=${state.season}`).then((r) => r.json());
  state.tracks = data.tracks;
  state.drivers = data.drivers;
  state.driversById = new Map(data.drivers.map((d) => [d.driver_id, d]));
  state.teams = data.teams;
  state.calendar = data.calendar;
  state.model = data.model;
  state.nextRace = data.next_race;
  state.boot = data;

  renderModelBadge(data);
  await buildTrackSelect(data.next_race);
}

const SKELETON_ROW = `<div class="entry skeleton-row" aria-hidden="true"><span class="skeleton skeleton-box"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line short"></span><span></span></div>`;

function setGridLoading(loading) {
  const entries = $("entries");
  entries.setAttribute("aria-busy", loading ? "true" : "false");
  if (loading) entries.innerHTML = SKELETON_ROW.repeat(Math.max(state.entries.length || 10, 10));
  $("btn-predict").disabled = loading || state.entries.length < 2;
  syncStickyCta();
}

function setMapLoading(loading) {
  const map = $("track-map");
  map.classList.toggle("is-loading", loading);
  map.setAttribute("aria-busy", loading ? "true" : "false");
  if (loading) map.innerHTML = `<div class="skeleton skeleton-map"></div>`;
}

function resultsSkeleton() {
  const pod = `<div class="pod pod-skeleton" aria-hidden="true"><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-number"></span></div>`;
  const row = `<div class="order-row skeleton-row" aria-hidden="true"><span class="skeleton skeleton-box"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line short"></span></div>`;
  $("podium").innerHTML = pod.repeat(3);
  $("order").innerHTML = row.repeat(6);
}

function updateTitle() {
  document.title = state.track
    ? t("meta.race", { race: (state.calendar.find((r) => r.circuit_id === state.track.circuit_id) || {}).race_name || state.track.race_name || state.track.name })
    : t("meta.title");
}

function syncStickyCta() {
  const sticky = $("btn-predict-sticky");
  if (!sticky) return;
  const main = $("btn-predict");
  sticky.disabled = main.disabled;
  sticky.classList.toggle("is-loading", main.classList.contains("is-loading"));
  sticky.textContent = main.textContent;
}

function watchStickyCta() {
  const bar = $("sticky-cta");
  if (!bar || !("IntersectionObserver" in window)) return;
  const seen = { predict: true, results: false };
  const update = () => {
    const show = !seen.predict && !seen.results;
    bar.hidden = !show;
    document.body.classList.toggle("has-sticky-cta", show);
  };
  const observer = new IntersectionObserver((items) => {
    for (const item of items) {
      if (item.target.id === "btn-predict") seen.predict = item.isIntersecting;
      if (item.target.id === "results") seen.results = item.isIntersecting && !item.target.hidden;
    }
    update();
  });
  observer.observe($("btn-predict"));
  observer.observe($("results"));
  $("btn-predict-sticky").onclick = () => {
    const running = predict();
    const behavior = matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    $("results").scrollIntoView({ behavior, block: "start" });
    return running;
  };
}

async function boot() {
  if (!initSite(onLanguageChanged)) return;
  localizeSeasonOptions();
  resetChampionship();
  wireControls();
  watchStickyCta();
  updateTitle();
  await loadSeasonData();
}

function localizeSeasonOptions() {
  for (const option of $("season-select").options) {
    option.textContent = option.value === "2026" ? t("season.2026") : t("season.real", { year: option.value });
  }
}

function renderModelBadge(data) {
  const s = data.model.summary || {};
  const [from, to] = data.model.seasons || [];
  const next = data.next_race;
  $("model-sub").textContent =
    t("model.badge", { from, to, trained: data.model.trained_through }) +
    (next ? t("model.next", { race: next.race_name, date: next.date }) : "");
  if (s.podium_hit_rate) $("metric-hit").firstElementChild.textContent = pct(s.podium_hit_rate, 0);
  if (s.baseline_podium_hit_rate) $("metric-auc").firstElementChild.textContent = pct(s.baseline_podium_hit_rate, 0);
}


async function buildTrackSelect(nextRace) {
  const sel = $("track-select");
  sel.disabled = true;
  sel.innerHTML = "";
  const onCal = state.tracks.filter((t) => t.on_calendar);
  const rest = state.tracks.filter((t) => !t.on_calendar);

  const group = (key, items) => {
    if (!items.length) return;
    const g = document.createElement("optgroup");
    g.dataset.key = key;
    g.label = t(key);
    for (const track of items) {
      const o = document.createElement("option");
      o.value = track.circuit_id;
      o.textContent = track.country && track.country !== track.name ? `${track.country} — ${track.name}` : track.name;
      g.appendChild(o);
    }
    sel.appendChild(g);
  };
  group("track.calendar", onCal);
  group("track.other", rest);

  const initial = (nextRace && nextRace.circuit_id) || (onCal[0] || state.tracks[0]).circuit_id;
  sel.value = initial;
  sel.disabled = false;
  await selectTrack(initial);
}

async function selectTrack(circuitId) {
  setMapLoading(true);
  setGridLoading(true);
  const meta = await fetch(`/api/track/${circuitId}`).then((r) => r.json());
  state.track = meta;
  updateTitle();
  const forecast = state.nextRace && state.nextRace.circuit_id === circuitId && state.nextRace.weather;
  $("weather-select").value = forecast ? forecast.preset : "dry";

  renderTrack(meta);
  $("results").hidden = true;
  state.lastResult = null;
  await loadGrid();
}

function renderTrack(meta) {
  setMapLoading(false);
  drawTrack(meta);
  $("track-caption").textContent =
    `${meta.name}${meta.locality ? ` · ${meta.locality}` : ""}${meta.country ? `, ${meta.country}` : ""}` +
    (meta.is_street ? t("track.street") : "");

  $("ro-difficulty").textContent = meta.track_difficulty ?? "—";
  $("ro-distance").textContent = meta.distance_km ?? "—";
  $("ro-corners").textContent = meta.corners ?? "—";
  $("ro-laps").textContent = meta.laps ?? "—";

  $("ro-difficulty-note").textContent = t("ro.difficulty_note");
  $("ro-deg").textContent = meta.tyre_degradation ?? "—";
  $("ro-deg-note").textContent = degWindow((meta.stats || {}).deg_window);

  renderTrackStats(meta);
}

function degWindow(window_) {
  if (!window_) return t("ro.deg_none");
  if (window_.startsWith("pit stops ")) return t("ro.deg_pitstops", { window: window_.slice(10) });
  if (window_ === "estimated from layout") return t("ro.deg_layout");
  return window_;
}

function drawTrack(meta) {
  const box = $("track-map");
  const g = meta.geometry;
  if (!g) {
    box.innerHTML = `<div class="map-empty">${t("track.no_map")}</div>`;
    return;
  }
  const corners = (g.corners || [])
    .map((c) => `<circle class="corner-dot" cx="${c.x}" cy="${c.y}" r="12"/>
                 <text class="corner-num" x="${c.x}" y="${c.y}">${c.n}</text>`)
    .join("");
  const a = ((g.start.angle + 90) * Math.PI) / 180;
  const dx = Math.cos(a) * 17, dy = Math.sin(a) * 17;
  const startLine = `<line class="start-line"
      x1="${g.start.x - dx}" y1="${g.start.y - dy}"
      x2="${g.start.x + dx}" y2="${g.start.y + dy}"/>`;

  box.innerHTML = `<svg viewBox="${g.view_box}" role="img" aria-label="${esc(t("track.layout", { name: meta.name }))}">
      <path class="track-edge" d="${g.path}"/>
      <path class="track-line" d="${g.path}"/>
      ${startLine}${corners}
    </svg>`;
}

function renderTrackStats(meta) {
  const s = meta.stats || {};
  const rows = [
    ["stat.sticky", s.grid_stickiness, pct],
    ["stat.pole", s.pole_win_rate, pct],
    ["stat.dnf", s.dnf_rate, pct],
    ["stat.gained", s.overtakes_per_race, (v) => v.toFixed(0)],
    ["stat.stops", s.stops_per_car, (v) => v.toFixed(1)],
    ["stat.sc", s.sc_rate, (v) => t("stat.sc_value", { pct: pct(v, 0), n: s.sc_races })],
    ["stat.deg", s.deg_pct_per_lap, (v) => `${v.toFixed(3)}%`],
    ["stat.length", meta.length_m, (v) => `${(v / 1000).toFixed(3)} km`],
  ];
  $("track-stats").innerHTML = rows
    .filter(([, v]) => v !== null && v !== undefined)
    .map(([k, v, f]) => `<div class="track-stat"><span>${t(k)}</span><span>${f(v)}</span></div>`)
    .join("") + `<div class="track-stat"><span>${t("stat.measured")}</span><span>${t("stat.starts", { n: s.starts ?? 0 })}</span></div>`;
}



function teamName(constructorId) {
  const team = state.teams[constructorId];
  return team ? team.name : constructorId;
}

function driverSummary(driverId) {
  const d = state.driversById.get(driverId);
  if (!d) return "";
  const c = d.career, r = d.recent, s = d.season;
  return [
    `${d.name} — ${d.team_name}`,
    t("driver.career", { races: c.races, wins: c.wins, podiums: c.podiums, avg: c.avg_finish ?? "—", dnf: pct(c.dnf_rate, 0) }),
    t("driver.recent", { seasons: r.seasons, grid: r.avg_grid ?? "—", finish: r.avg_finish ?? "—", rate: pct(r.podium_rate, 0) }),
    t("driver.season", { races: s.races, points: s.points, podiums: s.podiums, best: s.best_finish }),
  ].join("\n");
}

function historyCell(driverId) {
  if (!driverId) return `<span class="entry-history none">—</span>`;
  const h = state.trackHistory[driverId];
  if (!h) return `<span class="entry-history none">${t("history.none")}</span>`;
  const bits = [t("history.starts", { n: h.races })];
  if (h.avg != null) bits.push(t("history.avg", { pos: h.avg }));
  if (h.podiums) bits.push(t("history.podiums", { n: h.podiums }));
  if (h.wins) bits.push(t("history.wins", { n: h.wins }));
  return `<span class="entry-history">${bits.join(" · ")}</span>`;
}


function renderEntries() {
  const last = state.entries.length - 1;
  $("entries").innerHTML = state.entries
    .map((e, i) => {
      const d = state.driversById.get(e.driver_id);
      const name = d ? d.name : e.driver_id;
      return `<div class="entry" style="${teamStyle(e.constructor_id)}" title="${esc(driverSummary(e.driver_id))}">
        <b class="slot-num">${e.grid}</b>
        <span class="entry-driver">${esc(name)}${d && d.code ? `<small>${esc(d.code)}</small>` : ""}</span>
        <span class="entry-team">${esc(teamName(e.constructor_id))}</span>
        ${historyCell(e.driver_id)}
        <span class="entry-move">
          <button class="icon" type="button" data-move="-1" data-index="${i}" ${i === 0 ? "disabled" : ""} aria-label="${esc(t("grid.move_up", { name }))}">▲</button>
          <button class="icon" type="button" data-move="1" data-index="${i}" ${i === last ? "disabled" : ""} aria-label="${esc(t("grid.move_down", { name }))}">▼</button>
        </span>
      </div>`;
    })
    .join("");

  const source = state.edited ? "what_if" : (STAGE_ORDER[state.gridSource] ? state.gridSource : "expected");
  $("grid-source").textContent = t(`source.${source}`);
  $("entries-hint").textContent = `${t("grid.cars", { n: state.entries.length })} ${t(`source.${source}.hint`)}`;
  $("btn-reset-grid").hidden = !state.edited;
  $("btn-predict").disabled = state.entries.length < 2 || $("btn-predict").classList.contains("is-loading");
  syncStickyCta();
}

function moveEntry(index, step) {
  const target = index + step;
  if (target < 0 || target >= state.entries.length) return;
  const entries = [...state.entries];
  [entries[index], entries[target]] = [entries[target], entries[index]];
  state.entries = entries.map((e, i) => ({ ...e, grid: i + 1 }));
  state.edited = true;
  renderEntries();
  const button = $("entries").querySelector(`[data-index="${target}"][data-move="${step}"]`)
    || $("entries").querySelector(`[data-index="${target}"]`);
  if (button && !button.disabled) button.focus();
}

function resetGrid() {
  state.entries = state.original.map((e) => ({ ...e }));
  state.edited = false;
  renderEntries();
}

async function loadGrid() {
  const params = new URLSearchParams({ season: state.season });
  if (state.track) params.set("circuit_id", state.track.circuit_id);
  const data = await fetch(`/api/lineup?${params}`).then((r) => r.json());
  state.gridSource = data.source;
  state.entries = data.entries
    .map((e, i) => ({ ...e, grid: e.grid ?? i + 1 }))
    .sort((a, b) => a.grid - b.grid)
    .map((e, i) => ({
      driver_id: e.driver_id,
      constructor_id: e.constructor_id,
      grid: i + 1,
      quali_position: e.quali_position ?? null,
      quali_gap_pct: e.quali_gap_pct ?? null,
    }));
  state.original = state.entries.map((e) => ({ ...e }));
  state.edited = false;
  state.trackHistory = data.track_history || {};
  renderEntries();
  setGridLoading(false);
}


async function predict() {
  const btn = $("btn-predict");
  if (btn.classList.contains("is-loading")) return;
  setBusy(btn, true, t("btn.predicting"));
  syncStickyCta();
  const results = $("results");
  results.hidden = false;
  results.setAttribute("aria-busy", "true");
  $("results-chip").textContent = "";
  resultsSkeleton();
  try {
    const body = {
      circuit_id: state.track.circuit_id,
      weather: $("weather-select").value,
      laps: state.track.laps,
      distance_km: state.track.distance_km,
      season: parseInt(state.season),
      grid_source: state.edited ? "what_if" : state.gridSource,
      base_source: state.gridSource,
      entries: state.entries,
    };
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => r.json());
    if (res.error) throw new Error(res.error);
    renderResults(res);
  } catch (err) {
    state.lastResult = null;
    $("results").hidden = false;
    $("podium").innerHTML = `<p class="hint">${esc(t("predict.failed", { msg: err.message }))}</p>`;
    $("order").innerHTML = "";
  } finally {
    results.setAttribute("aria-busy", "false");
    setBusy(btn, false, t("btn.predict"));
    btn.disabled = state.entries.length < 2;
    syncStickyCta();
  }
}


function dnfBreakdown(e) {
  const crash = e.p_crash || 0;
  const mech = Math.max((e.p_dnf || 0) - crash, 0);
  return [
    t("dnf.total", { pct: pct(e.p_dnf || 0, 1) }),
    t("dnf.crash", { pct: pct(crash, 1) }),
    t("dnf.mech", { pct: pct(mech, 1) }),
    t("dnf.dsq", { pct: pct(e.p_dsq || 0, 1) }),
  ].join("\n");
}

function actualText(e) {
  if (!e.actual) return "";
  return e.actual.classified ? t("order.actual", { pos: e.actual.position }) : t("order.actual_dnf");
}

function noteText(note) {
  const key = `note.${note.code}`;
  const text = t(key, note.values || {});
  return text === key ? "" : text;
}

function notesFor(e) {
  if (e.note_codes) return e.note_codes.map(noteText).filter(Boolean);
  return e.notes || [];
}

function renderResults(res) {
  $("results").hidden = false;
  state.lastResult = res;
  $("share-hint").textContent = "";
  const c = res.conditions;
  $("results-chip").textContent =
    t("results.chip", { track: res.track.name, weather: weatherLabel(c.weather), deg: c.tyre_degradation }) +
    (res.mode === "backtest" ? t("results.backtest") : "") +
    (res.model && res.model.stage === "pre_qualifying" ? t("results.prequali") : "");

  const medals = ["#d4a017", "#9aa5b1", "#b06a3b"];
  $("podium").innerHTML = res.entries
    .slice(0, 3)
    .map(
      (e, i) => `<div class="pod" style="--medal:${medals[i]};${teamStyle(e.constructor_id)};--i:${i}">
        <span class="pod-number" aria-hidden="true">${i + 1}</span>
        <div class="pod-place">${esc(t("pod.from", { place: t(`place.${i + 1}`), grid: e.grid }))}</div>
        <div class="pod-name">${esc(e.name)}</div>
        <div class="pod-team">${esc(e.team_name)}</div>
        <div class="pod-prob">${pct(e.p_podium, 0)}<small>${t("pod.chance")}</small></div>
      </div>`
    )
    .join("");

  const head = `<div class="order-row head">
      <span>${t("order.pos")}</span><span>${t("order.driver")}</span><span>${t("order.team")}</span>
      <span>${t("order.prob")}</span><span>${t("order.podium")}</span><span>${t("order.win")}</span><span>${t("order.dnf")}</span>
    </div>`;
  const best = Math.max(...res.entries.map((e) => e.p_podium), 0.01);
  $("order").innerHTML = head + res.entries
    .map((e) => {
      const notes = notesFor(e).map((n) => `<span>${esc(n)}</span>`).join("");
      const range = e.finish_range ? t("order.range", { a: e.finish_range[0], b: e.finish_range[1] }) : "";
      const slot = e.p_podium_grid != null ? ` · ${t("order.slot", { pct: pct(e.p_podium_grid, 0) })}` : "";
      const line = t("order.line", { grid: e.grid, finish: e.expected_finish }) + range + slot + actualText(e);
      return `<div class="order-row" style="${teamStyle(e.constructor_id)}">
          <span class="order-pos">${e.expected_position}</span>
          <span class="order-name"><b>${esc(e.name)}${driverCode(e.driver_id) ? `<em>${esc(driverCode(e.driver_id))}</em>` : ""}</b><small>${esc(line)}</small></span>
          <span class="order-team">${esc(e.team_name)}</span>
          <span class="bar"><i style="width:${((e.p_podium / best) * 100).toFixed(1)}%"></i></span>
          <span class="order-num">${pct(e.p_podium, 1)}</span>
          <span class="order-num"><small>${pct(e.p_win, 1)}</small></span>
          <span class="order-num" title="${esc(dnfBreakdown(e))}"><small>${pct(e.p_dnf || 0, 0)}</small></span>
        </div>
        ${notes ? `<div class="order-notes">${notes}</div>` : ""}`;
    })
    .join("");
}


function podiumImage(res) {
  const W = 1200, H = 630;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const g = canvas.getContext("2d");
  const font = (weight, size) => `${weight} ${size}px "Titillium Web", "Segoe UI", system-ui, sans-serif`;

  g.fillStyle = "#15151e";
  g.fillRect(0, 0, W, H);
  g.fillStyle = "#e10600";
  g.fillRect(0, 0, W, 8);
  g.fillRect(60, 64, 10, 72);
  const logo = document.querySelector(".brand-logo.for-dark");
  if (logo && logo.complete && logo.naturalWidth) {
    const h = 64, w = Math.round(logo.naturalWidth * h / logo.naturalHeight);
    g.drawImage(logo, W - 60 - w, 66, w, h);
  }

  const race = res.race ? res.race.race_name : res.track.name;
  g.fillStyle = "#e9edf3";
  g.font = font(700, 46);
  g.font = font(900, 46);
  g.fillText(race.toUpperCase(), 92, 104);
  g.fillStyle = "#939cab";
  g.font = font(400, 26);
  const when = res.race ? `${res.race.date} · ` : "";
  g.fillText(`${when}${res.track.name} · ${weatherLabel(res.conditions.weather)}`, 92, 144);

  const medals = ["#d4a017", "#9aa5b1", "#b06a3b"];
  res.entries.slice(0, 3).forEach((e, i) => {
    const x = 60 + i * 370, y = 200, w = 340, h = 300;
    g.fillStyle = "#1f1f2b";
    g.fillRect(x, y, w, h);
    g.fillStyle = medals[i];
    g.fillRect(x, y, w, 6);
    g.fillStyle = TEAM_COLOURS[e.constructor_id] || "#9c9cab";
    g.fillRect(x, y + 6, 6, h - 6);
    g.fillStyle = "#939cab";
    g.font = font(600, 22);
    g.fillText(t("share.from", { place: t(`place.${i + 1}`), grid: e.grid }), x + 32, y + 50);
    g.fillStyle = "#e9edf3";
    g.font = font(700, 34);
    const [first, ...rest] = e.name.split(" ");
    g.fillText(rest.length ? first : e.name, x + 32, y + 104);
    if (rest.length) g.fillText(rest.join(" "), x + 32, y + 146);
    g.fillStyle = "#939cab";
    g.font = font(400, 22);
    g.fillText(e.team_name, x + 32, y + 184);
    g.fillStyle = "#e9edf3";
    g.font = font(700, 64);
    const chance = pct(e.p_podium, 0);
    g.fillText(chance, x + 32, y + 262);
    const offset = g.measureText(chance).width + 12;
    g.fillStyle = "#939cab";
    g.font = font(400, 20);
    g.fillText(t("pod.chance"), x + 32 + offset, y + 262);
  });

  g.fillStyle = "#939cab";
  g.font = font(400, 22);
  g.fillText(t("share.footer", { trained: res.model.trained_through }), 60, 578);
  return canvas;
}

async function sharePodium() {
  const res = state.lastResult;
  if (!res) return;
  const canvas = podiumImage(res);
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
  const name = `${(res.race ? res.race.race_name : res.track.name).replace(/[^a-z0-9]+/gi, "-").toLowerCase()}-podium.png`;
  const file = new File([blob], name, { type: "image/png" });
  const text = t("share.text", { list: res.entries.slice(0, 3).map((e) => `${e.name} ${pct(e.p_podium, 0)}`).join(", ") });
  try {
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({ files: [file], text });
      return;
    }
  } catch (err) {
    if (err && err.name === "AbortError") return;
  }
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $("share-hint").textContent = t("share.saved", { name });
}


function resetChampionship() {
  $("champ-chip").textContent = t("champ.chip");
  $("champ-hint").textContent = t("champ.hint");
  $("btn-champ").textContent = t("champ.btn");
}

async function loadChampionship() {
  const btn = $("btn-champ");
  setBusy(btn, true, t("champ.running"));
  const tables = $("champ-tables");
  tables.hidden = false;
  tables.setAttribute("aria-busy", "true");
  const skeleton = `<div class="champ-row skeleton-row" aria-hidden="true"><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span><span class="skeleton skeleton-line short"></span><span></span></div>`;
  $("champ-drivers").innerHTML = skeleton.repeat(8);
  $("champ-teams").innerHTML = skeleton.repeat(6);
  try {
    const res = await fetch("/api/championship").then((r) => r.json());
    if (res.error) throw new Error(res.error);
    state.championship = res;
    renderChampionship(res);
    btn.hidden = true;
  } catch (err) {
    tables.hidden = true;
    $("champ-hint").textContent = t("champ.failed", { msg: err.message });
    setBusy(btn, false, t("champ.retry"));
  } finally {
    tables.setAttribute("aria-busy", "false");
  }
}

function renderChampionship(res) {
  const left = res.races_left;
  $("champ-chip").textContent = left ? t("champ.left", { races: left, sprints: res.sprints_left }) : t("champ.done");
  $("champ-hint").textContent = left
    ? t("champ.summary", { sims: res.sims.toLocaleString(locale()) }) +
      (res.sprints_known ? t("champ.sprints") : t("champ.no_sprints"))
    : t("champ.final");
  $("champ-drivers").innerHTML = champTable(res.drivers.slice(0, 10), t("champ.driver"), (r) =>
    `${esc(r.name)}${r.team_name ? `<small>${esc(r.team_name)}</small>` : ""}`);
  $("champ-teams").innerHTML = champTable(res.teams, t("champ.team"), (r) => esc(r.name));
  $("champ-tables").hidden = false;
}

function champTable(rows, title, label) {
  const best = Math.max(...rows.map((r) => r.p_title), 0.01);
  const head = `<div class="champ-row head"><span>${t("champ.now")}</span><span>${title}</span><span>${t("champ.expected")}</span><span>${t("champ.title_col")}</span><span></span></div>`;
  return head + rows
    .filter((r) => r.points_now > 0 || r.expected_points > 0)
    .map((r) => `<div class="champ-row" style="${teamStyle(r.team_id || r.id)}">
        <span class="order-num">${r.points_now.toFixed(0)}</span>
        <span class="order-name"><b>${label(r)}</b></span>
        <span class="order-num" title="${esc(t("champ.range", { a: r.points_p10.toFixed(0), b: r.points_p90.toFixed(0) }))}">${r.expected_points.toFixed(0)}<small> (${r.points_p10.toFixed(0)}–${r.points_p90.toFixed(0)})</small></span>
        <span class="order-num">${r.p_title >= 0.001 ? pct(r.p_title, r.p_title < 0.1 ? 1 : 0) : "&lt;0.1%"}</span>
        <span class="bar"><i style="width:${((r.p_title / best) * 100).toFixed(1)}%"></i></span>
      </div>`)
    .join("");
}


async function onLanguageChanged() {
  localizeSeasonOptions();
  updateTitle();
  for (const group of $("track-select").querySelectorAll("optgroup")) group.label = t(group.dataset.key);
  if (state.boot) renderModelBadge(state.boot);
  if (state.track) renderTrack(state.track);
  if (state.entries.length) renderEntries();
  if (state.lastResult) renderResults(state.lastResult);
  if (state.championship) renderChampionship(state.championship);
  else resetChampionship();
  if ($("about").open) await renderAbout();
}

function wireControls() {
  $("season-select").onchange = async (e) => {
    state.season = e.target.value;
    await loadSeasonData();
  };
  $("track-select").onchange = (e) => selectTrack(e.target.value);
  $("btn-sync").onclick = syncLiveGrid;
  $("btn-predict").onclick = predict;
  $("btn-reset-grid").onclick = resetGrid;
  $("btn-champ").onclick = loadChampionship;
  $("btn-share").onclick = sharePodium;
  $("entries").onclick = (e) => {
    const button = e.target.closest("[data-move]");
    if (button) moveEntry(Number(button.dataset.index), Number(button.dataset.move));
  };
  $("btn-about").onclick = showAbout;
}

async function syncLiveGrid() {
  const btn = $("btn-sync");
  setBusy(btn, true, t("btn.syncing"));
  try {
    const res = await fetch("/api/sync", { method: "POST" }).then((r) => r.json());
    if (res.error) throw new Error(res.error);

    await loadSeasonData();
    alert(t("sync.done"));
  } catch (err) {
    alert(t("sync.failed", { msg: err.message }));
  } finally {
    setBusy(btn, false, t("btn.sync"));
  }
}

const STAGE_ORDER = { expected: 1, expected_practice: 2, openf1: 3, qualifying: 3, starting_grid: 4, race: 5 };

function stageLabel(source) {
  return STAGE_ORDER[source] ? t(`source.${source}`) : source;
}

function stagesRow(r) {
  const stages = r.stages || [];
  if (stages.length < 2) return "";
  const items = stages
    .map((st) => {
      const when = new Date(st.recorded_at).toLocaleString(locale(), { weekday: "short", hour: "2-digit", minute: "2-digit" });
      const hits = st.podium_hits != null ? ` <b>${st.podium_hits}/3</b>` : "";
      return `<li><span>${esc(stageLabel(st.grid_source))}, ${esc(when)}:</span> ${st.predicted_podium.map(esc).join(", ")}${hits}</li>`;
    })
    .join("");
  return `<tr class="stages-row"><td colspan="4"><ol class="stages">${items}</ol></td></tr>`;
}

async function trackRecordHtml() {
  let card;
  try {
    card = await fetch("/api/ledger").then((r) => r.json());
  } catch (e) {
    return "";
  }
  const s = card.summary || {};
  const rows = (card.races || [])
    .map((r) => `<tr><td>${esc(r.race_name)}</td>
      <td>${r.predicted_podium.map(esc).join(", ")}</td>
      <td>${r.status === "scored" ? (r.actual_podium || []).map(esc).join(", ") : t("record.not_run")}</td>
      <td>${r.status === "scored" ? `${r.podium_hits}/3${r.winner_hit ? t("record.winner") : ""}` : "—"}</td></tr>
      ${stagesRow(r)}`)
    .join("");
  const headline = s.races
    ? `<p>${t("record.headline", { n: s.races, hit: pct(s.podium_hit_rate, 0), grid: pct(s.grid_podium_hit_rate, 0), winner: pct(s.winner_hit_rate, 0) })}</p>`
    : `<p>${t("record.empty")}</p>`;
  const bySource = Object.entries(s.by_source || {})
    .sort(([a], [b]) => (STAGE_ORDER[a] || 0) - (STAGE_ORDER[b] || 0))
    .map(([src, v]) => `<li>${esc(t("record.source_line", { label: stageLabel(src), hit: pct(v.podium_hit_rate, 0), n: v.races }))}</li>`)
    .join("");
  return `<h3>${t("record.title")}</h3>${headline}
    ${bySource ? `<p>${t("record.by_source")}</p><ul>${bySource}</ul>` : ""}
    ${rows ? `<table class="val-table ledger-table"><tr><th>${t("record.race")}</th><th>${t("record.predicted")}</th><th>${t("record.actual")}</th><th>${t("record.hits")}</th></tr>${rows}</table>` : ""}`;
}

async function renderAbout(withRecord = true) {
  const m = state.model;
  const rows = (m.validation || [])
    .map((v) => `<tr><td>${v.season}</td><td>${v.races}</td><td>${v.roc_auc.toFixed(3)}</td>
      <td>${pct(v.podium_hit_rate, 0)}</td><td>${pct(v.baseline_podium_hit_rate, 0)}</td>
      <td>${signed(v.lift_vs_grid)}</td>
      <td>${pct(v.winner_top1_rate, 0)}</td><td>${pct(v.baseline_winner_top1_rate, 0)}</td></tr>`)
    .join("");
  const imp = (m.importance || [])
    .map((f) => `<li>${esc(f.feature)}</li>`).join("");

  $("about-body").innerHTML = `${t("about.body", { imp })}
    <table class="val-table">
      <tr><th>${t("val.season")}</th><th>${t("val.races")}</th><th>AUC</th><th>${t("val.hit")}</th><th>${t("val.grid")}</th>
          <th>${t("val.lift")}</th><th>${t("val.winner")}</th><th>${t("val.pole")}</th></tr>
      ${rows}
    </table>
    <div id="track-record" aria-busy="${withRecord ? "false" : "true"}">${withRecord ? await trackRecordHtml() : RECORD_SKELETON}</div>`;
}

const RECORD_SKELETON = `<h3 class="skeleton skeleton-line short"></h3><p class="skeleton skeleton-line"></p><p class="skeleton skeleton-line"></p>`;

async function showAbout() {
  await renderAbout(false);
  const dialog = $("about");
  dialog.showModal();
  dialog.querySelector("h2").focus({ preventScroll: true });
  dialog.scrollTop = 0;
  const record = $("track-record");
  record.innerHTML = await trackRecordHtml();
  record.setAttribute("aria-busy", "false");
}

function pct(v, digits = 0) {
  return pctText(v, digits);
}

function signed(v) {
  return v == null ? "—" : `${v >= 0 ? "+" : ""}${(v * 100).toFixed(0)} pp`;
}

boot();
