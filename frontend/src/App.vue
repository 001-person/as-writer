<script>
import HelloWorld from './components/HelloWorld.vue'
import setting_view from './components/setting_view.vue';
import { useEventBusStore } from './stores/eventBus';
import { computed } from 'vue';
import { waitForPywebviewApi} from './customFuncs.js'


export default {
  components: {
    HelloWorld,
    setting_view,
  },
  data() {
    return {
      showConfirm: false,
      setting_collapse: true,
      menu_height:'auto',
      book_path: '',
      settings: null
    }
  },
  provide() {
    // Provide the book_path and settings to child components
    const base_config = {
      bookPath: this.book_path,
      Settings: this.settings
    };

    this.$watch(
      () => this.book_path,
      (newVal) => {
        base_config.bookPath = newVal;
      }
    );

    this.$watch(
      () => this.settings,
      (newVal) => {
        base_config.Settings = newVal;
      }
    );

      return {base_config};
  },

  async mounted() {
    this.menu_height = document.getElementById("menu_view").offsetHeight + "px";
    document.getElementById("menu_view").style.height = this.menu_height;

    await waitForPywebviewApi();
    await this.init_config();
    console.log("moutapp book_path is:");
    console.log(this.book_path);

    // 监听浏览器关闭事件（右上角叉号）
    window.addEventListener("beforeunload", (e) => {
      // 弹出确认对话框
      e.preventDefault();
      this.tryExit();
      // Chrome 兼容性需要设置 returnValue
      e.returnValue = '';
    });

    // 事件总线初始化
    const eventBus = useEventBusStore();
    eventBus.on('select_book_path', this.sel_book_path);
    eventBus.on('exitApp', this.tryExit);
  },

  beforeUnmount() {
    // 清理事件总线监听
    const eventBus = useEventBusStore();
    eventBus.off('select_book_path', this.sel_book_path);
    eventBus.off('exitApp', this.tryExit);
  },

  methods: {

    sel_book_path(path) {
      this.book_path = path;
      console.log("选择的书籍路径为：", this.book_path);
    },
    menu_collapse() {
      
      var element = document.getElementById("menu_view");
      if (element.style.height === "0px") {
        element.style.height = this.menu_height;
        element.style.marginBottom = "10px";

      } else {
        element.style.height = "0px";
        element.style.marginBottom = "0px";
      }

    },

    async init_config() {
      
      console.log("初始化配置");
      const config = await window.pywebview.api.get_bookConfig();
      if (config) {
        this.book_path = config.path || '';
        this.settings = config.current_setting || null;
      } else {
        console.error("Failed to load book configuration.");
      }

    },

    tryExit() {
      this.showConfirm = true;
    },

    async confirmExit() {
      this.showConfirm = false;
      if (window.pywebview?.api?.exit_app) {
        await window.pywebview.api.exit_app();
      }
    },
  }

}
</script>


<template>
  <div id="app">
    <div @click="menu_collapse" style="height: 10px; "></div>
    <div class="setting">
      <!-- <div @click="menu_collapse" style="height: 10px; background-color: var(--color-background-bottom-layer);"></div> -->
      <setting_view id="menu_view"/>
    </div>
    <HelloWorld class="hello" />

    <!-- 确认对话框 -->
    <el-dialog
      v-model="showConfirm"
      title="提示"
      width="30%"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <span>请确保当前工作已保存，确定退出应用吗？</span>
      <template #footer>
        <el-button @click="showConfirm = false">取消</el-button>
        <el-button type="primary" @click="confirmExit">确定</el-button>
      </template>
    </el-dialog>


  </div>
</template>

<style scoped>

#app {
  position: relative;
  padding: 0px 10px 10px 10px;
  box-sizing: border-box;
  height: 100vh;
  background-color: var(--color-background-bottom-layer);
  display: flex;
  flex-direction: column;

}


.setting {
  
  background-color: var(--color-background-header);
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
}

#menu_view {
  transition: height 0.5s ease;
  margin-bottom: 10px;
}

.hello {
  
  flex: 1 1 auto;
  
  min-height: 0;
  background-color: var(--color-background-mainview);
}
</style>
