"use strict";

STRINGS.es = {
  "html.title": "Race Predictor",
  "model.loading": "cargando el modelo…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · entrenado hasta ${trained}`,
  "model.next": ({ race, date }) => ` · próxima: ${race}, ${date}`,
  "metric.hit": "acierto en el podio",
  "metric.grid": "solo la parrilla",
  "btn.about": "Cómo funciona",
  "btn.theme": "Cambiar tema",
  "btn.lang": "Idioma",

  "track.title": "Circuito y condiciones de carrera",
  "track.season": "Temporada",
  "season.2026": "2026 (simulada)",
  "season.real": ({ year }) => `${year} (disputada)`,
  "track.select": "Circuito",
  "track.calendar": "Calendario de esta temporada",
  "track.other": "Otros circuitos con historial",
  "track.street": " · circuito urbano",
  "track.no_map": "No hay trazado dibujado para este circuito.<br>La predicción no se ve afectada.",
  "track.layout": ({ name }) => `Trazado de ${name}`,
  "ro.difficulty": "Dificultad del circuito",
  "ro.difficulty_note": "densidad de curvas, incidentes, muros",
  "ro.deg": "Desgaste de neumáticos",
  "ro.deg_none": "sin datos recientes",
  "ro.deg_pitstops": ({ window }) => `paradas en boxes ${window}`,
  "ro.deg_layout": "estimado a partir del trazado",
  "ro.distance": "Distancia de carrera",
  "ro.corners": "Curvas",
  "ro.laps": "Vueltas",
  "weather.title": "Meteorología",
  "weather.dry": "Seco",
  "weather.cloudy": "Nublado",
  "weather.light_rain": "Lluvia ligera",
  "weather.mixed": "Mixto / secándose",
  "weather.heavy_rain": "Lluvia intensa",

  "stat.sticky": "Podio desde el top 3 de la parrilla",
  "stat.pole": "La pole se convierte en victoria",
  "stat.dnf": "Tasa de abandonos",
  "stat.gained": "Posiciones ganadas por carrera",
  "stat.stops": "Paradas por coche",
  "stat.sc": "Coche de seguridad o bandera roja",
  "stat.sc_value": ({ pct, n }) => `${pct} de ${n} ${plural(n, ["carrera", "carreras"])}`,
  "stat.deg": "Tiempo perdido por vuelta de neumático",
  "stat.length": "Longitud de la vuelta",
  "stat.measured": "Medido sobre",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["salida reciente", "salidas recientes"])}`,

  "grid.title": "Parrilla de salida",
  "grid.col.grid": "Pos.",
  "grid.col.driver": "Piloto",
  "grid.col.team": "Equipo / coche",
  "grid.col.history": "En este circuito",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["coche", "coches"])}.`,
  "grid.move_up": ({ name }) => `Subir a ${name}`,
  "grid.move_down": ({ name }) => `Bajar a ${name}`,
  "history.none": "sin salidas aquí",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["salida", "salidas"])}`,
  "history.avg": ({ pos }) => `media <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["podio", "podios"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["victoria", "victorias"])}`,
  "driver.career": (c) => `Carrera: ${c.races} salidas, ${c.wins} victorias, ${c.podiums} podios, llegada media P${c.avg}, abandonos ${c.dnf}`,
  "driver.recent": (r) => `Temporadas ${r.seasons}: salida media P${r.grid}, llegada media P${r.finish}, podio en el ${r.rate}`,
  "driver.season": (s) => `Esta temporada: ${s.races} salidas, ${s.points} puntos, ${s.podiums} podios${s.best ? `, mejor P${s.best}` : ""}`,

  "source.race": "Parrilla real",
  "source.race.hint": "Esta carrera ya se disputó. La predicción usa solo lo que se sabía el día anterior, y el resultado real aparece al lado.",
  "source.starting_grid": "Parrilla oficial",
  "source.starting_grid.hint": "La parrilla de salida oficial de OpenF1, con las sanciones aplicadas.",
  "source.qualifying": "Según la clasificación",
  "source.qualifying.hint": "Orden según el resultado oficial de la clasificación. Las sanciones se aplican cuando se publica la parrilla oficial.",
  "source.openf1": "Según la clasificación (OpenF1)",
  "source.openf1.hint": "Orden de la clasificación en OpenF1; la fuente oficial aún no lo tiene.",
  "source.expected_practice": "Parrilla prevista (con libres)",
  "source.expected_practice.hint": "La clasificación aún no se ha disputado: el orden combina las diferencias recientes de cada piloto en clasificación con su mejor vuelta en los libres de este fin de semana. Se actualiza sola tras la clasificación.",
  "source.expected": "Parrilla prevista",
  "source.expected.hint": "La clasificación aún no se ha disputado: el orden sigue la diferencia mediana de cada piloto con la pole en sus tres últimas clasificaciones. Se actualiza sola tras la clasificación.",
  "source.what_if": "Parrilla hipotética",
  "source.what_if.hint": "Has reordenado la parrilla. Las predicciones con una parrilla editada no se guardan en el historial.",

  "btn.sync": "Actualizar datos",
  "btn.syncing": "Actualizando…",
  "sync.done": "¡Datos actualizados correctamente!",
  "sync.failed": ({ msg }) => `Error al actualizar: ${msg}`,
  "btn.reset": "Restaurar parrilla",
  "btn.predict": "Predecir el podio",
  "btn.predicting": "Calculando…",
  "predict.failed": ({ msg }) => `Error en la predicción: ${msg}`,

  "results.title": "Resultado previsto",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · desgaste ${deg}/10`,
  "results.backtest": " · con lo sabido el día anterior",
  "results.prequali": " · modelo previo a la clasificación",
  "order.slot": ({ pct }) => `solo la posición de salida ${pct}`,
  "place.1": "1.º",
  "place.2": "2.º",
  "place.3": "3.º",
  "pod.from": ({ place, grid }) => `${place} · desde P${grid}`,
  "pod.chance": "probabilidad de podio",
  "order.pos": "Pos.",
  "order.driver": "Piloto",
  "order.team": "Equipo",
  "order.prob": "Probabilidad de podio",
  "order.podium": "Podio",
  "order.win": "Victoria",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `sale P${grid} · llegada prevista ${finish}`,
  "order.range": ({ a, b }) => ` · normalmente P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · terminó P${pos}`,
  "order.actual_dnf": " · no terminó",
  "dnf.total": ({ pct }) => `Riesgo de abandono ${pct}`,
  "dnf.crash": ({ pct }) => `  accidente ${pct}`,
  "dnf.mech": ({ pct }) => `  avería ${pct}`,
  "dnf.dsq": ({ pct }) => `  descalificación ${pct}`,

  "note.grid_front": ({ grid }) => `sale P${grid}`,
  "note.grid_deep": ({ grid }) => `muy atrás, en P${grid}`,
  "note.form": ({ pos }) => `forma reciente ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `coche en el podio en el ${pctText(rate)} de las últimas salidas`,
  "note.over_performs": ({ delta }) => `aquí rinde por encima de lo habitual (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `aquí suele rendir peor (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["podio", "podios"])} en este circuito`,
  "note.reliability": ({ rate }) => `riesgo de fiabilidad (${pctText(rate)} de abandonos recientes)`,
  "note.crashed_here": ({ n }) => `abandonó aquí por accidente ${n} ${plural(n, ["vez", "veces"])}`,
  "note.crash_risk": ({ rate }) => `riesgo de accidente elevado aquí (${pctText(rate)})`,

  "btn.share": "Compartir podio",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · DESDE P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · modelo entrenado hasta ${trained}`,
  "share.text": ({ list }) => `Podio previsto: ${list}`,
  "share.saved": ({ name }) => `Guardado ${name}`,

  "champ.title": "Previsión del Mundial",
  "champ.chip": "resto de la temporada",
  "champ.hint": "Disputa miles de veces cada carrera restante con el modelo y suma los puntos.",
  "champ.btn": "Simular el resto de la temporada",
  "champ.running": "Simulando…",
  "champ.retry": "Reintentar",
  "champ.failed": ({ msg }) => `Error en la simulación: ${msg}`,
  "champ.drivers": "Pilotos",
  "champ.teams": "Constructores",
  "champ.left": ({ races, sprints }) => `quedan ${races} ${plural(races, ["carrera", "carreras"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprints"])}` : ""),
  "champ.done": "temporada terminada",
  "champ.summary": ({ sims }) => `${sims} temporadas simuladas desde la clasificación actual. Cada carrera usa la parrilla prevista y las probabilidades del modelo; `,
  "champ.sprints": "los sprints se puntúan con las mismas probabilidades.",
  "champ.no_sprints": "no se pudieron comprobar los fines de semana con sprint, así que se omiten.",
  "champ.final": "No quedan carreras: esta es la clasificación final.",
  "champ.now": "Ahora",
  "champ.driver": "Piloto",
  "champ.team": "Equipo",
  "champ.expected": "Prevista",
  "champ.title_col": "Título",
  "champ.range": ({ a, b }) => `El 80 % de las temporadas simuladas termina entre ${a} y ${b} puntos`,

  "record.title": "Historial",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["carrera evaluada", "carreras evaluadas"])}: ${hit} de los puestos de podio acertados (solo la parrilla: ${grid}), ganador acertado el ${winner} de las veces.`,
  "record.empty": "Aún no hay carreras evaluadas. La app guarda su predicción antes de cada carrera y la evalúa cuando llega el resultado.",
  "record.by_source": "Según lo que se sabía del fin de semana al guardar la predicción:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} de los puestos de podio en ${n} ${plural(n, ["carrera", "carreras"])}`,
  "record.race": "Carrera",
  "record.predicted": "Podio previsto",
  "record.actual": "Real",
  "record.hits": "Aciertos",
  "record.not_run": "aún no disputada",
  "record.winner": " · ganador",

  "about.title": "Cómo se predice el podio",
  "about.close": "Cerrar",
  "about.body": ({ imp }) => `
    <p>Tres clasificadores de gradient boosting puntúan cada coche de la parrilla: para la
    victoria, el podio y los puntos. Cada puntuación se ancla después a lo que históricamente ha
    valido salir desde esa posición, y todo el pelotón pasa por 20 000 carreras simuladas. Cada
    probabilidad que ves sale de esa única simulación, por eso siempre cuadran entre sí y con el
    orden en que aparecen.</p>

    <h3>Por qué la parrilla tiene voto</h3>
    <p>Por sí solo, el modelo cambiaba el orden de la parrilla más o menos una de cada dos
    carreras y acertaba el 43 % de las veces, frente al 57 % que habría logrado dejándolo tal
    cual. Sus desacuerdos eran peor que inútiles. Por eso ahora cada puntuación se mezcla, en
    log-odds, con la tasa real de conversión de esa posición; el modelo sigue moviendo un coche,
    pero solo en proporción a lo mucho que discrepa. El peso de la mezcla se mide en temporadas
    que el modelo nunca vio, no se elige a mano.</p>

    <h3>Qué termina una carrera</h3>
    <p>En cada carrera simulada se sortean por separado la fiabilidad y el accidente. Romperse
    depende del coche; estrellarse depende del piloto, del circuito concreto y sobre todo de la
    zona del pelotón que pelea por posiciones. Por eso Mónaco y Zandvoort dan al mismo piloto
    probabilidades muy distintas de ver la bandera a cuadros.</p>

    <h3>En qué se fija</h3>
    <p>Posición de salida y diferencia en clasificación; la forma reciente del piloto, su
    fiabilidad y su balance frente al compañero de equipo; el ritmo del coche y su tasa de
    podios; el historial del piloto en <em>este</em> circuito; y lo que el propio circuito suele
    hacer con una carrera: cuánto se mezcla el orden, cuántas veces gana la pole, cuántos coches
    abandonan. Las variables con más peso ahora mismo:</p>
    <ul>${imp}</ul>

    <h3>Por qué las carreras antiguas cuentan menos</h3>
    <p>El deporte no se detiene, así que cada fila de entrenamiento pesa
    <code>0,5 ^ (años atrás / 8)</code>. Una carrera de 2005 todavía cuenta, con más o menos el
    16 % del peso de una del mes pasado. La forma reciente se desvanece más rápido, por carrera y
    no por año.</p>

    <h3>Validado temporada a temporada</h3>
    <p>Nunca un reparto aleatorio: el modelo se entrena solo con temporadas anteriores a la que se
    evalúa, así que nada del futuro se cuela. Cada cifra se compara con leer el podio de las tres
    primeras posiciones de la parrilla y la victoria de la pole, algo mucho más difícil de batir
    en la Fórmula 1 moderna de lo que parece: salir entre los tres primeros acaba en podio el 68 %
    de las veces; salir más atrás, solo el 6 %.</p>`,
  "val.season": "Temporada",
  "val.races": "Carreras",
  "val.hit": "Acierto podio",
  "val.grid": "Solo parrilla",
  "val.lift": "Mejora",
  "val.winner": "Ganador",
  "val.pole": "Solo pole",

  "nav.skip": "Saltar al contenido",
  "nav.back": "Volver a las predicciones",
  "footer.tagline": "Predicciones del podio de Fórmula 1 con 30 años de datos de carreras.",
  "footer.nav": "Pie de página",
  "footer.home": "Predicciones",
  "footer.privacy": "Política de privacidad",
  "footer.terms": "Condiciones de uso",
  "footer.data": "Datos:",
  "footer.disclaimer": "Sin relación con la Fórmula 1, la FIA ni ningún equipo. F1 y Formula 1 son marcas de Formula One Licensing B.V.",
  "notfound.title": "Fuera de pista",
  "notfound.text": "Esta página no existe o se ha movido. Pero la carrera sigue.",
  "notfound.home": "Ir a las predicciones",
  "meta.title": "Race Predictor — predicciones del podio de F1 para cada Gran Premio",
  "meta.race": ({ race }) => `${race}: predicción del podio · Race Predictor`,
};
