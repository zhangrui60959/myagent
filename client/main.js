/**
 * MyAgent Electron 客户端 - 主进程
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, globalShortcut } = require('electron');
const path = require('path');
const WebSocket = require('ws');
const http = require('http');

// ============== 配置 ==============
const HUB_HOST = process.env.HUB_HOST || '127.0.0.1';
const HUB_PORT = process.env.HUB_PORT || '8765';
const WS_PORT = process.env.WS_PORT || '8765';

// ============== 全局变量 ==============
let mainWindow = null;
let tray = null;
let ws = null;
let isQuitting = false;

// ============== 窗口管理 ==============
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'MyAgent',
    icon: path.join(__dirname, 'assets/icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.loadFile('index.html');

  // 窗口事件
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // 创建菜单
  createMenu();

  // 创建托盘
  createTray();

  console.log('[MyAgent] 客户端已启动');
}

// ============== 菜单 ==============
function createMenu() {
  const template = [
    {
      label: 'MyAgent',
      submenu: [
        { label: '关于 MyAgent', role: 'about' },
        { type: 'separator' },
        {
          label: '偏好设置',
          accelerator: 'CmdOrCtrl+,',
          click: () => mainWindow?.webContents.send('open-settings')
        },
        { type: 'separator' },
        { label: '退出', accelerator: 'CmdOrCtrl+Q', click: () => { isQuitting = true; app.quit(); } }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { label: '撤销', role: 'undo' },
        { label: '重做', role: 'redo' },
        { type: 'separator' },
        { label: '剪切', role: 'cut' },
        { label: '复制', role: 'copy' },
        { label: '粘贴', role: 'paste' },
        { label: '全选', role: 'selectAll' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { label: '重新加载', accelerator: 'CmdOrCtrl+R', role: 'reload' },
        { label: '强制重载', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
        { type: 'separator' },
        { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
        { label: '缩小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
        { label: '重置缩放', role: 'resetZoom' },
        { type: 'separator' },
        { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
        { label: '关闭', accelerator: 'CmdOrCtrl+W', role: 'close' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// ============== 托盘 ==============
function createTray() {
  // 使用系统默认图标
  tray = new Tray(path.join(__dirname, 'assets/tray-icon.png'));
  
  const contextMenu = Menu.buildFromTemplate([
    { label: '显示 MyAgent', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: '连接状态', enabled: false, id: 'connection-status' },
    { type: 'separator' },
    { label: '退出', click: () => { isQuitting = true; app.quit(); } }
  ]);

  tray.setToolTip('MyAgent');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    mainWindow?.show();
  });
}

// ============== WebSocket 连接 ==============
function connectToHub() {
  const clientId = `electron-${Date.now()}`;
  const url = `ws://${HUB_HOST}:${WS_PORT}/ws/${clientId}`;
  console.log(`[WS] 正在连接: ${url}`);

  ws = new WebSocket(url);

  ws.on('open', () => {
    console.log('[WS] 已连接到 Hub');
    mainWindow?.webContents.send('hub-status', { connected: true });
    updateTrayStatus(true);
  });

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      mainWindow?.webContents.send('hub-message', message);
    } catch (e) {
      console.error('[WS] 解析消息失败:', e);
    }
  });

  ws.on('close', () => {
    console.log('[WS] 连接已断开');
    mainWindow?.webContents.send('hub-status', { connected: false });
    updateTrayStatus(false);

    // 5秒后重连
    if (!isQuitting) {
      setTimeout(connectToHub, 5000);
    }
  });

  ws.on('error', (error) => {
    console.error('[WS] 连接错误:', error.message);
    mainWindow?.webContents.send('hub-status', { connected: false, error: error.message });
  });
}

function updateTrayStatus(connected) {
  if (tray) {
    const contextMenu = Menu.buildFromTemplate([
      { label: '显示 MyAgent', click: () => mainWindow?.show() },
      { type: 'separator' },
      { 
        label: `状态: ${connected ? '已连接' : '未连接'}`,
        enabled: false
      },
      { type: 'separator' },
      { 
        label: '重新连接',
        click: () => {
          if (ws) ws.close();
          connectToHub();
        }
      },
      { type: 'separator' },
      { label: '退出', click: () => { isQuitting = true; app.quit(); } }
    ]);
    tray.setContextMenu(contextMenu);
  }
}

function sendToHub(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
    return true;
  }
  return false;
}

// ============== IPC 处理 ==============
ipcMain.handle('hub-connect', async () => {
  connectToHub();
  return { success: true };
});

ipcMain.handle('hub-disconnect', async () => {
  if (ws) ws.close();
  return { success: true };
});

ipcMain.handle('hub-send', async (event, message) => {
  if (!sendToHub(message)) {
    return { success: false, error: 'Not connected to Hub' };
  }
  return { success: true };
});

ipcMain.handle('hub-status', async () => {
  return {
    connected: ws?.readyState === WebSocket.OPEN,
    host: HUB_HOST,
    port: WS_PORT
  };
});

ipcMain.handle('hub-check', async () => {
  // 检查 Hub 是否可用
  return new Promise((resolve) => {
    const req = http.get(`http://${HUB_HOST}:${HUB_PORT}/health`, (res) => {
      resolve({ available: res.statusCode === 200 });
    });
    req.on('error', () => resolve({ available: false }));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve({ available: false });
    });
  });
});

// ============== 全局快捷键 ==============
function registerShortcuts() {
  // 快速唤起
  globalShortcut.register('CommandOrControl+Shift+M', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });
}

// ============== 应用生命周期 ==============
app.whenReady().then(() => {
  createWindow();
  connectToHub();
  registerShortcuts();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow?.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    isQuitting = true;
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  if (ws) ws.close();
  globalShortcut.unregisterAll();
});

console.log('[MyAgent] 启动中...');
