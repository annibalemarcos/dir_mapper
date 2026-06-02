// main.js - DIR MAP v0.3.3 (cancelamento + segurança + binário PyInstaller)
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let activeProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 980,
    height: 900,
    resizable: true,
    minWidth: 760,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    backgroundColor: '#0e0d0c',
    autoHideMenuBar: true,
    title: 'DIR MAP v0.3.3'
  });
  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
    title: 'Selecione um diretório'
  });
  if (!result.canceled && result.filePaths.length > 0) return result.filePaths[0];
  return null;
});

ipcMain.handle('cancel-mapping', async () => {
  if (activeProcess) {
    try { activeProcess.kill('SIGTERM'); } catch (_) {}
    try { activeProcess.kill('SIGKILL'); } catch (_) {}
    activeProcess = null;
    return true;
  }
  return false;
});

// ----- Resolução de binários -----
// 1) Procura o executável standalone gerado pelo PyInstaller
//    (dir_mapper.exe no Windows, dir_mapper no Linux/macOS).
// 2) Se não achar, cai no script Python + interpretador local.
function findStandaloneBinary() {
  const exeName = process.platform === 'win32' ? 'dir_mapper.exe' : 'dir_mapper';
  const candidates = [
    path.join(process.resourcesPath || '', exeName),
    path.join(process.resourcesPath || '', 'bin', exeName),
    path.join(__dirname, 'bin', exeName),
    path.join(__dirname, exeName),
  ];
  for (const c of candidates) {
    try { if (c && fs.existsSync(c)) return c; } catch (_) {}
  }
  return null;
}

function findPythonScript() {
  const candidates = [
    path.join(process.resourcesPath || '', 'dir_mapper.py'),
    path.join(__dirname, 'dir_mapper.py'),
  ];
  for (const c of candidates) {
    try { if (c && fs.existsSync(c)) return c; } catch (_) {}
  }
  return null;
}

ipcMain.handle('map-directory', async (event, options) => {
  return new Promise((resolve, reject) => {
    const argsPayload = JSON.stringify({
      path: options.path || '',
      hidden_folders: options.hiddenFolders || '',
      hidden_extensions: options.hiddenExtensions || '',
      hide_files: !!options.hideFiles,
      max_depth: options.maxDepth || null,
      max_items: options.maxItems || null,
      format_type: options.formatType || 'uml',
    });

    const standalone = findStandaloneBinary();

    const handleProcess = (proc) => {
      activeProcess = proc;
      let out = '';
      let err = '';
      proc.stdout.on('data', (d) => { out += d.toString('utf8'); });
      proc.stderr.on('data', (d) => { err += d.toString('utf8'); });
      proc.on('error', (e) => {
        activeProcess = null;
        reject(e);
      });
      proc.on('close', (code, signal) => {
        activeProcess = null;
        if (signal === 'SIGTERM' || signal === 'SIGKILL') {
          return reject(new Error('CANCELADO'));
        }
        if (code !== 0) {
          return reject(new Error(err.trim() || 'Erro ao processar diretório'));
        }
        try {
          resolve(JSON.parse(out));
        } catch (e) {
          reject(new Error('Resposta inválida: ' + e.message));
        }
      });
      try {
        proc.stdin.write(argsPayload);
        proc.stdin.end();
      } catch (_) {}
    };

    // 1) Tenta o binário standalone PyInstaller (sem dependência de Python)
    if (standalone) {
      try {
        const proc = spawn(standalone, [], {
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
        });
        handleProcess(proc);
        return;
      } catch (e) {
        // continua para fallback python
      }
    }

    // 2) Fallback: script Python + interpretador do sistema
    const scriptPath = findPythonScript();
    if (!scriptPath) {
      return reject(new Error(
        'dir_mapper não encontrado (nem binário, nem script Python).'
      ));
    }

    const wrapper = `
import sys, os, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, r'${path.dirname(scriptPath).replace(/\\/g, '\\\\')}')
from dir_mapper import map_directory_api
data = json.loads(sys.stdin.read())
print(map_directory_api(**data), end='')
`;

    const tryRun = (cmd, fallback) => {
      const proc = spawn(cmd, ['-c', wrapper], {
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
        stdio: ['pipe', 'pipe', 'pipe'],
      });
      activeProcess = proc;

      let out = '';
      let err = '';
      proc.stdout.on('data', (d) => { out += d.toString('utf8'); });
      proc.stderr.on('data', (d) => { err += d.toString('utf8'); });

      proc.on('error', (e) => {
        if (e.code === 'ENOENT' && fallback) return tryRun(fallback, null);
        activeProcess = null;
        reject(new Error(
          'Python não encontrado. Instale Python 3 ou use a versão com binário embutido.'
        ));
      });

      proc.on('close', (code, signal) => {
        activeProcess = null;
        if (signal === 'SIGTERM' || signal === 'SIGKILL') {
          return reject(new Error('CANCELADO'));
        }
        if (code !== 0) {
          return reject(new Error(err.trim() || 'Erro ao processar diretório'));
        }
        try {
          resolve(JSON.parse(out));
        } catch (e) {
          reject(new Error('Resposta inválida: ' + e.message));
        }
      });

      try {
        proc.stdin.write(argsPayload);
        proc.stdin.end();
      } catch (_) {}
    };

    const firstCmd = process.platform === 'win32' ? 'python' : 'python3';
    const secondCmd = process.platform === 'win32' ? 'py' : 'python';
    tryRun(firstCmd, secondCmd);
  });
});

ipcMain.handle('save-file', async (event, { content, extension, defaultName }) => {
  const filters = [];
  if (extension === 'md') filters.push({ name: 'Markdown', extensions: ['md'] });
  else if (extension === 'json') filters.push({ name: 'JSON', extensions: ['json'] });
  else if (extension === 'txt') filters.push({ name: 'Text', extensions: ['txt'] });
  filters.push({ name: 'Todos os Arquivos', extensions: ['*'] });

  const result = await dialog.showSaveDialog(mainWindow, {
    filters,
    defaultPath: `${defaultName || 'dir_map'}.${extension}`,
    title: `Salvar como .${extension}`
  });
  if (!result.canceled && result.filePath) {
    try {
      fs.writeFileSync(result.filePath, content, 'utf-8');
      return { success: true, path: result.filePath };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }
  return { success: false, canceled: true };
});
