"use strict";

STRINGS.fr = {
  "html.title": "Race Predictor",
  "model.loading": "chargement du modèle…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · entraîné jusqu'au ${trained}`,
  "model.next": ({ race, date }) => ` · prochaine course : ${race}, ${date}`,
  "metric.hit": "podiums trouvés",
  "metric.grid": "grille seule",
  "btn.about": "Comment ça marche",
  "btn.theme": "Changer de thème",
  "btn.lang": "Langue",

  "track.title": "Circuit et conditions de course",
  "track.season": "Saison",
  "season.2026": "2026 (simulée)",
  "season.real": ({ year }) => `${year} (disputée)`,
  "track.select": "Circuit",
  "track.calendar": "Calendrier de la saison",
  "track.other": "Autres circuits avec historique",
  "track.street": " · circuit urbain",
  "track.no_map": "Pas de tracé dessiné pour ce circuit.<br>La prédiction n'est pas affectée.",
  "track.layout": ({ name }) => `Tracé de ${name}`,
  "ro.difficulty": "Difficulté du circuit",
  "ro.difficulty_note": "densité de virages, incidents, murs",
  "ro.deg": "Usure des pneus",
  "ro.deg_none": "pas de données récentes",
  "ro.deg_pitstops": ({ window }) => `arrêts aux stands ${window}`,
  "ro.deg_layout": "estimée d'après le tracé",
  "ro.distance": "Distance de course",
  "ro.corners": "Virages",
  "ro.laps": "Tours",
  "weather.title": "Météo",
  "weather.dry": "Sec",
  "weather.cloudy": "Nuageux",
  "weather.light_rain": "Pluie légère",
  "weather.mixed": "Mixte / piste qui sèche",
  "weather.heavy_rain": "Forte pluie",

  "stat.sticky": "Podium issu du top 3 de la grille",
  "stat.pole": "La pole se transforme en victoire",
  "stat.dnf": "Taux d'abandon",
  "stat.gained": "Places gagnées par course",
  "stat.stops": "Arrêts par voiture",
  "stat.sc": "Voiture de sécurité ou drapeau rouge",
  "stat.sc_value": ({ pct, n }) => `${pct} sur ${n} ${plural(n, ["course", "courses"])}`,
  "stat.deg": "Temps perdu par tour de pneu",
  "stat.length": "Longueur du tour",
  "stat.measured": "Mesuré sur",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["départ récent", "départs récents"])}`,

  "grid.title": "Grille de départ",
  "grid.col.grid": "Place",
  "grid.col.driver": "Pilote",
  "grid.col.team": "Écurie / voiture",
  "grid.col.history": "Sur ce circuit",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["voiture", "voitures"])}.`,
  "grid.move_up": ({ name }) => `Faire monter ${name}`,
  "grid.move_down": ({ name }) => `Faire descendre ${name}`,
  "history.none": "aucun départ ici",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["départ", "départs"])}`,
  "history.avg": ({ pos }) => `moy. <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podium", "podiums"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["victoire", "victoires"])}`,
  "driver.career": (c) => `Carrière : ${c.races} départs, ${c.wins} victoires, ${c.podiums} podiums, arrivée moyenne P${c.avg}, abandons ${c.dnf}`,
  "driver.recent": (r) => `Saisons ${r.seasons} : départ moyen P${r.grid}, arrivée moyenne P${r.finish}, podium dans ${r.rate} des courses`,
  "driver.season": (s) => `Cette saison : ${s.races} départs, ${s.points} points, ${s.podiums} podiums${s.best ? `, meilleur résultat P${s.best}` : ""}`,

  "source.race": "Grille réelle",
  "source.race.hint": "Cette course a déjà eu lieu. La prédiction n'utilise que ce qu'on savait la veille, et le vrai résultat est affiché à côté.",
  "source.starting_grid": "Grille officielle",
  "source.starting_grid.hint": "La grille de départ officielle d'OpenF1, pénalités comprises.",
  "source.qualifying": "D'après les qualifications",
  "source.qualifying.hint": "Ordre du résultat officiel des qualifications. Les pénalités sont appliquées dès que la grille officielle est publiée.",
  "source.openf1": "D'après les qualifications (OpenF1)",
  "source.openf1.hint": "Ordre des qualifications sur OpenF1 ; la source officielle ne l'a pas encore.",
  "source.expected_practice": "Grille attendue (avec essais libres)",
  "source.expected_practice.hint": "Les qualifications n'ont pas encore eu lieu : l'ordre combine les écarts récents de chaque pilote en qualifications et son meilleur tour aux essais libres de ce week-end. Il se met à jour tout seul après les qualifications.",
  "source.expected": "Grille attendue",
  "source.expected.hint": "Les qualifications n'ont pas encore eu lieu : le plateau est classé par l'écart médian de chaque pilote sur la pole lors de ses trois dernières qualifications. Il se met à jour tout seul après les qualifications.",
  "source.what_if": "Grille hypothétique",
  "source.what_if.hint": "Vous avez réorganisé la grille. Les prédictions faites sur une grille modifiée ne sont pas enregistrées dans le bilan.",

  "btn.sync": "Mettre à jour les données",
  "btn.syncing": "Mise à jour…",
  "sync.done": "Données mises à jour !",
  "sync.failed": ({ msg }) => `Échec de la mise à jour : ${msg}`,
  "btn.reset": "Rétablir la grille",
  "btn.predict": "Prédire le podium",
  "btn.predicting": "Calcul en cours…",
  "predict.failed": ({ msg }) => `Échec de la prédiction : ${msg}`,

  "results.title": "Résultat prévu",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · usure ${deg}/10`,
  "results.backtest": " · état de la veille",
  "results.prequali": " · modèle avant les qualifications",
  "order.slot": ({ pct }) => `place sur la grille seule ${pct}`,
  "place.1": "1er",
  "place.2": "2e",
  "place.3": "3e",
  "pod.from": ({ place, grid }) => `${place} · depuis P${grid}`,
  "pod.chance": "chance de podium",
  "order.pos": "Pos.",
  "order.driver": "Pilote",
  "order.team": "Écurie",
  "order.prob": "Probabilité de podium",
  "order.podium": "Podium",
  "order.win": "Victoire",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `part P${grid} · arrivée attendue ${finish}`,
  "order.range": ({ a, b }) => ` · en général P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · a fini P${pos}`,
  "order.actual_dnf": " · a abandonné",
  "dnf.total": ({ pct }) => `Risque d'abandon ${pct}`,
  "dnf.crash": ({ pct }) => `  accident ${pct}`,
  "dnf.mech": ({ pct }) => `  panne ${pct}`,
  "dnf.dsq": ({ pct }) => `  disqualification ${pct}`,

  "note.grid_front": ({ grid }) => `part P${grid}`,
  "note.grid_deep": ({ grid }) => `loin dans le peloton, P${grid}`,
  "note.form": ({ pos }) => `forme récente ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `voiture sur le podium dans ${pctText(rate)} des derniers départs`,
  "note.over_performs": ({ delta }) => `meilleur ici que d'habitude (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `souvent moins bon ici (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podium", "podiums"])} sur ce circuit`,
  "note.reliability": ({ rate }) => `risque de fiabilité (${pctText(rate)} d'abandons récents)`,
  "note.crashed_here": ({ n }) => `a abandonné ici sur accident ${n} ${plural(n, ["fois", "fois"])}`,
  "note.crash_risk": ({ rate }) => `risque d'accident élevé ici (${pctText(rate)})`,

  "btn.share": "Partager le podium",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · DEPUIS P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · modèle entraîné jusqu'au ${trained}`,
  "share.text": ({ list }) => `Podium prévu : ${list}`,
  "share.saved": ({ name }) => `${name} enregistré`,

  "champ.title": "Prévision du championnat",
  "champ.chip": "reste de la saison",
  "champ.hint": "Fait courir chaque course restante des milliers de fois avec le modèle et additionne les points.",
  "champ.btn": "Simuler le reste de la saison",
  "champ.running": "Simulation…",
  "champ.retry": "Réessayer",
  "champ.failed": ({ msg }) => `Échec de la simulation : ${msg}`,
  "champ.drivers": "Pilotes",
  "champ.teams": "Constructeurs",
  "champ.left": ({ races, sprints }) => `encore ${races} ${plural(races, ["course", "courses"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprints"])}` : ""),
  "champ.done": "saison terminée",
  "champ.summary": ({ sims }) => `${sims} saisons simulées à partir du classement actuel. Chaque course utilise la grille attendue et les probabilités du modèle ; `,
  "champ.sprints": "les sprints sont comptés avec les mêmes probabilités.",
  "champ.no_sprints": "les week-ends sprint n'ont pas pu être vérifiés, les sprints sont donc ignorés.",
  "champ.final": "Plus aucune course : voici le classement final.",
  "champ.now": "Actuel",
  "champ.driver": "Pilote",
  "champ.team": "Écurie",
  "champ.expected": "Attendu",
  "champ.title_col": "Titre",
  "champ.range": ({ a, b }) => `80 % des saisons simulées finissent entre ${a} et ${b} points`,

  "record.title": "Bilan",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["course évaluée", "courses évaluées"])} : ${hit} des places de podium trouvées (grille seule : ${grid}), vainqueur trouvé dans ${winner} des cas.`,
  "record.empty": "Aucune course évaluée pour l'instant. L'appli enregistre sa prédiction avant chaque course et l'évalue dès que le résultat est connu.",
  "record.by_source": "Selon ce qu'on savait du week-end au moment d'enregistrer la prédiction :",
  "record.source_line": ({ label, hit, n }) => `${label} : ${hit} des places de podium sur ${n} ${plural(n, ["course", "courses"])}`,
  "record.race": "Course",
  "record.predicted": "Podium prévu",
  "record.actual": "Réel",
  "record.hits": "Trouvés",
  "record.not_run": "pas encore disputée",
  "record.winner": " · vainqueur",

  "about.title": "Comment le podium est prédit",
  "about.close": "Fermer",
  "about.body": ({ imp }) => `
    <p>Trois classifieurs de gradient boosting notent chaque voiture de la grille : pour la
    victoire, le podium et les points. Chaque note est ensuite ancrée sur ce que valait
    historiquement un départ depuis cette place, puis tout le plateau passe par 20 000 courses
    simulées. Chaque probabilité affichée provient de cette seule simulation ; c'est pourquoi elles
    concordent toujours entre elles et avec l'ordre d'affichage.</p>

    <h3>Pourquoi la grille a son mot à dire</h3>
    <p>Livré à lui-même, le modèle modifiait l'ordre de la grille environ une course sur deux et
    avait raison dans 43 % des cas, contre 57 % s'il avait laissé l'ordre tel quel. Ses désaccords
    étaient pires qu'inutiles. Chaque note est donc désormais mélangée, en log-odds, avec le taux
    de réussite réel de cette place ; le modèle déplace encore une voiture, mais seulement en
    proportion de son désaccord. Le poids du mélange est mesuré sur des saisons que le modèle n'a
    jamais vues, pas choisi à la main.</p>

    <h3>Ce qui met fin à une course</h3>
    <p>Chaque course simulée tire séparément la fiabilité et l'accident. La casse dépend de la
    voiture ; l'accident dépend du pilote, du circuit et surtout de la partie du peloton qui se
    bat pour les positions. C'est pourquoi Monaco et Zandvoort donnent au même pilote des chances
    très différentes de voir le drapeau à damier.</p>

    <h3>Ce qu'il regarde</h3>
    <p>La place sur la grille et l'écart en qualifications ; la forme récente du pilote, sa
    fiabilité et son bilan face à son coéquipier ; le rythme de la voiture et son taux de
    podiums ; l'historique du pilote sur <em>ce</em> circuit ; et ce que le circuit fait
    d'habitude à une course : à quel point l'ordre se mélange, combien de fois la pole gagne,
    combien de voitures abandonnent. Les variables les plus lourdes en ce moment :</p>
    <ul>${imp}</ul>

    <h3>Pourquoi les vieilles courses comptent moins</h3>
    <p>Le sport ne reste pas immobile : chaque ligne d'entraînement pèse
    <code>0,5 ^ (années écoulées / 8)</code>. Une course de 2005 compte encore, avec environ 16 %
    du poids d'une course du mois dernier. La forme récente s'estompe plus vite, course après
    course plutôt qu'année après année.</p>

    <h3>Validé saison par saison</h3>
    <p>Jamais de découpage aléatoire : le modèle n'apprend que sur les saisons antérieures à
    celle où il est évalué, rien du futur ne fuit. Chaque chiffre est comparé au fait de lire le
    podium sur les trois premières places de la grille et la victoire sur la pole, une barre bien
    plus haute qu'il n'y paraît en Formule 1 moderne : un départ dans le top 3 se transforme en
    podium dans 68 % des cas, un départ derrière dans seulement 6 %.</p>`,
  "val.season": "Saison",
  "val.races": "Courses",
  "val.hit": "Podiums trouvés",
  "val.grid": "Grille seule",
  "val.lift": "Gain",
  "val.winner": "Vainqueur",
  "val.pole": "Pole seule",

  "nav.skip": "Aller au contenu",
  "nav.back": "Retour aux pronostics",
  "footer.tagline": "Pronostics du podium de Formule 1 à partir de 30 ans de données de course.",
  "footer.nav": "Pied de page",
  "footer.home": "Pronostics",
  "footer.privacy": "Politique de confidentialité",
  "footer.terms": "Conditions d'utilisation",
  "footer.data": "Données :",
  "footer.disclaimer": "Sans lien avec la Formule 1, la FIA ou une écurie. F1 et Formula 1 sont des marques de Formula One Licensing B.V.",
  "notfound.title": "Sortie de piste",
  "notfound.text": "Cette page n'existe pas ou a été déplacée. Mais la course continue.",
  "notfound.home": "Voir les pronostics",
  "meta.title": "Race Predictor — pronostics du podium F1 pour chaque Grand Prix",
  "meta.race": ({ race }) => `${race} : pronostic du podium · Race Predictor`,
};
