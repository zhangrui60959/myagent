/**
 * MyAgent Renderer - 渲染进程
 */

// ============== DOM 元素 ==============
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const welcomeEl = document.getElementById('welcome');
const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('inputMessage');
const btnSend = document.getElementById('btnSend');
const btnClear = document.getElementById('btnClear');
const settingsPanel = document.getElementById('settingsPanel');
const overlay = document.getElementById('overlay');
const agentItems = document.querySelectorAll('.agent-item');

// ============== 状态 ==============
let isConnected = false;
let currentAgent = 'general';
let messageCount = 0;

// ============== 初始化 ==============
async function init() {
  // 监听 Hub 状态
  window.myagent.onHubStatus(handleHubStatus);
  
  // 监听 Hub 消息
  window.myagent.onHubMessage(handleHubMessage);
  
  // 监听设置打开
  window.myagent.onOpenSettings(openSettings);
  
  // 检查 Hub 状态
  const status = await window.myagent.status();
  updateConnectionStatus(status.connected);
  
  // 检查 Hub 可用性
  const check = await window.myagent.checkHub();
  if (!check.available) {
    addMessage('system', '⚠️ 无法连接到 Hub 服务，请确保 Hub 已启动。\n运行: cd hub && python main.py');
  }
  
  // 事件绑定
  inputEl.addEventListener('keydown', handleKeyDown);
  inputEl.addEventListener('input', autoResize);
  btnSend.addEventListener('click', sendMessage);
  btnClear.addEventListener('click', clearMessages);
  
  // Agent 选择
  agentItems.forEach(item => {
    item.addEventListener('click', () => selectAgent(item.dataset.agent));
  });
}

// ============== 状态处理 ==============
function handleHubStatus(data) {
  updateConnectionStatus(data.connected, data.error);
}

function updateConnectionStatus(connected, error = null) {
  isConnected = connected;
  statusDot.className = 'status-dot';
  
  if (connected) {
    statusDot.classList.add('connected');
    statusText.textContent = '已连接';
    btnSend.disabled = false;
  } else {
    statusText.textContent = error ? `错误: ${error}` : '未连接';
    btnSend.disabled = true;
  }
}

function handleHubMessage(data) {
  if (data.type === 'connected') {
    return; // 忽略连接消息
  }
  
  if (data.type === 'status') {
    // 正在处理中
    return;
  }
  
  if (data.type === 'response') {
    addMessage('assistant', data.result);
    setLoading(false);
  }
  
  if (data.type === 'error') {
    addMessage('error', `错误: ${data.error}`);
    setLoading(false);
  }
  
  if (data.type === 'pong') {
    console.log('[Client] 心跳响应');
  }
}

// ============== 消息处理 ==============
function addMessage(role, content, time = new Date()) {
  messageCount++;
  
  // 隐藏欢迎页
  welcomeEl.style.display = 'none';
  messagesEl.style.display = 'block';
  
  const div = document.createElement('div');
  div.className = `message ${role}`;
  
  const timeStr = time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  
  if (role === 'system') {
    div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
  } else {
    div.innerHTML = `
      <div class="message-content">${formatMarkdown(content)}</div>
      <div class="message-time">${timeStr}</div>
    `;
  }
  
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(loading) {
  if (loading) {
    const div = document.createElement('div');
    div.className = 'message assistant loading-message';
    div.id = 'loadingMsg';
    div.innerHTML = `<div class="loading"><span></span><span></span><span></span></div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } else {
    const loadingMsg = document.getElementById('loadingMsg');
    if (loadingMsg) loadingMsg.remove();
  }
}

function clearMessages() {
  messagesEl.innerHTML = '';
  messageCount = 0;
  welcomeEl.style.display = 'flex';
  messagesEl.style.display = 'none';
}

// ============== 发送消息 ==============
async function sendMessage() {
  const content = inputEl.value.trim();
  if (!content || !isConnected) return;
  
  // 添加用户消息
  addMessage('user', content);
  
  // 清空输入框
  inputEl.value = '';
  inputEl.style.height = 'auto';
  
  // 显示加载
  setLoading(true);
  
  // 发送
  const result = await window.myagent.send({
    type: 'task',
    content: content,
    agent_type: currentAgent,
    id: Date.now().toString()
  });
  
  if (!result.success) {
    addMessage('error', `发送失败: ${result.error}`);
    setLoading(false);
  }
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize() {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 150) + 'px';
}

// ============== Agent 选择 ==============
function selectAgent(agent) {
  currentAgent = agent;
  agentItems.forEach(item => {
    item.classList.toggle('active', item.dataset.agent === agent);
  });
}

// ============== 设置面板 ==============
function openSettings() {
  settingsPanel.style.display = 'block';
  overlay.style.display = 'block';
}

function closeSettings() {
  settingsPanel.style.display = 'none';
  overlay.style.display = 'none';
}

function saveSettings() {
  const hub = document.getElementById('settingHub').value;
  const port = document.getElementById('settingPort').value;
  
  // 保存到本地存储
  localStorage.setItem('myagent_hub', hub);
  localStorage.setItem('myagent_port', port);
  
  closeSettings();
  
  // 重新连接
  window.myagent.disconnect();
  window.myagent.connect();
}

// ============== 工具函数 ==============
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  // 简单的 Markdown 格式化
  return text
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

// ============== 启动 ==============
document.addEventListener('DOMContentLoaded', init);
