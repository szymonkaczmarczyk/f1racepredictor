# Race Predictor — model and data

Technical notes behind the predictions: where the data comes from, every feature, how the model is trained and validated, what was tried and rejected, how the race is simulated, and the honest limits. The project overview, setup and screenshots are in the [README](../README.md) (Polish version: [READMEpl.md](../READMEpl.md)).

---

## Where the data comes from

| Source | What it gives us |
| --- | --- |
| [Jolpica-F1](https://api.jolpi.ca/ergast/f1) (the maintained continuation of Ergast) | every race, result, grid slot, qualifying time, sprint and pit stop from 1996 to today |
| [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) | traced circuit outlines (GeoJSON, from OpenStreetMap) |
| [OpenF1](https://openf1.org) | cancellations, session times, sprint weekends, qualifying results before the official feed has them, the official starting grid with penalties |
| [FastF1](https://docs.fastf1.dev) | lap-by-lap practice timing from 2018, summarised per driver and weekend; safety cars, virtual safety cars and red flags of every race since 2018 |
| [Open-Meteo](https://open-meteo.com) | measured rain at every past race (ERA5 archive) and the forecast for the next one |

Nothing is hand-entered. Corner counts are measured off the traced geometry,
lap counts and race distances come from the races themselves, and track
difficulty and tyre degradation are percentile ranks over measured history
rather than opinions.

---

## The idea in one paragraph

Every row is one car on one starting grid. The features describe what was known
**before the lights went out**: where it starts, how the driver has been going,
how quick the car is, what that driver has specifically done at that circuit, and
what that circuit tends to do to a race. The label is whether the car finished in
the top three. Because the sport keeps changing, training rows are weighted by
how recent they are; and because a random train/test split would let the model
peek at the future, validation walks forward one season at a time.

---

## Feature engineering

72 features, built in a single chronological pass. A row for race *R* can only
ever see races before *R* — the store emits features first and folds in that
race's own result afterwards, which is what makes the validation honest.

**Grid and qualifying** — grid slot (raw and normalised to field size),
qualifying position, percentage gap to pole, whether they reached Q3, any grid
penalty (grid minus qualifying position), pit lane starts.

**Driver form** — decayed means of finishing position, podium and win rate,
points rate, DNF rate, average grid, places gained, qualifying gap, and the rate
of beating their own team mate. Career starts and career podium rate, shrunk
towards a prior so one podium from one start does not read as a 100% record.

**Team pace** — the same treatment for the car: finishing position, podium rate,
points rate, reliability, qualifying gap (the cleanest read on raw car speed),
best finisher per race, and an estimated pace rank against the other teams still
racing (teams that have left the sport drop out of it after three races).

**Driver × circuit** — how this driver has actually gone *here*: starts, average
and best finish, podium rate, places gained, plus `drv_track_vs_form`, which is
their record here relative to their record everywhere. Negative means they
over-perform at this track. The team's record at the circuit sits alongside it.

**Circuit character** — measured, not assumed: how much the order shuffles
(`circuit_volatility`), how often a top-three grid slot converts to a podium,
how often pole wins, the retirement rate, the scheduled lap count (the median of
the last three visits, not the laps actually run — a race cut short would
otherwise describe its own ending) and race distance, plus the difficulty and
tyre-degradation indices.

**Conditions** — `is_wet`, and a driver's own wet-weather record.

**Regulation era** — `era_races`, how many races into the current set of
technical rules the sport is (see below).

**Practice pace** (2018 on) — from that weekend's FP1–FP3: each driver's best
lap, their long-run pace (the median lap of their quickest stint of five or more
green-flag laps, cool-down laps dropped) and their team's best long run, each as
a percentage off the best in the field, plus where the best lap and the long run
rank in this field. Practice runs before the race, so it is fair game.
Walk-forward, adding it improved every probability score in the shipped pipeline
(log loss 0.2156 → 0.2148, win Brier 0.0306 → 0.0302) while the ranking metrics
stayed level; on the raw podium head it lifted winner accuracy by five points,
most of which the anchoring to grid order absorbs. Practice laps are noisy —
fuel loads and programmes are unknown — which is why the long run is a median
and only one input among many.

**Relative to the field** — a podium is not won in isolation, it is won against
the other nineteen cars. Scoring each entry independently misses that entirely:
P5 behind three dominant cars is a very different proposition from P5 in a season
where six teams can win. So each entry is also described relative to the grid it
is actually on — the rank of its car's pace and its driver's form within *this*
field, how far the grid slot sits from where the car's pace says it belongs, how
many cars ahead are in quicker machinery (the ones you will not pass) versus
slower (the places you can take), how spread out the field is, the team's best
grid slot and the gap to the team mate, and the qualifying gap to the fastest car
that is not your own team's.

### Three pieces worth calling out

**Old races count less.** Every training row carries a weight of
`0.5 ** (years_ago / half_life)`. A race from 2005 still contributes to a 2026
prediction, at a small fraction of the weight of a race from last month. Rolling
form decays on the same principle: 0.93 per race for form, 0.75 per year for a
driver's record at a given circuit. This is the direct answer to "a 2005 result
should not carry the same weight as a 2025 one".

**Weather is measured, not read back out of the race.** Ergast carries no weather
data. An earlier version recovered it from race pace — each race's winning pace
compared with the circuit's norm — and `is_wet` ranked as the second most useful
feature. That was a leak: the index was computed from the race it described, so
a safety car, a red flag or a race cut short told that race's own training row
how it had gone. Now every race gets the rain measured by the ERA5 reanalysis
(Open-Meteo archive) at the circuit's coordinates, from an hour before the start
to two hours after, scaled so 4 mm or more is fully wet. That is something a
forecast can know in advance, and it is the same quantity the app feeds in from
the Open-Meteo forecast for the next race. 9% of races since 1996 come out wet.

Measured walk-forward, dropping the leak cost about 0.004 of log loss on the
podium head alone — the honest price of the pace index having peeked — while
measured rain picked the winner better than either the pace index or no weather
at all. ERA5 is coarse and misses some local downpours (the 2007 Nürburgring
cloudburst barely registers); `scripts/02_build_features.py --wet-source pace`
rebuilds with the old index for comparison.

**Each new set of rules resets part of the picture.** 1998, 2009, 2014, 2017,
2022 and 2026 brought new technical regulations, and a team's form from the old
rules says much less about the new ones. At the first race of each new era the
accumulated team statistics are faded to 30% of their weight, so the first few
results under the new rules take over quickly, and `era_races` tells the model
how far into the era it is. Walk-forward, this improved log loss and winner
accuracy overall, and in the first eight races of each new era raised winner
accuracy from 34% to 44%.

---

## The model

`HistGradientBoostingClassifier` (scikit-learn), log loss, no early stopping —
sklearn's built-in early stopping carves out a *random* validation slice, which
leaks the future into a time series.

Three heads share the feature matrix: **podium** (the headline), **win**, and
**points finish**.

### Making the three heads agree

They are separate models, so nothing stops the win head claiming a driver has a
67% chance of winning while the podium head gives the same driver 46% — which
cannot be true, because every win is a podium. Left alone it also scrambles the
displayed order: the car with the best podium chance ends up listed third.

So the normalisation is nested. Points-finish is scaled to the ten places on
offer and capped by each car's chance of reaching the flag, podium to three but
capped by points, and win to one but capped by podium. Those coherent numbers are
the targets the race simulation is calibrated to (see *Simulating the race*),
and the app orders the field by expected points from that simulation, so the
ranking always agrees with the probabilities printed next to it.

### What was tried and rejected

Monotonic constraints looked like an obvious win. Some relationships in this
sport are not in question — a car starting further back is not *more* likely to
reach the podium, all else equal — so pinning ~40 features to their known
direction should stop the model inventing wiggles from thin slices of history.

Measured under the walk-forward protocol, it made things **worse**: about three
points of podium@3 and half a point of AUC. sklearn's constrained split search
gives up more fit quality than the prior buys back. The code is still there
(`make_model(monotonic=True)`, and the direction map in `train.py`) so the
experiment can be re-run, but it is off by default; `scripts/04_tune.py` writes
the comparison to `models/tuning_report*.json`.

Carrying team history across renames looked just as obvious. Jolpica gives a
team a new id whenever it changes its name, so Audi (2026) started with no
form while it is the Sauber factory and staff; the same goes for AlphaTauri ->
RB, Renault -> Alpine and Racing Point -> Aston Martin. Mapping every id onto
its factory lineage made the walk-forward numbers slightly **worse** (log loss
+0.0005, AUC -0.0004, exact podium -0.7 points), and worst in 2026 itself
(podium@3 -6.7 points): a renamed team is often a genuinely different car, and
the fade of team form at each new rules era already handles the overlap. The
mapping was not kept.

Sprint results looked like the freshest race pace there is: on a sprint weekend
the sprint is a short race on the same track, a day earlier. Three features
(sprint finish, places gained, sprint finish against the grid) changed nothing
measurable on the 29 sprint weekends since 2021 (podium@3 unchanged, log loss
+0.0001) and cost 0.6 points of podium@3 across all seasons. Twenty-nine
weekends are too few for the model to learn from, and the qualifying that sets
the grid already carries most of what the sprint shows.

How often a circuit brings out the safety car looked like the missing half of
"how much the order shuffles here". From FastF1's track status, every race since
2018 has its safety cars, virtual safety cars and red flags; two features (share
of races with a safety car or red flag, neutralisations per race, both shrunk
towards the field average) left races since 2018 flat (podium@3 unchanged, log
loss -0.0003) and cost 0.9 points of winner accuracy across all seasons. The
circuit's volatility and retirement rate already carry it. Like tyre wear per
lap, the figure is shown in the circuit panel and not modelled.

---

## Validation

No random splits. For each season *S*, the model trains on every season before
*S* and is scored on *S*. Nothing from the future is ever in the training set.

Reported per season:

- **ROC AUC, log loss, Brier** — how good the podium probabilities are, plus the
  Brier score of the win and points probabilities. All of them are scored on the
  final, simulated numbers the app displays.
- **podium@3** — of the three podium slots, how many the model's top three called.
- **exact** — how often all three were right (in any order).
- **winner** — how often the top-ranked driver won.
- **grid@3 / pole** — the same measures for the naive baselines: read the podium
  off the top three grid slots, and the win off pole. Plus the **lift** over them.

Those baseline columns are what keep everybody honest. A model with a beautiful
AUC that ranks worse than grid order has not earned its place, and the training
script prints the comparison every time.

`scripts/04_tune.py` runs the same protocol across model configurations and picks
on podium@3, not on AUC. `scripts/05_diagnose.py` goes further and asks *where*
the model disagrees with grid order and whether it was right to.

### What it actually scores

Thirteen seasons, 2014–2026 (through Baku 2026), 267 races, each one predicted by
a model that had never seen it or anything after it. Averages are weighted by
races:

| | model | leaky version | baseline |
| --- | --- | --- | --- |
| ROC AUC | 0.939 | 0.941 | — |
| log loss (podium) | **0.213** | 0.214 | — |
| Brier (podium) | **0.065** | 0.066 | — |
| Brier (win) | **0.030** | 0.036 | — |
| Brier (points) | **0.155** | 0.186 | — |
| podium@3 | **0.697** | 0.698 | 0.689 (grid order) |
| exact podium | **0.300** | 0.285 | 0.281 |
| winner | **0.558** | 0.544 | 0.543 (pole) |

The "leaky version" is this pipeline before the fixes described above: weather
read back out of the race itself, lap counts from the laps actually run, a car
pace rank padded with long-gone teams, and a simulation that ignored the win and
points heads. Its probability scores looked slightly better only because some of
its features had seen the result. With the leaks gone, practice pace added and
the hyperparameters re-tuned for the current feature set, the podium numbers
hold level, the exact podium and the winner calls improve, and the win and
points probabilities are much better calibrated (see `calibration` in
`models/validation_report.json`; every bin with a meaningful sample is within a
few points of what actually happened).

The re-tuning (`scripts/04_tune.py --preset current --ensemble`) compared a
dozen configurations walk-forward and settled on a more regularised model — at
least 60 rows per leaf and 400 boosting rounds instead of 40 and 500 — which
improved every metric at once. It was chosen on the same seasons it is scored on
here, so a little of that gain may be luck of the draw.

Read the result honestly. The model edges grid order on naming the podium and
the exact podium, and pole on picking the winner by about four races in 267 —
margins inside the noise. It does not beat the grid at naming names. Where it
genuinely adds something the baseline cannot is calibrated probabilities: grid
order gives you a list, not a probability.

### Why the podium is so hard to beat

`scripts/05_diagnose.py` answers this directly:

```
a top-three start converts to a podium         68.3% of the time
a start outside the top three converts          5.6% of the time
```

Every time the model promotes a car into its predicted top three, it drops one
with a 68% claim in favour of one whose base rate is 6%. Those promotions come
off 37.5% of the time — six times the base rate, so the model is picking the
right candidates — but 37.5% still loses to 62%. Overriding grid order is a bet
that has to be nearly right just to break even, and the model only makes it 0.44
times a race.

And the reason it cannot be made more right: when a top-three starter *does* miss
the podium, **70% of the time they finished the race.** They were beaten on pace,
strategy or a start. Only 20% is a mechanical failure and 8% an incident — the
parts a model has any hope of anticipating from reliability history. The rest is
not sitting in the data waiting to be found.

That finding drove the final configuration. The regularisation is heavier than a
default gradient booster would use, because a loosely-fitted model spends its
extra capacity making exactly the bets it cannot win. Tightening it moved
podium@3 up while giving the best calibration of anything tried. Re-run the
sweep with `scripts/04_tune.py` after changing the features; the old reports
were measured on a feature set that no longer exists and have been removed.

### Anchoring to the grid

Regularisation was not enough on its own. Re-running the diagnostic settled it:
the model overrode grid order 0.43 times a race and was right **42.9%** of the
time, against the **57%** it would have scored by leaving the order alone — and
its confidence did not separate the good overrides from the bad, the most
confident bucket hitting only 41%. The overrides were not a wash, they were a
loss.

So the model no longer gets to disagree for free. Each head is blended with the
empirical conversion rate for that starting slot, in log-odds:

```
logit(p) = w · logit(p_model) + (1 − w) · logit(p_grid_slot)
```

At `w = 1` nothing changes; at `w = 0` the model is ignored. The weight is
measured, not chosen — fitted on the walk-forward predictions, every one of them
made on a season the model had never seen. It lands at 0.45 for the podium head,
0.30 for the win head and 0.75 for points: against the grid, the model is worth
between a third and a half of a vote on who reaches the podium.

One detail mattered more than expected. Fitting those weights on podium accuracy
seemed natural and measured worse: it drove the points head's weight to zero,
discarding the model entirely, and cost five points of winner accuracy — a podium
metric says nothing about who wins or who scores. Judging each head by Brier
score on its own target fixed both, at identical podium accuracy.

### Before qualifying: a second model

The anchor above assumes the grid is real. Before qualifying it is not: the app
only has an expected grid (each driver's median gap to pole over the last three
qualifying sessions, which matches the real grid at a rank correlation of about
0.7). Anchoring hard to a guess threw away exactly what should matter most on a
Friday, recent form and record at the circuit: with the grid-trained model and
its anchor, the predicted podium differed from the expected grid's top three in
only 7% of races.

So there is a second set of heads, trained on the grid as it was expected before
each race. While building the features, the expected grid of every race since
1996 is rebuilt from the qualifying sessions before it, with the grid-slot
priors as they stood that day (`src/features/prequali.py`,
`data/processed/features_prequali.csv`). The heads, their grid priors and their
blend weights are fitted and validated walk-forward like the main ones, and the
app uses them whenever the grid is expected rather than known.

Over 2014-2026, predicting from the expected grid:

| | grid-trained model, anchored | pre-qualifying model | expected grid alone |
| --- | --- | --- | --- |
| podium places called | 59.2% | 60.0% | 58.8% |
| winner called | 37.1% | 42.1% | 35.9% |
| podium Brier | 0.084 | 0.078 | |
| podium log loss | 0.267 | 0.249 | |
| predicted podium differs from the grid | 7% of races | 24% of races | |

After qualifying the grid-trained heads take over again; there the grid really
is the best single predictor, and the anchor is what keeps the model honest.
Each driver's line in the result shows what the grid slot alone would give
(*grid slot alone 49%*), so it is visible how far form, car pace and circuit
history move the number.

### Simulating the race

The three heads are then run through 20,000 simulated races
(`src/models/simulate.py`). Every number the app shows is read off that single
distribution, so exactly one car wins and three reach the podium by
construction, `P(win) ≤ P(podium) ≤ P(points)` always holds, and the finishing
order cannot contradict the probabilities printed beside it.

The simulation is a **stage-wise Plackett–Luce** race. Each car carries three
strengths, one per head: the winner is drawn with the win strengths, P2–P3 from
the remaining cars with the podium strengths, and the rest of the order with the
points strengths. The strengths are calibrated so the simulated marginals match
all three heads at once.

An earlier version had one pace number per car, calibrated to the podium head
only, plus a fixed amount of race noise — so the win and points heads were
trained, blended and then silently ignored, and every win probability on screen
was really a by-product of that noise constant. It was badly overconfident: when
it gave the favourite 87% to win, the favourite won 52% of the time. Measured
walk-forward over 264 races, the stage-wise version cut the Brier score of the
win probabilities by 16% and of the points probabilities by 16%, left the podium
probabilities where they were, and picked the winner more often (0.519 → 0.534).

The validation now scores these final, simulated probabilities — the ones the
app displays — for all three outcomes, and prints a calibration table for each
(`calibration` in `models/validation_report.json`).

Each simulated race also rolls for retirement, with the two causes separated:
mechanical failure belongs to the car and ignores the circuit, while crashing out
belongs to the driver, is scaled by what that circuit does to a field and by
their own record at it, and is tilted towards the back of the grid where the
fighting is. That is why Leclerc's chance of crashing out reads 9.5% at Monaco
and 1.1% at Zandvoort.

---

## Staying in step with the real calendar

The calendar is not "the first race without results" any more; it is read off
the clock. Every race gets a status — `completed`, `upcoming`, `in_progress`,
`awaiting_results` (run, but the feed has not caught up) or `cancelled` — and the
next race is the first one whose start time is still ahead. A race whose date
has passed without results no longer blocks the calendar.

- **Moved, postponed and cancelled races.** Races are identified by circuit and
  start time, never by name or country. A Grand Prix moved to another country
  (2026's "Bahrain Grand Prix in Malaysia") is modelled on the circuit it is
  actually run at. Cancellations come from OpenF1's `is_cancelled` flag; the
  two feeds are matched on dates, since a moved race keeps its old name in one
  of them and a country can host more than one race.
- **Season** comes from today's date, not a constant in the config.
- **Grid.** Once qualifying has run, its result is the default grid, and once
  OpenF1 publishes the starting grid (`starting_grid`, keyed by the qualifying
  session) that order replaces it, so engine and gearbox penalties are applied
  before the race. Over 2025-2026 the qualifying order differed from the real
  starting grid for 173 of 809 cars; OpenF1's starting grid for 25, all of them
  back-of-grid renumbering around pit-lane starters. The ledger writes the
  prediction down again if the starting grid changes after it was recorded.
  Before qualifying,
  the default is an *expected* grid: the current field ordered by each driver's
  median gap to pole over their last three qualifying sessions. Copying the last
  race alone let one freak pole margin decide the next race. Once that weekend's
  practice has run, the order blends those qualifying gaps 50/50 with each
  driver's best practice lap: over 167 races since 2019 that raised the rank
  correlation with the real qualifying order from 0.71 to 0.76. When the official
  feed lags behind a finished qualifying session, the grid comes from OpenF1,
  whose session is found by date; cars without a qualifying time are added at
  the back.
- **Weather.** For the next race, the Open-Meteo forecast for the circuit's
  coordinates and the two hours after the start is mapped onto the weather
  presets and pre-selects the weather dropdown. Beyond the ~15-day forecast
  horizon, the dropdown stays on its default.
- **Sync.** `src/pipeline.py` fetches the latest results, qualifying, pit stops,
  schedule and weather, rebuilds the features, and refits the model (about ten
  seconds) only when a new race has been run. A file lock stops two syncs from
  writing the same files at once. The app runs it by itself every 15 minutes if
  a race has finished without results in the feed, if qualifying has finished
  but its grid is missing, or if the last sync is over 12 hours old (turn this
  off with `F1_AUTO_SYNC=0`). The *Sync live data* button runs the same thing on
  demand.

---

## Honest limits

- **Grid position dominates, and this model does not beat it at picking names.**
  Most of what decides a podium is decided on Saturday. What the model adds is
  calibrated probability, reliability risk, circuit affinity and wet-weather
  handling — not overturning qualifying.
- **The most useful features are not the exotic ones.** Permutation importance
  puts grid position first and "how many cars ahead of you are in quicker
  machinery" second, followed by the championship order and the qualifying gap to
  the best rival. The driver-versus-circuit history matters, but it is a
  modifier, not the story.
- **Before qualifying, the grid is an estimate.** This predicts a race given a
  starting order. Until qualifying has run, that order is the expected grid, and
  the prediction is only as good as that guess, which is why it comes from the
  pre-qualifying heads that lean more on form; after qualifying it is the real
  one, and penalties are in once the official starting grid is published.
- **Pit-lane starts are not known before the race.** The model learned what a
  pit-lane start costs, but no feed the app reads says who will start from the
  pit lane: OpenF1's race control does not carry it, and the FIA announces it in
  documents. Since 2025 Jolpica no longer marks pit-lane starters with grid 0
  either, so the history of that feature thins out. The what-if grid is the way
  to move such a car to the back.
- **Circuit history needs history.** "Likes this track" only exists where the
  current field has raced: Sepang returns in 2026 after eight years away, so
  only a few drivers have any record there, and the model leans on form and car
  pace instead.
- **The championship outlook holds the field still.** Each future race uses
  today's expected grid and today's form; nobody improves, upgrades or gets a
  penalty in the simulated weeks ahead.
- **Weather is only as good as the forecast.** For the next race the selector
  starts on the Open-Meteo forecast, which is reliable a few days out and absent
  beyond about two weeks; it can always be overridden. Historical rain comes from
  a coarse reanalysis that misses some local storms.
- **A debut circuit has no history.** A new venue is in the catalogue with
  geometry and regulation-derived lap count, but its circuit features are empty
  rather than invented. The same goes, mostly, for a circuit returning after
  years away, like Sepang in 2026.
- **Strategy, tyre allocation and in-race incidents are not modelled.** They show
  up only as the variance the model has learned to expect.
