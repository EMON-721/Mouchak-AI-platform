// Execute the actual pure TypeScript presentation helpers with owned fixture data.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import ts from "typescript";
const defaults = JSON.parse(
  readFileSync(
    new URL("../packages/ui-tokens/site-defaults.json", import.meta.url),
    "utf8",
  ),
);
const source = readFileSync(
  new URL("../components/mouchak/site-config.ts", import.meta.url),
  "utf8",
).replace(
  /import defaults from [^;]+;/,
  `const defaults=${JSON.stringify(defaults)};`,
);
const { outputText } = ts.transpileModule(source, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.CommonJS,
  },
});
const box = { exports: {} };
runInNewContext(outputText, box);
const { customizeTool, siteTokenCSS } = box.exports;
const baseline = {
  name: "DEMO original pond",
  logo: "/logos/demo.svg",
  description_bn: "ডেমো বিবরণ",
  description_en: "DEMO original description",
  fields: [
    { key: "text", bn: "ডেমো তথ্য", en: "DEMO input", type: "textarea" },
    {
      key: "rows",
      bn: "ডেমো সারি",
      en: "DEMO rows",
      type: "table",
      columns: [
        { key: "units", bn: "ডেমো একক", en: "DEMO units", type: "number" },
      ],
    },
  ],
};
const published = {
  slug: "pukursos-ai",
  engine: "observation",
  model_ready: false,
  release_status: "limited_support",
  full_module_complete: false,
  ...baseline,
  name: "DEMO old published name",
  logo: "/api/public/site-assets/" + "a".repeat(64) + ".svg",
  presentation_base: structuredClone(baseline),
};
// Removing a previously published override must show original copy in a draft.
const originalJSON = JSON.stringify(published);
const restored = customizeTool(published, structuredClone(defaults), "en");
assert.equal(restored.name, baseline.name);
assert.equal(restored.logo, baseline.logo);
const preview = structuredClone(defaults);
preview.tool_overrides["pukursos-ai"] = {
  name: { bn: "ডেমো নতুন পুকুর", en: "DEMO new pond" },
  fields: {
    text: {
      bn: "ডেমো নতুন ঘর",
      en: "DEMO new input",
      help_en: "Check your measurement",
    },
    "rows.units": {
      bn: "ডেমো পরিবর্তিত একক",
      en: "DEMO changed units",
      help_en: "Use a measured unit",
      placeholder_bn: "ডেমো মান",
    },
  },
};
const shown = customizeTool(published, preview, "bn");
assert.equal(shown.name, "ডেমো নতুন পুকুর");
assert.equal(shown.fields[0].bn, "ডেমো নতুন ঘর");
assert.equal(shown.fields[1].columns[0].help_en, "Use a measured unit");
assert.equal(shown.fields[1].columns[0].placeholder_bn, "ডেমো মান");
assert.equal(shown.fields[1].columns[0].type, "number");
assert.equal(shown.engine, published.engine);
assert.equal(shown.model_ready, false);
assert.equal(shown.fields[0].type, "textarea");
assert.equal(JSON.stringify(published), originalJSON);
const css = siteTokenCSS(preview);
assert.ok(css.includes(':root[data-theme="dark"]'));
assert.ok(css.includes(':root[data-large="true"]'));
const invalid = structuredClone(defaults);
invalid.theme.light.ink = "red; background:url(https://example.test/pixel)";
invalid.theme.text_scale = Infinity;
assert.ok(!siteTokenCSS(invalid).includes("example.test"));
assert.ok(!siteTokenCSS(invalid).includes("Infinity"));
console.log(
  "Actual presentation helpers: draft removal, bilingual field overrides, immutable operational gates, safe theme and larger-text rules passed.",
);
