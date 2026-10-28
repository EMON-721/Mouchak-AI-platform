// Pure source-engine comparisons, not browser automation. No stored accounts/data.
import vm from "node:vm";
import { readFileSync } from "node:fs";
const root = "reference/legacy-snapshots/";
function engine(files) {
  const c = vm.createContext({ window: {}, module: { exports: {} }, Intl });
  for (const f of files)
    vm.runInContext(readFileSync(root + f, "utf8"), c, { filename: f });
  return c.module.exports;
}
const read = engine(["banglaread/content.js", "banglaread/engine.js"]);
const market = engine(["bazarcompare/engine.js"]);
const shop = engine(["dokanlens/v3-core.js"]);
const reading = read.passages.flatMap((p) =>
  ["", p.answer, "অন্য উত্তর"].map((answer) => ({
    input: {
      passage_id: "legacy:" + p.id,
      difficult_indices: [0, 0, 2],
      answer,
    },
    expected: read.evaluate(p, [0, 0, 2], answer),
  })),
);
const now = "2026-10-27T08:00:00+06:00";
const basket = [
  {
    product: "চাল",
    quantity: 2,
    unit: "kg",
    grade: "standard",
    origin: "local",
    priceType: "retail",
  },
];
const base = {
  product: "চাল",
  quantity: 500,
  unit: "g",
  price: 45.1,
  date: "2026-10-27",
  vendor: "own",
  market: "own",
  grade: "standard",
  origin: "local",
  priceType: "retail",
};
const baskets = [
  [],
  [base],
  [
    base,
    { ...base, price: 1, date: "2026-10-20" },
    { ...base, price: 1, priceType: "wholesale" },
    { ...base, price: 1, grade: "other" },
    { ...base, price: 1, flagged: true },
  ],
].map((offers) => ({
  input: { basket, offers, freshness_days: 7 },
  now,
  expected: market.compare(basket, offers, 7, Date.parse(now)),
}));
let products = [{ id: "golden-stock", stock: 10, revision: 0 }];
const movements = [];
for (const [type, quantity] of [
  ["sale", 2],
  ["purchase", 5],
  ["return", 1],
  ["damage", 3],
  ["supplier_return", 2],
]) {
  products = shop.applyMovement(products, "golden-stock", type, quantity);
  movements.push({ type, quantity, expected: products[0] });
}
process.stdout.write(JSON.stringify({ reading, baskets, movements }));
