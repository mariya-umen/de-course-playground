const COLLECTION = 'VooDoo · Typography';
const FAMILY = 'Inter';
const WEIGHTS = { regular: 400, medium: 500, semibold: 600, bold: 700 };
const SIZES = [10, 11, 12, 13, 14, 16, 18, 22, 28, 36, 48];
const LINE_HEIGHTS = [14, 16, 20, 24, 28, 36, 44, 56];
const STYLE_WEIGHT = { 'Regular': 400, 'Medium': 500, 'Semi Bold': 600, 'Bold': 700 };

figma.showUI(__html__, { width: 560, height: 560 });

function definitions() {
  const defs = [{ path: 'font-family/sans', type: 'STRING', value: FAMILY, scopes: ['FONT_FAMILY'] }];
  for (const [name, value] of Object.entries(WEIGHTS)) defs.push({ path: 'font-weight/' + name, type: 'FLOAT', value, scopes: ['FONT_WEIGHT'] });
  for (const value of SIZES) defs.push({ path: 'font-size/' + value, type: 'FLOAT', value, scopes: ['FONT_SIZE'] });
  for (const value of LINE_HEIGHTS) defs.push({ path: 'line-height/' + value, type: 'FLOAT', value, scopes: ['LINE_HEIGHT'] });
  return defs;
}

async function ensureVariables(log) {
  const collections = await figma.variables.getLocalVariableCollectionsAsync();
  let collection = collections.find((c) => c.name === COLLECTION);
  if (!collection) {
    collection = figma.variables.createVariableCollection(COLLECTION);
    collection.renameMode(collection.modes[0].modeId, 'Value');
    log('Створено колекцію ' + COLLECTION);
  } else {
    log('Колекція ' + COLLECTION + ' вже є — оновлюю');
  }
  const modeId = collection.modes[0].modeId;
  const all = await figma.variables.getLocalVariablesAsync();
  const inCollection = all.filter((v) => v.variableCollectionId === collection.id);
  const byName = {};
  for (const v of inCollection) byName[v.name] = v;

  let created = 0;
  let updated = 0;
  for (const d of definitions()) {
    const name = 'typography/' + d.path;
    let variable = byName[name];
    if (!variable) {
      variable = figma.variables.createVariable(name, collection, d.type);
      created++;
    } else {
      updated++;
    }
    variable.setValueForMode(modeId, d.value);
    variable.scopes = d.scopes;
    variable.setVariableCodeSyntax('WEB', 'var(--' + d.path.replace(/\//g, '-') + ')');
    byName[name] = variable;
  }
  log('Змінні: створено ' + created + ', оновлено ' + updated);
  return byName;
}

async function bindStyles(vars, log) {
  const styles = await figma.getLocalTextStylesAsync();
  let bound = 0;
  const problems = [];
  for (const style of styles) {
    const before = { font: style.fontName.family + '|' + style.fontName.style, size: style.fontSize, lh: JSON.stringify(style.lineHeight) };
    const weight = STYLE_WEIGHT[style.fontName.style];
    const lh = style.lineHeight.unit === 'PIXELS' ? style.lineHeight.value : null;
    const targets = [
      ['fontFamily', vars['typography/font-family/sans']],
      ['fontSize', vars['typography/font-size/' + style.fontSize]],
    ];
    if (lh !== null) targets.push(['lineHeight', vars['typography/line-height/' + lh]]);
    if (weight) targets.push(['fontWeight', vars['typography/font-weight/' + Object.keys(WEIGHTS).find((k) => WEIGHTS[k] === weight)]]);
    try {
      await figma.loadFontAsync(style.fontName);
      for (const [field, variable] of targets) {
        if (!variable) throw new Error('немає змінної для ' + field);
        style.setBoundVariable(field, variable);
      }
      const after = { font: style.fontName.family + '|' + style.fontName.style, size: style.fontSize, lh: JSON.stringify(style.lineHeight) };
      if (after.font !== before.font || after.size !== before.size || after.lh !== before.lh) {
        for (const [field] of targets) style.setBoundVariable(field, null);
        style.fontName = { family: before.font.split('|')[0], style: before.font.split('|')[1] };
        style.fontSize = before.size;
        style.lineHeight = JSON.parse(before.lh);
        problems.push(style.name + ': значення змінилися — прив\'язку скасовано');
      } else {
        bound++;
      }
    } catch (e) {
      problems.push(style.name + ': ' + e.message);
    }
  }
  log('Стилі з прив\'язкою до змінних: ' + bound + ' з ' + styles.length);
  for (const p of problems) log('  ! ' + p);
}

async function exportJson(vars) {
  const group = {};
  for (const name of Object.keys(vars).sort()) {
    const variable = vars[name];
    const parts = name.split('/');
    const modeId = Object.keys(variable.valuesByMode)[0];
    const raw = variable.valuesByMode[modeId];
    let token;
    if (parts[1] === 'font-family') token = { $type: 'fontFamily', $value: raw };
    else if (parts[1] === 'font-weight') token = { $type: 'fontWeight', $value: raw };
    else token = { $type: 'dimension', $value: raw + 'px' };
    let node = group;
    for (const key of parts.slice(0, -1)) node = node[key] = node[key] || {};
    node[parts[parts.length - 1]] = token;
  }
  return JSON.stringify({ [COLLECTION]: { Value: group } }, null, 2);
}

figma.ui.onmessage = async (msg) => {
  if (msg.type !== 'run') return;
  const lines = [];
  const log = (t) => { lines.push(t); figma.ui.postMessage({ type: 'log', text: t }); };
  try {
    const vars = await ensureVariables(log);
    await bindStyles(vars, log);
    const json = await exportJson(vars);
    figma.ui.postMessage({ type: 'done', json });
    log('Готово. Скопіюйте JSON нижче й передайте його в чат.');
  } catch (e) {
    figma.ui.postMessage({ type: 'error', text: String(e && e.message ? e.message : e) });
  }
};
