const fs = require('fs');
const path = require('path');

const COLLECTION = 'VooDoo · Typography';
const file = process.argv[2];
if (!file) {
  console.error('Usage: node scripts/check-typography.js <figma-typography-export.json>');
  process.exit(2);
}

function flatten(node, prefix, out) {
  if ('$value' in node) out[prefix] = [node.$type, node.$value];
  for (const [key, child] of Object.entries(node)) {
    if (key.startsWith('$') || typeof child !== 'object' || child === null) continue;
    flatten(child, prefix ? `${prefix}.${key}` : key, out);
  }
  return out;
}

const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
const root = Array.isArray(raw) ? raw[0] : raw;
const figma = flatten(root[COLLECTION].Value.typography, '', {});
const repoRaw = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'design', 'figma-variables.json'), 'utf8'));
const repo = flatten((Array.isArray(repoRaw) ? repoRaw[0] : repoRaw)[COLLECTION].Value.typography, '', {});

const keys = [...new Set([...Object.keys(figma), ...Object.keys(repo)])].sort();
const diffs = keys.filter((k) => JSON.stringify(figma[k]) !== JSON.stringify(repo[k]));
for (const k of diffs) console.log(`DIFF ${k}: figma=${JSON.stringify(figma[k])} repo=${JSON.stringify(repo[k])}`);
console.log(`${keys.length} tokens compared, ${diffs.length} differences`);
process.exit(diffs.length ? 1 : 0);
