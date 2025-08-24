// src/router/index.js
import { createRouter, createWebHashHistory } from 'vue-router'
import WritePage from '../components/write_view.vue'
import WriteShelf from '../components/write_shelf.vue'

// 2. 创建 router 实例
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    // { path: '/read-page', component: ReadPage },
    { path: '/write-page/:book_id/:book_name/:last_node', name: 'writePage', component: WritePage },
    { path:'/', name: 'writeShelf', component: WriteShelf },
    //{ path:'/', name: 'dataStatistics', component: DataStatistics },
  ],
});

export default router
