const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SOURCE_FILE = path.join(ROOT, 'design', 'figma-variables.json');
const TOKENS_JSON_FILE = path.join(ROOT, 'tokens.json');
const TOKENS_CSS_FILE = path.join(ROOT, 'src', 'styles', 'tokens.css');

function flattenValues(node, prefix, out) {
  if (node && typeof node === 'object' && '$value' in node) {
    out[prefix] = node['$value'];
  }
  for (const [key, value] of Object.entries(node)) {
    if (key === '$type' || key === '$value') continue;
    if (value && typeof value === 'object') {
      flattenValues(value, prefix ? `${prefix}.${key}` : key, out);
    }
  }
  return out;
}

function resolveRef(value, lookup) {
  if (typeof value !== 'string') return value;
  const match = value.match(/^\{(.+)\}$/);
  if (!match) return value;
  const refPath = match[1];
  if (!(refPath in lookup)) {
    throw new Error(`Unresolved token reference: {${refPath}}`);
  }
  return lookup[refPath];
}

function resolveNode(node, lookup) {
  const out = {};
  for (const [key, value] of Object.entries(node)) {
    if (key === '$type') {
      out[key] = value;
    } else if (key === '$value') {
      out[key] = resolveRef(value, lookup);
    } else if (value && typeof value === 'object') {
      out[key] = resolveNode(value, lookup);
    } else {
      out[key] = value;
    }
  }
  return out;
}

function cssVarName(flatKey) {
  return `--${flatKey.split('.').slice(1).join('-')}`;
}

function cssBlock(flatMap) {
  return Object.entries(flatMap)
    .map(([key, value]) => `  ${cssVarName(key)}: ${value};`)
    .join('\n');
}

function main() {
  const raw = JSON.parse(fs.readFileSync(SOURCE_FILE, 'utf8'));
  const data = raw[0];

  const primitivesRaw = data['VooDoo · Primitives']['Value']['primitives'];
  const primitivesFlat = flattenValues(primitivesRaw, 'primitives', {});

  const themes = {};
  const themesFlat = {};
  const componentFlat = {};

  for (const [figmaMode, themeKey] of [['Light', 'light'], ['Dark', 'dark']]) {
    const semanticRaw = data['VooDoo · Theme'][figmaMode]['semantic'];
    const semanticResolved = resolveNode(semanticRaw, primitivesFlat);
    const semanticFlat = flattenValues(semanticResolved, 'semantic', {});

    const combinedFlat = { ...primitivesFlat, ...semanticFlat };

    const componentRaw = data['VooDoo · Components']['Default']['component'];
    const componentResolved = resolveNode(componentRaw, combinedFlat);
    const componentFlatForTheme = flattenValues(componentResolved, 'component', {});

    themes[themeKey] = semanticResolved;
    themesFlat[themeKey] = semanticFlat;
    componentFlat[themeKey] = { resolved: componentResolved, flat: componentFlatForTheme };
  }

  const tokensJson = {
    primitives: primitivesRaw,
    theme: {
      light: themes.light,
      dark: themes.dark,
    },
    component: {
      light: componentFlat.light.resolved,
      dark: componentFlat.dark.resolved,
    },
  };

  fs.mkdirSync(path.dirname(TOKENS_JSON_FILE), { recursive: true });
  fs.writeFileSync(TOKENS_JSON_FILE, JSON.stringify(tokensJson, null, 2) + '\n');

  const css = `/* Auto-generated from design/figma-variables.json by scripts/build-tokens.js. Do not edit by hand. */

:root {
  /* primitives */
${cssBlock(primitivesFlat)}

  /* semantic (light, default) */
${cssBlock(themesFlat.light)}

  /* component (light, default) */
${cssBlock(componentFlat.light.flat)}
}

[data-theme='light'] {
  /* semantic (light, explicit) */
${cssBlock(themesFlat.light)}

  /* component (light, explicit) */
${cssBlock(componentFlat.light.flat)}
}

[data-theme='dark'] {
  /* semantic (dark) */
${cssBlock(themesFlat.dark)}

  /* component (dark) */
${cssBlock(componentFlat.dark.flat)}
}
`;

  fs.mkdirSync(path.dirname(TOKENS_CSS_FILE), { recursive: true });
  fs.writeFileSync(TOKENS_CSS_FILE, css);

  console.log(`Wrote ${path.relative(ROOT, TOKENS_JSON_FILE)}`);
  console.log(`Wrote ${path.relative(ROOT, TOKENS_CSS_FILE)}`);
}

main();
