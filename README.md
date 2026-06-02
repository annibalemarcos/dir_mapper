# DIR MAP

<<<<<<< HEAD
![Windows](https://img.shields.io/badge/platform-Windows-blue)
![Electron](https://img.shields.io/badge/Electron-desktop-47848F)
![Python](https://img.shields.io/badge/Python-backend-3776AB)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

**DIR MAP** é um aplicativo desktop para mapear estruturas de diretórios locais e exportar o resultado em formatos úteis como **árvore/UML**, **Markdown**, **TXT**, **JSON**, **diagrama textual** e **estatísticas em Markdown**.

A ideia é simples: você escolhe uma pasta, o app varre arquivos e subpastas, aplica filtros para não cair em buracos negros como `node_modules`, `.git`, `dist` e `build`, e gera uma visão organizada da estrutura. É uma ferramenta pequena, direta e útil para documentar projetos, auditar pastas, entender bases de código e mostrar a arquitetura de um diretório sem depender de prints improvisados.

---

## Screenshot

> Adicione aqui uma imagem ou GIF do app em funcionamento.
>
> Sugestão de caminho:
>
> ```md
> ![DIR MAP - Dashboard](docs/screenshot-dashboard.png)
> ```

---

## Download

Quando houver uma versão publicada, baixe o instalador pela aba **Releases** do repositório:

```txt
https://github.com/annibalemarcos/dir_mapper/releases
```

> Recomenda-se publicar instaladores, `.exe` e arquivos `.zip` na aba **Releases**, não diretamente dentro do repositório.
=======
**DIR MAP** é um aplicativo desktop para mapear a estrutura de diretórios do computador e exportar o resultado em formatos úteis como **árvore/UML**, **JSON**, **diagrama textual**, **Markdown**, **TXT** e **JSON**.

A ideia é simples e boa: você escolhe uma pasta, o app varre os arquivos e subpastas, aplica filtros para não cair em buracos negros como `node_modules` e `.git`, e gera uma visão organizada da estrutura. É aquele tipo de ferramenta pequena que salva tempo quando você precisa documentar projeto, auditar pastas ou mostrar a estrutura de um sistema sem mandar um print capenga.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

---

## O que o projeto faz

- Mapeia diretórios locais de forma visual.
<<<<<<< HEAD
- Exibe a estrutura em formato de árvore.
- Mostra estatísticas gerais do diretório varrido.
- Exibe tamanho total, quantidade de arquivos, pastas e profundidade máxima encontrada.
- Exibe ranking das pastas mais pesadas.
- Exibe ranking das extensões que mais ocupam espaço.
- Permite exportar o resultado como `.md`, `.json` ou `.txt`.
- Permite exportar somente o dashboard/estatísticas em Markdown.
=======
- Mostra a estrutura em formato de árvore.
- Permite exportar o resultado como `.md`, `.json` ou `.txt`.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
- Permite copiar o resultado para a área de transferência.
- Permite ocultar pastas específicas.
- Permite ocultar extensões específicas.
- Permite ocultar todos os arquivos e exibir apenas pastas.
- Permite limitar a profundidade da varredura.
- Permite limitar a quantidade máxima de itens lidos.
<<<<<<< HEAD
- Evita travamentos em diretórios gigantes usando filtros e limites de segurança.
=======
- Evita travamentos em diretórios gigantes usando filtros e limite de segurança.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
- Tem botão de cancelamento para interromper a varredura.
- Pode ser empacotado como `.exe` para Windows com Python embutido.

---

<<<<<<< HEAD
## Uso básico

1. Abra o **DIR MAP**.
2. Clique em **Selecionar pasta**.
3. Escolha o formato de saída desejado.
4. Ajuste filtros, profundidade e limite de itens se necessário.
5. Clique em **Mapear**.
6. Analise a árvore, o dashboard e as estatísticas.
7. Copie o resultado ou exporte em arquivo.

---

## Casos de uso

O **DIR MAP** é útil para:

- documentar a estrutura de projetos de software;
- gerar seções de README automaticamente;
- revisar pastas grandes antes de backup, limpeza ou publicação;
- entender rapidamente a organização de um projeto legado;
- identificar pastas pesadas dentro de um diretório;
- visualizar extensões que ocupam mais espaço;
- preparar relatórios técnicos simples sobre uma base de arquivos.

---

=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
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

<<<<<<< HEAD
### Interface Electron

- Exibe a janela do aplicativo.
- Permite selecionar uma pasta local.
- Envia as opções de mapeamento para o backend.
- Recebe o resultado da varredura.
- Mostra a árvore, o dashboard e as estatísticas na tela.
- Copia e exporta os resultados.

### Backend Python

- Recebe parâmetros via JSON.
- Varre o diretório usando `os.scandir`.
- Aplica filtros de pastas, extensões, profundidade e limite de itens.
- Calcula estatísticas de arquivos, pastas, tamanhos e extensões.
- Gera a saída nos formatos disponíveis.
- Retorna o resultado para o Electron.

Quando empacotado, o Electron tenta usar primeiro o binário `dir_mapper.exe` gerado pelo PyInstaller. Se ele não existir, o app cai no modo de desenvolvimento e tenta usar o Python instalado no sistema.
=======
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
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

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

<<<<<<< HEAD
### Estatísticas em Markdown

```md
# Estatísticas do diretório

- Tamanho total: 1.42 GB
- Arquivos: 8.431
- Pastas: 912
- Profundidade máxima: 9
- Média por arquivo: 176.4 KB
```

=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
---

## Recursos de segurança

<<<<<<< HEAD
Para evitar travamentos ao abrir pastas gigantes, o app já vem com proteções importantes:
=======
Para evitar que o app trave ao abrir pastas gigantes, ele já vem com algumas proteções:
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

- Pastas pesadas ignoradas por padrão:

```txt
node_modules, .git, __pycache__, .venv, venv, dist, build, .next, .cache, target, .idea, .vscode
```

- Limite padrão de itens: **100.000**.
- Profundidade máxima absoluta: **50 níveis**.
- Varredura iterativa, evitando recursão profunda.
<<<<<<< HEAD
- Botão **Cancelar** para encerrar a varredura em andamento.
=======
- Botão **Cancelar** para matar o processo em andamento.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
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
<<<<<<< HEAD
- **npm**
=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

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

<<<<<<< HEAD
O projeto inclui um arquivo `build.bat` para automatizar o processo.
=======
O projeto já inclui um arquivo `build.bat` para automatizar o processo.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

```bash
build.bat
```

Ele executa, em sequência:

1. Instala as dependências Node.
<<<<<<< HEAD
2. Instala ou atualiza o PyInstaller.
=======
2. Instala/atualiza o PyInstaller.
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
3. Gera o binário Python `bin/dir_mapper.exe`.
4. Gera o instalador Electron.

Ao final, os arquivos principais ficam em:

```txt
dist\DIR MAP Setup 0.2.0.exe
dist\win-unpacked\DIR MAP.exe
```

<<<<<<< HEAD
> O número da versão pode mudar conforme o `package.json`.

=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
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

<<<<<<< HEAD
## Observação sobre arquivos gerados

Arquivos de build, instaladores, executáveis e pacotes compactados normalmente não precisam ficar versionados no repositório principal.

Use a aba **Releases** do GitHub para publicar arquivos como:

```txt
.exe
.zip
Setup.exe
instaladores
builds finais
```

Recomenda-se manter no `.gitignore` pastas e arquivos como:

```gitignore
node_modules/
dist/
build/
dist-build/
bin/
*.zip
*.exe
.env
```

Isso evita problemas com limite de tamanho do GitHub e mantém o repositório mais limpo.

---

## Status do projeto

O projeto já tem uma base funcional e utilizável, principalmente no Windows. Ainda assim, deve ser tratado como uma versão em evolução.

### Já implementado

- Varredura iterativa.
- Filtros básicos.
- Exportação em múltiplos formatos.
- Dashboard de estatísticas.
- Exibição de tamanhos em unidade legível.
- Ranking de pastas mais pesadas.
- Ranking de extensões por tamanho ocupado.
- Cancelamento de varredura.
- Empacotamento com Python embutido.
- Interface simples e direta.

### Melhorias planejadas
=======
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
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b

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

<<<<<<< HEAD
## Ideias futuras

- Modo “documentar projeto”, gerando automaticamente uma seção para README.
- Comparador de versões de diretórios.
- Relatório visual com contagem de arquivos por extensão.
- Estatísticas avançadas de tamanho por pasta.
- Exportação para Mermaid.
- Exportação para Graphviz.
- Modo CLI completo, sem Electron.
- Histórico dos últimos diretórios mapeados.

---

## Changelog

### v0.3.3.2 — Dashboard de estatísticas

- Adicionado dashboard logo acima do resultado principal.
- Adicionado tamanho total varrido.
- Adicionado total de arquivos e pastas.
- Adicionada profundidade máxima encontrada.
- Adicionada média de tamanho por arquivo.
- Adicionada contagem de itens ignorados e erros de permissão.
- Adicionado ranking das pastas mais pesadas.
- Adicionado ranking das extensões que mais ocupam espaço.
- Tamanhos agora são exibidos em unidade legível: B, KB, MB, GB, TB ou PB.
- O mapa textual passou a mostrar o tamanho de arquivos e diretórios ao lado de cada item.
- Novo botão **ESTATÍSTICAS** em **EXPORTAR COMO**, para salvar somente o dashboard/estatísticas em Markdown.

---

=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
## Licença

Este projeto está configurado como **MIT** no `package.json`.

<<<<<<< HEAD
---

## Observação

Este README foi criado com base na análise dos arquivos do projeto:

- `main.js`
- `index.html`
- `dir_mapper.py`
- `dir_mapper_cli.py`
- `package.json`
- `build.bat`
- `requirements-build.txt`
=======
>>>>>>> 932198d66fd0a4be2e1de668ac4c75d3ac237d2b
