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
      setting_collapse: true,
      menu_height:'auto',
      book_path: '',
      settings: null
    }
  },
  provide() {
    // Provide the book_path and settings to child components
    return {
      bookPath: computed(() => this.book_path),
      Settings: computed(() => this.settings),
    };
  },

  async mounted() {
    this.menu_height = document.getElementById("menu_view").offsetHeight + "px";
    document.getElementById("menu_view").style.height = this.menu_height;

    await waitForPywebviewApi();
    await this.init_config();
    console.log("moutapp book_path is:");
    console.log(this.book_path);

    // 事件总线初始化
    const eventBus = useEventBusStore();
    eventBus.on('select_book_path', this.sel_book_path);
     
  },

  beforeUnmount() {
    // 清理事件总线监听
    const eventBus = useEventBusStore();
    eventBus.off('select_book_path', this.sel_book_path);
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
