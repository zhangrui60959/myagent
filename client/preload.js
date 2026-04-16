/**
 * MyAgent preload.js - 安全桥接
 */

const { contextBridge, ipcRenderer } = require('electron');

// 回调存储
const callbacks = {
  onHubStatus: null,
  onHubMessage: null,
  onOpenSettings: null
};

// 监听 Hub 状态
ipcRenderer.on('hub-status', (event, data) => {
  if (callbacks.onHubStatus) callbacks.onHubStatus(data);
});

// 监听 Hub 消息
ipcRenderer.on('hub-message', (event, data) => {
  if (callbacks.onHubMessage) callbacks.onHubMessage(data);
});

// 监听设置打开
ipcRenderer.on('open-settings', () => {
  if (callbacks.onOpenSettings) callbacks.onOpenSettings();
});

// 暴露 API
contextBridge.exposeInMainWorld('myagent', {
  // Hub 连接
  connect: () => ipcRenderer.invoke('hub-connect'),
  disconnect: () => ipcRenderer.invoke('hub-disconnect'),
  send: (message) => ipcRenderer.invoke('hub-send', message),
  status: () => ipcRenderer.invoke('hub-status'),
  checkHub: () => ipcRenderer.invoke('hub-check'),

  // 监听器
  onHubStatus: (callback) => { callbacks.onHubStatus = callback; },
  onHubMessage: (callback) => { callbacks.onHubMessage = callback; },
  onOpenSettings: (callback) => { callbacks.onOpenSettings = callback; },

  // 移除监听器
  offHubStatus: () => { callbacks.onHubStatus = null; },
  offHubMessage: () => { callbacks.onHubMessage = null; }
});

console.log('[Preload] MyAgent API 已加载');
