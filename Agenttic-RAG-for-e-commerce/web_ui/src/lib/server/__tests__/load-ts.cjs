const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');
const ts = require('typescript');

function loader(overrides = {}) {
  const cache = new Map();
  return function load(filename) {
    filename = path.resolve(filename);
    if (cache.has(filename)) return cache.get(filename).exports;
    const mod = new Module(filename);
    mod.paths = Module._nodeModulePaths(path.dirname(filename));
    cache.set(filename, mod);
    const normalRequire = mod.require.bind(mod);
    mod.require = name => {
      if (name === 'server-only') return {}; // Next's compile-time client boundary.
      if (overrides[name]) return overrides[name];
      const target = name.startsWith('@/')
        ? path.resolve(__dirname, '../../../', name.slice(2))
        : name.startsWith('.') ? path.resolve(path.dirname(filename), name) : null;
      if (target && fs.existsSync(`${target}.ts`)) return load(`${target}.ts`);
      return normalRequire(name);
    };
    mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
      compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
    }).outputText, filename);
    return mod.exports;
  };
}
module.exports = { loader };
