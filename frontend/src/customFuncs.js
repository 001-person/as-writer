// 两个集合取交集
export function intersection(setA, setB) {

    let _intersection = new Set();
    for(let elem of setA) {
        if(setB.has(elem)) {
            _intersection.add(elem);
        }
    }
    return _intersection;
}

export function waitbookpathinit(bookpath) {
    return new Promise(resolve => {
      const check = () => {
        if (bookpath && bookpath !== '') {
          console.log("cus bookpath is:",bookpath);
          resolve(bookpath);
        } else {
          setTimeout(() => check(), 100); // 每隔100毫秒检查一次
          console.log('等待中。。')
          console.log('wait bookpath:',bookpath)
        }
      };
      check();
    });
  }

export function waitForPywebviewApi() {
    return new Promise(resolve => {
      const check = () => {
        if (typeof window.pywebview !== 'undefined' && typeof window.pywebview.api !== 'undefined') {
          resolve(window.pywebview.api);
        } else {
          setTimeout(() => check(), 100); // 每隔100毫秒检查一次
        }
      };
      check();
    });
  }

  // 模拟按下右箭头键
export function simulateKeyPress(editor, keyCode) {
  const event = new KeyboardEvent('keydown', {
    key: keyCode,
    code: keyCode,
    bubbles: true,
    cancelable: true,
    view: window
  });

  // 获取编辑器的内容区域
  const contentArea = editor.getContentAreaContainer();

  // 派发事件到编辑器的内容区域
  contentArea.dispatchEvent(event);
}