// 防止浏览器扩展消息通信错误的工具模块
// 解决 "Unchecked runtime.lastError: The message port closed before a response was received" 错误

/**
 * 浏览器扩展兼容性工具
 * 防止第三方扩展干扰应用正常运行
 */

// 监听并静默处理浏览器扩展相关的错误
function setupExtensionErrorSuppression() {
  // 监听 runtime.lastError 相关错误
  window.addEventListener('error', (event) => {
    const error = event.error;
    const message = event.message || '';
    
    // 检查是否是扩展相关的错误
    if (
      message.includes('runtime.lastError') ||
      message.includes('message port closed') ||
      message.includes('Extension context') ||
      (error && error.message && error.message.includes('runtime.lastError'))
    ) {
      console.warn('检测到浏览器扩展错误，已自动忽略:', message);
      event.preventDefault();
      return false;
    }
  }, true);
  
  // 监听未处理的 Promise 拒绝
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason;
    if (
      reason && 
      (
        reason.message?.includes('runtime.lastError') ||
        reason.message?.includes('message port closed') ||
        reason.toString().includes('Extension')
      )
    ) {
      console.warn('检测到扩展相关的Promise拒绝，已自动忽略:', reason);
      event.preventDefault();
      return false;
    }
  });
}

/**
 * 安全的消息通信包装器
 * 防止与浏览器扩展的消息冲突
 */
function safePostMessage(target, message, origin = '*') {
  try {
    if (target && typeof target.postMessage === 'function') {
      target.postMessage(message, origin);
    }
  } catch (error) {
    console.warn('消息发送失败（可能被扩展拦截）:', error.message);
  }
}

/**
 * 安全的事件监听器
 * 带有扩展错误保护
 */
function safeAddEventListener(target, event, handler, options) {
  const wrappedHandler = (e) => {
    try {
      return handler(e);
    } catch (error) {
      if (error.message?.includes('runtime.lastError') || 
          error.message?.includes('Extension')) {
        console.warn('事件处理器被扩展干扰，已忽略:', error.message);
        return;
      }
      throw error;
    }
  };
  
  target.addEventListener(event, wrappedHandler, options);
  
  // 返回清理函数
  return () => target.removeEventListener(event, wrappedHandler, options);
}

/**
 * iframe 安全通信
 * 防止扩展干扰 iframe 消息
 */
function safeIframeMessage(iframe, message, origin = '*') {
  if (!iframe || !iframe.contentWindow) {
    console.warn('iframe 不可用');
    return;
  }
  
  try {
    iframe.contentWindow.postMessage(message, origin);
  } catch (error) {
    console.warn('iframe 消息发送失败:', error.message);
  }
}

/**
 * 检查当前环境是否存在可能干扰的扩展
 */
function detectPotentialExtensionIssues() {
  const indicators = [];
  
  // 检查是否有常见的扩展全局变量
  if (window.chrome && window.chrome.runtime) {
    indicators.push('Chrome扩展环境');
  }
  
  if (window.browser && window.browser.runtime) {
    indicators.push('WebExtensions环境');
  }
  
  // 检查是否有修改过的原生方法
  if (window.postMessage.toString() !== 'function postMessage() { [native code] }') {
    indicators.push('postMessage已被修改');
  }
  
  if (indicators.length > 0) {
    console.info('检测到可能的扩展环境:', indicators.join(', '));
  }
  
  return indicators;
}

// 初始化扩展兼容性
function initExtensionCompatibility() {
  setupExtensionErrorSuppression();
  detectPotentialExtensionIssues();
  
  console.info('浏览器扩展兼容性保护已启用');
}

export {
  initExtensionCompatibility,
  safePostMessage,
  safeAddEventListener,
  safeIframeMessage,
  detectPotentialExtensionIssues
};

export default {
  init: initExtensionCompatibility,
  safePostMessage,
  safeAddEventListener,
  safeIframeMessage,
  detect: detectPotentialExtensionIssues
};