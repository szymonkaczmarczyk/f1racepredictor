"use strict";

STRINGS.pt = {
  "html.title": "Race Predictor",
  "model.loading": "carregando o modelo…",
  "model.badge": ({ from, to, trained }) => `${from}–${to} · treinado até ${trained}`,
  "model.next": ({ race, date }) => ` · próxima: ${race}, ${date}`,
  "metric.hit": "acerto no pódio",
  "metric.grid": "só o grid",
  "btn.about": "Como funciona",
  "btn.theme": "Mudar tema",
  "btn.lang": "Idioma",

  "track.title": "Circuito e condições da corrida",
  "track.season": "Temporada",
  "season.2026": "2026 (simulada)",
  "season.real": ({ year }) => `${year} (disputada)`,
  "track.select": "Circuito",
  "track.calendar": "Calendário desta temporada",
  "track.other": "Outros circuitos com histórico",
  "track.street": " · circuito de rua",
  "track.no_map": "Não há traçado desenhado para este circuito.<br>A previsão não é afetada.",
  "track.layout": ({ name }) => `Traçado de ${name}`,
  "ro.difficulty": "Dificuldade do circuito",
  "ro.difficulty_note": "densidade de curvas, incidentes, muros",
  "ro.deg": "Desgaste dos pneus",
  "ro.deg_none": "sem dados recentes",
  "ro.deg_pitstops": ({ window }) => `pit stops ${window}`,
  "ro.deg_layout": "estimado pelo traçado",
  "ro.distance": "Distância da corrida",
  "ro.corners": "Curvas",
  "ro.laps": "Voltas",
  "weather.title": "Clima",
  "weather.dry": "Seco",
  "weather.cloudy": "Nublado",
  "weather.light_rain": "Chuva fraca",
  "weather.mixed": "Misto / pista secando",
  "weather.heavy_rain": "Chuva forte",

  "stat.sticky": "Pódio saindo do top 3 do grid",
  "stat.pole": "A pole vira vitória",
  "stat.dnf": "Taxa de abandonos",
  "stat.gained": "Posições ganhas por corrida",
  "stat.stops": "Pit stops por carro",
  "stat.sc": "Safety car ou bandeira vermelha",
  "stat.sc_value": ({ pct, n }) => `${pct} de ${n} ${plural(n, ["corrida", "corridas"])}`,
  "stat.deg": "Tempo perdido por volta de pneu",
  "stat.length": "Extensão da volta",
  "stat.measured": "Medido em",
  "stat.starts": ({ n }) => `${n} ${plural(n, ["largada recente", "largadas recentes"])}`,

  "grid.title": "Grid de largada",
  "grid.col.grid": "Pos.",
  "grid.col.driver": "Piloto",
  "grid.col.team": "Equipe / carro",
  "grid.col.history": "Neste circuito",
  "grid.cars": ({ n }) => `${n} ${plural(n, ["carro", "carros"])}.`,
  "grid.move_up": ({ name }) => `Subir ${name}`,
  "grid.move_down": ({ name }) => `Descer ${name}`,
  "history.none": "nenhuma largada aqui",
  "history.starts": ({ n }) => `<b>${n}</b> ${plural(n, ["largada", "largadas"])}`,
  "history.avg": ({ pos }) => `média <b>P${pos}</b>`,
  "history.podiums": ({ n }) => `<b>${n}</b> ${plural(n, ["pódio", "pódios"])}`,
  "history.wins": ({ n }) => `<b>${n}</b> ${plural(n, ["vitória", "vitórias"])}`,
  "driver.career": (c) => `Carreira: ${c.races} largadas, ${c.wins} vitórias, ${c.podiums} pódios, chegada média P${c.avg}, abandonos ${c.dnf}`,
  "driver.recent": (r) => `Temporadas ${r.seasons}: largada média P${r.grid}, chegada média P${r.finish}, pódio em ${r.rate} das corridas`,
  "driver.season": (s) => `Nesta temporada: ${s.races} largadas, ${s.points} pontos, ${s.podiums} pódios${s.best ? `, melhor P${s.best}` : ""}`,

  "source.race": "Grid real",
  "source.race.hint": "Esta corrida já aconteceu. A previsão usa só o que se sabia na véspera, e o resultado real aparece ao lado.",
  "source.starting_grid": "Grid oficial",
  "source.starting_grid.hint": "O grid de largada oficial da OpenF1, com as punições aplicadas.",
  "source.qualifying": "Pela classificação",
  "source.qualifying.hint": "Ordem do resultado oficial da classificação. As punições entram quando o grid oficial é publicado.",
  "source.openf1": "Pela classificação (OpenF1)",
  "source.openf1.hint": "Ordem da classificação na OpenF1; a fonte oficial ainda não a publicou.",
  "source.expected_practice": "Grid previsto (com treinos livres)",
  "source.expected_practice.hint": "A classificação ainda não aconteceu: a ordem combina a diferença recente de cada piloto nas classificações com a melhor volta dele nos treinos livres deste fim de semana. Ela se atualiza sozinha depois da classificação.",
  "source.expected": "Grid previsto",
  "source.expected.hint": "A classificação ainda não aconteceu: o grid segue a diferença mediana de cada piloto para a pole nas três últimas classificações. Ele se atualiza sozinho depois da classificação.",
  "source.what_if": "Grid hipotético",
  "source.what_if.hint": "Você reorganizou o grid. Previsões com um grid editado não entram no histórico.",

  "btn.sync": "Atualizar dados",
  "btn.syncing": "Atualizando…",
  "sync.done": "Dados atualizados com sucesso!",
  "sync.failed": ({ msg }) => `Falha ao atualizar: ${msg}`,
  "btn.reset": "Restaurar grid",
  "btn.predict": "Prever o pódio",
  "btn.predicting": "Calculando…",
  "predict.failed": ({ msg }) => `Falha na previsão: ${msg}`,

  "results.title": "Resultado previsto",
  "results.chip": ({ track, weather, deg }) => `${track} · ${weather} · desgaste ${deg}/10`,
  "results.backtest": " · com o que se sabia na véspera",
  "results.prequali": " · modelo pré-classificação",
  "order.slot": ({ pct }) => `só a posição no grid ${pct}`,
  "place.1": "1º",
  "place.2": "2º",
  "place.3": "3º",
  "pod.from": ({ place, grid }) => `${place} · largando em P${grid}`,
  "pod.chance": "chance de pódio",
  "order.pos": "Pos.",
  "order.driver": "Piloto",
  "order.team": "Equipe",
  "order.prob": "Probabilidade de pódio",
  "order.podium": "Pódio",
  "order.win": "Vitória",
  "order.dnf": "DNF",
  "order.line": ({ grid, finish }) => `larga P${grid} · chegada prevista ${finish}`,
  "order.range": ({ a, b }) => ` · geralmente P${a}–P${b}`,
  "order.actual": ({ pos }) => ` · terminou P${pos}`,
  "order.actual_dnf": " · abandonou",
  "dnf.total": ({ pct }) => `Risco de abandono ${pct}`,
  "dnf.crash": ({ pct }) => `  acidente ${pct}`,
  "dnf.mech": ({ pct }) => `  quebra ${pct}`,
  "dnf.dsq": ({ pct }) => `  desclassificação ${pct}`,

  "note.grid_front": ({ grid }) => `larga em P${grid}`,
  "note.grid_deep": ({ grid }) => `bem atrás, em P${grid}`,
  "note.form": ({ pos }) => `fase recente ~P${pos.toFixed(1)}`,
  "note.team_podium": ({ rate }) => `carro no pódio em ${pctText(rate)} das últimas largadas`,
  "note.over_performs": ({ delta }) => `aqui rende acima do normal (${signedNum(delta)})`,
  "note.weaker_here": ({ delta }) => `aqui costuma render menos (${signedNum(delta)})`,
  "note.podiums_here": ({ n }) => `${n} ${plural(n, ["pódio", "pódios"])} neste circuito`,
  "note.reliability": ({ rate }) => `risco de confiabilidade (${pctText(rate)} de abandonos recentes)`,
  "note.crashed_here": ({ n }) => `abandonou aqui por acidente ${n} ${plural(n, ["vez", "vezes"])}`,
  "note.crash_risk": ({ rate }) => `risco de acidente elevado aqui (${pctText(rate)})`,

  "btn.share": "Compartilhar pódio",
  "share.from": ({ place, grid }) => `${place.toUpperCase()} · LARGANDO EM P${grid}`,
  "share.footer": ({ trained }) => `Race Predictor · modelo treinado até ${trained}`,
  "share.text": ({ list }) => `Pódio previsto: ${list}`,
  "share.saved": ({ name }) => `${name} salvo`,

  "champ.title": "Previsão do campeonato",
  "champ.chip": "resto da temporada",
  "champ.hint": "Roda cada corrida restante milhares de vezes com o modelo e soma os pontos.",
  "champ.btn": "Simular o resto da temporada",
  "champ.running": "Simulando…",
  "champ.retry": "Tentar de novo",
  "champ.failed": ({ msg }) => `Falha na simulação: ${msg}`,
  "champ.drivers": "Pilotos",
  "champ.teams": "Construtores",
  "champ.left": ({ races, sprints }) => `${plural(races, ["falta", "faltam"])} ${races} ${plural(races, ["corrida", "corridas"])}` +
    (sprints ? ` + ${sprints} ${plural(sprints, ["sprint", "sprints"])}` : ""),
  "champ.done": "temporada encerrada",
  "champ.summary": ({ sims }) => `${sims} temporadas simuladas a partir da classificação atual. Cada corrida usa o grid previsto e as probabilidades do modelo; `,
  "champ.sprints": "as sprints são pontuadas com as mesmas probabilidades.",
  "champ.no_sprints": "não foi possível verificar os fins de semana com sprint, então as sprints ficam de fora.",
  "champ.final": "Não há mais corridas: esta é a classificação final.",
  "champ.now": "Agora",
  "champ.driver": "Piloto",
  "champ.team": "Equipe",
  "champ.expected": "Previsto",
  "champ.title_col": "Título",
  "champ.range": ({ a, b }) => `80% das temporadas simuladas terminam entre ${a} e ${b} pontos`,

  "record.title": "Histórico",
  "record.headline": ({ n, hit, grid, winner }) => `${n} ${plural(n, ["corrida avaliada", "corridas avaliadas"])}: ${hit} das posições de pódio acertadas (só o grid: ${grid}), vencedor acertado em ${winner} das vezes.`,
  "record.empty": "Nenhuma corrida avaliada ainda. O app registra a previsão antes de cada corrida e a avalia quando sai o resultado.",
  "record.by_source": "Conforme o quanto do fim de semana se sabia quando a previsão foi registrada:",
  "record.source_line": ({ label, hit, n }) => `${label}: ${hit} das posições de pódio em ${n} ${plural(n, ["corrida", "corridas"])}`,
  "record.race": "Corrida",
  "record.predicted": "Pódio previsto",
  "record.actual": "Real",
  "record.hits": "Acertos",
  "record.not_run": "ainda não disputada",
  "record.winner": " · vencedor",

  "about.title": "Como o pódio é previsto",
  "about.close": "Fechar",
  "about.body": ({ imp }) => `
    <p>Três classificadores de gradient boosting avaliam cada carro do grid: para a vitória, o
    pódio e a zona de pontos. Cada nota é depois ancorada no quanto historicamente valeu largar
    daquela posição, e o grid inteiro passa por 20.000 corridas simuladas. Cada probabilidade
    mostrada sai dessa única simulação; por isso elas sempre batem entre si e com a ordem em que
    aparecem.</p>

    <h3>Por que o grid tem voto</h3>
    <p>Sozinho, o modelo mudava a ordem do grid mais ou menos uma corrida sim, outra não, e
    acertava em 43% dos casos, contra os 57% que teria conseguido deixando a ordem como estava.
    Suas discordâncias eram piores que inúteis. Por isso cada nota agora é misturada, em
    log-odds, com a taxa real de conversão daquela posição; o modelo ainda move um carro, mas
    só na proporção do quanto discorda. O peso da mistura é medido em temporadas que o modelo
    nunca viu, e não escolhido à mão.</p>

    <h3>O que termina uma corrida</h3>
    <p>Em cada corrida simulada, a confiabilidade e o acidente são sorteados separadamente.
    Quebrar depende do carro; bater depende do piloto, do circuito e principalmente da parte do
    pelotão que briga por posição. Por isso Mônaco e Zandvoort dão ao mesmo piloto chances
    muito diferentes de ver a bandeira quadriculada.</p>

    <h3>O que ele observa</h3>
    <p>Posição no grid e diferença na classificação; a fase recente do piloto, a confiabilidade
    e o retrospecto contra o companheiro de equipe; o ritmo do carro e a frequência de pódios;
    o histórico do piloto <em>neste</em> circuito; e o que o próprio circuito costuma fazer com
    uma corrida: o quanto a ordem embaralha, quantas vezes a pole vence, quantos carros
    abandonam. As variáveis de maior peso no momento:</p>
    <ul>${imp}</ul>

    <h3>Por que corridas antigas contam menos</h3>
    <p>O esporte não para, então cada linha de treino pesa
    <code>0,5 ^ (anos atrás / 8)</code>. Uma corrida de 2005 ainda conta, com cerca de 16% do peso
    de uma corrida do mês passado. A fase recente se apaga mais rápido, corrida a corrida e não
    ano a ano.</p>

    <h3>Validado temporada por temporada</h3>
    <p>Nunca uma divisão aleatória: o modelo aprende só com temporadas anteriores àquela em que é
    avaliado, então nada do futuro vaza. Cada número é comparado com ler o pódio nas três
    primeiras posições do grid e a vitória na pole, uma régua muito mais alta do que parece na
    Fórmula 1 moderna: largar entre os três primeiros vira pódio em 68% das vezes; largar mais
    atrás, só em 6%.</p>`,
  "val.season": "Temporada",
  "val.races": "Corridas",
  "val.hit": "Acerto no pódio",
  "val.grid": "Só o grid",
  "val.lift": "Ganho",
  "val.winner": "Vencedor",
  "val.pole": "Só a pole",

  "nav.skip": "Pular para o conteúdo",
  "nav.back": "Voltar às previsões",
  "footer.tagline": "Previsões de pódio da Fórmula 1 com 30 anos de dados de corridas.",
  "footer.nav": "Rodapé",
  "footer.home": "Previsões",
  "footer.privacy": "Política de privacidade",
  "footer.terms": "Termos de uso",
  "footer.data": "Dados:",
  "footer.disclaimer": "Sem vínculo com a Fórmula 1, a FIA ou qualquer equipe. F1 e Formula 1 são marcas da Formula One Licensing B.V.",
  "notfound.title": "Fora da pista",
  "notfound.text": "Esta página não existe ou foi movida. Mas a corrida continua.",
  "notfound.home": "Ir para as previsões",
  "meta.title": "Race Predictor — previsões de pódio da F1 para cada Grande Prêmio",
  "meta.race": ({ race }) => `${race}: previsão do pódio · Race Predictor`,
};
