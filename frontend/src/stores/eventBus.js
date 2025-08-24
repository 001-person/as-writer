import { defineStore } from 'pinia'

// 不放在 state，避免响应式和序列化问题
const events = {}

export const useEventBusStore = defineStore('eventBus', {
  actions: {
    on(event, handler) {
      if (!events[event]) events[event] = []
      if (!events[event].includes(handler)) {
        events[event].push(handler)
      }
      // 返回解绑函数
      return () => this.off(event, handler)
    },
    emit(event, payload) {
      if (events[event]) {
        // 拷贝一份，防止执行过程中被修改
        events[event].slice().forEach(fn => fn(payload))
      }
    },
    off(event, handler) {
      if (events[event]) {
        events[event] = events[event].filter(fn => fn !== handler)
        if (events[event].length === 0) {
          delete events[event]
        }
      }
    }
  }
})
