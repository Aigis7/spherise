// むずかしい用のデッキを探す道具。サイトを http サーバーで開いて（localhost:8765）、node src/opt_cpu_deck.js <デッキid> <回数> <1組あたりの試合数> で動かす。結果は同じフォルダの opt_<デッキid>.json に出る。
// むずかしい用のデッキを探す：1枚入れ替えて、ほかのスターターデッキへの勝率が上がったら残す
// 使い方: node opt.js <base> <iters> <N>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const base = process.argv[2], ITERS = +(process.argv[3] || 30), N = +(process.argv[4] || 120);
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('http://localhost:8765/'); await pg.waitForFunction(() => typeof STORE !== 'undefined' && STORE.decks && STORE.decks.shiki);
  const prev = fs.existsSync(__dirname + `/opt_${base}.json`) ? JSON.parse(fs.readFileSync(__dirname + `/opt_${base}.json`)).list : null;
  const res = await pg.evaluate(async ({ base, ITERS, N, prev }) => {
    const opps = ['soiree', 'noctiluca', 'yumemakura', 'shiki', 'hajimari'];
    const bd = STORE.decks[base], col = deckColor(bd);
    const pool = Object.entries(STORE.cards).filter(([id, c]) => !c.token && c.rarity !== 'RR' && !c.needs && (cardColor(c) === col || cardColor(c) === '無')).map(([id]) => id);
    const toList = m => Object.entries(m).filter(([, n]) => n > 0).map(([id, n]) => ({ id, n }));
    async function score(m) {
      STORE.decks._opt = { name: 'opt', field: bd.field, list: toList(m) };
      let w = 0, tot = 0;
      for (const o of opps) for (let i = 0; i < N; i++) {
        const g = newGame({ decks: ['_opt', o], ai: [true, true], sim: true });
        aiMulligan(g, g.players[0]); aiMulligan(g, g.players[1]); await gameLoop(g);
        if (g.winner === 0) w++; else if (g.winner == null) w += 0.5; tot++;
      }
      return w / tot;
    }
    let cur = {}; for (const e of (prev || bd.list)) cur[e.id] = e.n;
    let cs = await score(cur); const start = cs; const log = [`start ${cs.toFixed(3)}`];
    for (let it = 0; it < ITERS; it++) {
      const ins = Object.keys(cur).filter(k => cur[k] > 0);
      const out = ins[Math.floor(Math.random() * ins.length)];
      const cand = pool.filter(id => id !== out && (cur[id] || 0) < 3);
      const add = cand[Math.floor(Math.random() * cand.length)];
      const nx = Object.assign({}, cur); nx[out]--; nx[add] = (nx[add] || 0) + 1;
      const s = await score(nx);
      if (s > cs + 0.012) { const re = await score(nx); const avg = (s + re) / 2; if (avg > cs) { cur = nx; cs = avg; log.push(`${it}: -${C[out].name} +${C[add].name} -> ${cs.toFixed(3)}`); } }
    }
    delete STORE.decks._opt;
    return { start, end: cs, list: toList(cur), log };
  }, { base, ITERS, N, prev });
  fs.writeFileSync(__dirname + `/opt_${base}.json`, JSON.stringify(res, null, 1));
  console.log(base, res.start.toFixed(3), '->', res.end.toFixed(3)); console.log(res.log.join('\n'));
  await b.close();
})();
