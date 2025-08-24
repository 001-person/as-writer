import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { createPinia } from 'pinia' 
import router from './router'

// 设置默认主题
document.documentElement.setAttribute('data-theme', 'light');

const app = createApp(App)
app.use(createPinia())
app.use(router)

app.use(ElementPlus)
// 图标库 ElementPlus
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(`ele-${key}`, component)
}

import './assets/theme.css'
app.mount('#app')
