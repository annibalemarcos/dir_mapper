# DIR MAP v0.2 — Desktop (Electron + Python embutido)

Versão estável do mapeador de diretórios. **O usuário final não precisa instalar Python** — o interpretador é empacotado dentro do `.exe` via PyInstaller.

---

## ✨ O que mudou em relação à v0.1

| Bug / Limitação | Correção na v0.2 |
|---|---|
| App **trava** em diretórios gigantes (esquecer de filtrar `node_modules`, `.git`...) | Lista padrão de pastas pesadas **pré-preenchida** + **limite de itens** (default 100k) + trava de profundidade máxima absoluta (50) |
| Travamento sem possibilidade de cancelar | Botão **CANCELAR** que mata o processo imediatamente |
| Recursão Python profunda podia estourar limites | Varredura **iterativa** com `os.scandir`, muito mais rápida |
| Output sem feedback | Estatísticas: **nº de itens lidos**, **tempo decorrido** e badge **TRUNCADO** |
| Usuário final precisava instalar Python | **Python embutido via PyInstaller** — basta instalar o `.exe`, nada mais |
| `dir_mapper.py` perdido dentro do .exe empacotado | Empacotado corretamente como `extraResources` |

---

## 🚀 Para o USUÁRIO FINAL

1. Baixar e executar `DIR MAP Setup 0.2.0.exe` (gerado pelo build).
2. Pronto. Nenhuma dependência adicional.

---

## 🛠️ Para QUEM VAI BUILDAR (você)

### Pré-requisitos (apenas na sua máquina, **não** no PC do usuário final):
- **Node.js** ≥ 16 — https://nodejs.org
- **Python** ≥ 3.8 — https://python.org

### Build em 1 clique (Windows)
```bash
build.bat
```
Saída:
- `dist\DIR MAP Setup 0.2.0.exe` — instalador NSIS
- `dist\win-unpacked\DIR MAP.exe` — versão portátil

### Build manual (passo a passo)
```bash
npm install
pip install pyinstaller
npm run build-python    # gera bin\dir_mapper.exe (~7 MB)
npm run build-win       # gera dist\DIR MAP Setup 0.2.0.exe
```

### Build em uma única linha
```bash
npm run build-all-win
```

---

## 🧠 Como funciona internamente

1. O Electron (`main.js`) procura primeiro o binário standalone:
   ```
   process.resourcesPath/bin/dir_mapper.exe
   ```
2. Se encontrar, executa-o passando os parâmetros via JSON no stdin.
3. Se **não** encontrar (modo dev, sem PyInstaller), cai em fallback: chama `python` ou `py` no sistema.

→ Resultado: o `.exe` distribuído sempre funciona, **sem dependências externas**.

---

## 🔒 Comportamento de segurança

- Lista padrão de pastas ignoradas: `node_modules, .git, __pycache__, .venv, venv, dist, build, .next, .cache, target, .idea, .vscode`
- Limite duro de **100.000 itens** por mapeamento (configurável na UI)
- Profundidade máxima absoluta: **50 níveis**
- Botão **CANCELAR** envia `SIGTERM`/`SIGKILL` ao processo

---

## 📂 Estrutura

```
desktop/
├── main.js                    # Processo principal Electron (IPC, spawn)
├── index.html                 # UI dark/âmbar
├── dir_mapper.py              # Lógica de varredura iterativa + formatadores
├── dir_mapper_cli.py          # Entry point empacotado pelo PyInstaller
├── package.json               # Config electron-builder (NSIS)
├── build.bat                  # Build completo em 1 clique (Windows)
├── requirements-build.txt     # pyinstaller (apenas para build)
└── README.md
```

---

## 🧪 Teste rápido (sem UI)

Após o build:
```bash
echo {"path":"C:\\Users\\eu\\meu-projeto","format_type":"uml"} | bin\dir_mapper.exe
```
Saída: `{"content": "...", "items": N, "truncated": false, "elapsed_ms": M}`

---

## 🌐 Versão Web

Existe também a versão **100% web** (sem instalação, sem Python): basta abrir o link do app no navegador. Faz tudo client-side via `webkitdirectory`.
