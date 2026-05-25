# DIR MAP

**DIR MAP** é um aplicativo desktop para mapear a estrutura de diretórios do computador e exportar o resultado em formatos úteis como **árvore/UML**, **JSON**, **diagrama textual**, **Markdown**, **TXT** e **JSON**.

A ideia é simples e boa: você escolhe uma pasta, o app varre os arquivos e subpastas, aplica filtros para não cair em buracos negros como `node_modules` e `.git`, e gera uma visão organizada da estrutura. É aquele tipo de ferramenta pequena que salva tempo quando você precisa documentar projeto, auditar pastas ou mostrar a estrutura de um sistema sem mandar um print capenga.

---

## O que o projeto faz

- Mapeia diretórios locais de forma visual.
- Mostra a estrutura em formato de árvore.
- Permite exportar o resultado como `.md`, `.json` ou `.txt`.
- Permite copiar o resultado para a área de transferência.
- Permite ocultar pastas específicas.
- Permite ocultar extensões específicas.
- Permite ocultar todos os arquivos e exibir apenas pastas.
- Permite limitar a profundidade da varredura.
- Permite limitar a quantidade máxima de itens lidos.
- Evita travamentos em diretórios gigantes usando filtros e limite de segurança.
- Tem botão de cancelamento para interromper a varredura.
- Pode ser empacotado como `.exe` para Windows com Python embutido.

---

## Stack utilizada

- **Electron** — interface desktop.
- **Node.js** — processo principal do app e integração com o sistema.
- **Python** — motor de varredura dos diretórios.
- **PyInstaller** — empacotamento do backend Python em executável.
- **electron-builder** — geração do instalador desktop.
- **HTML/CSS/JavaScript** — interface do usuário.

---

## Como funciona por baixo do capô

O projeto é dividido em duas partes principais:

1. **Interface Electron**
   - Exibe a janela do aplicativo.
   - Permite selecionar uma pasta.
   - Envia as opções de mapeamento para o backend.
   - Recebe o resultado e mostra na tela.
   - Salva/exporta arquivos.

2. **Backend Python**
   - Recebe os parâmetros via JSON.
   - Varre o diretório usando `os.scandir`.
   - Aplica filtros de pastas, extensões, profundidade e limite de itens.
   - Gera a saída nos formatos disponíveis.
   - Retorna o resultado para o Electron.

Quando empacotado, o Electron tenta usar primeiro o binário `dir_mapper.exe` gerado pelo PyInstaller. Se ele não existir, cai no modo de desenvolvimento e tenta usar o Python instalado no sistema.

---

## Formatos de saída

### Árvore / UML

```txt
meu-projeto/
├── app/
│   ├── main.py
│   └── routes.py
├── static/
└── README.md
```

### JSON

```json
{
  "name": "meu-projeto",
  "type": "directory",
  "children": []
}
```

### Diagrama textual

```txt
┌─────────────┐
│ meu-projeto │
└─────────────┘
```

---

## Recursos de segurança

Para evitar que o app trave ao abrir pastas gigantes, ele já vem com algumas proteções:

- Pastas pesadas ignoradas por padrão:

```txt
node_modules, .git, __pycache__, .venv, venv, dist, build, .next, .cache, target, .idea, .vscode
```

- Limite padrão de itens: **100.000**.
- Profundidade máxima absoluta: **50 níveis**.
- Varredura iterativa, evitando recursão profunda.
- Botão **Cancelar** para matar o processo em andamento.
- Ignora links simbólicos, sockets e entradas especiais.
- Trata erros de permissão sem quebrar o app inteiro.

---

## Estrutura do projeto

```txt
DIR MAP/
├── build.bat                 # Build completo para Windows
├── dir_mapper.py             # Motor principal de varredura em Python
├── dir_mapper_cli.py         # Entrada CLI usada pelo PyInstaller
├── index.html                # Interface do app
├── main.js                   # Processo principal do Electron
├── open_cmd.bat              # Atalho para abrir terminal
├── package.json              # Configuração Node/Electron
├── requirements-build.txt    # Dependências de build Python
└── README.md                 # Documentação do projeto
```

---

## Como rodar em modo desenvolvimento

### Pré-requisitos

Você precisa ter instalado:

- **Node.js 16+**
- **Python 3.8+**

### Instale as dependências

```bash
npm install
```

### Rode o app

```bash
npm start
```

---

## Como gerar o executável para Windows

O projeto já inclui um arquivo `build.bat` para automatizar o processo.

```bash
build.bat
```

Ele executa, em sequência:

1. Instala as dependências Node.
2. Instala/atualiza o PyInstaller.
3. Gera o binário Python `bin/dir_mapper.exe`.
4. Gera o instalador Electron.

Ao final, os arquivos principais ficam em:

```txt
dist\DIR MAP Setup 0.2.0.exe
dist\win-unpacked\DIR MAP.exe
```

---

## Build manual

Caso prefira rodar etapa por etapa:

```bash
npm install
python -m pip install pyinstaller
npm run build-python
npm run build-win
```

Ou tudo em uma linha:

```bash
npm run build-all-win
```

---

## Teste direto do backend Python

Você também pode testar o motor de mapeamento sem abrir a interface Electron:

```bash
python dir_mapper.py "C:\\caminho\\da\\pasta" uml
```

Ou, depois de gerar o binário:

```bash
echo {"path":"C:\\caminho\\da\\pasta","format_type":"uml"} | bin\dir_mapper.exe
```

---

## Scripts disponíveis

No `package.json`:

```json
{
  "start": "electron .",
  "build-python": "pyinstaller --onefile --name dir_mapper --console --distpath bin --workpath build/pyinstaller --specpath build/pyinstaller --clean dir_mapper_cli.py",
  "build-win": "electron-builder --win",
  "build-mac": "electron-builder --mac",
  "build-linux": "electron-builder --linux",
  "build-all-win": "npm run build-python && electron-builder --win"
}
```

---

## Status do projeto

O projeto já tem uma base funcional e utilizável, principalmente no Windows. Ainda assim, vale tratar como uma versão em evolução.

Pontos que já estão bem resolvidos:

- Varredura iterativa.
- Filtros básicos.
- Exportação.
- Cancelamento.
- Empacotamento com Python embutido.
- Interface simples e direta.

Pontos que podem melhorar:

- Melhorar a interface visual.
- Adicionar tema claro/escuro.
- Criar página de configurações.
- Adicionar opção de salvar presets de filtros.
- Adicionar testes automatizados.
- Melhorar suporte a Linux/macOS.
- Adicionar barra de progresso real para diretórios grandes.
- Permitir exportação em HTML.
- Permitir comparação entre dois mapas de diretórios.

---

## Licença

Este projeto está configurado como **MIT** no `package.json`.

---

## Observação

Este README foi criado com base na análise dos arquivos do projeto: `main.js`, `index.html`, `dir_mapper.py`, `dir_mapper_cli.py`, `package.json`, `build.bat` e `requirements-build.txt`.
