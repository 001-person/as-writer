<template>
  <div class="top" ref="dev0">
    <div class="resizeable" :style="{ width: divWidth[0] + 'px'}" id='dev1'>
      <left_area 
        :catalog_data="catalog_data" 
        :book_path="bookpath" 
        :book_name="bookname" 
        :book_id="book_id"
        class="left"/>
    </div>
    <div class="resize-handle" @mousedown="startResize1" ></div>
    <div class="resizeable" :style="{ width: divWidth[1] + 'px' }" id='dev2'>
      
      <!-- 使用tinymce富文本编辑器替换了 textarea元素 -->
      <textarea ref="textarea" v-model="novelContent" placeholder="开始写作..."  id="text-area"></textarea>
      
    </div>
    <div class="resize-handle" @mousedown="startResize2"></div>
      <div class="resizeable" :style="{ width: divWidth[2] + 'px' }" id='dev3'>
        <div class="data-area">


          <div class="data-item">
            <div class="data-label">本章字数:</div><div class="data-value">{{words_count}}</div>
          </div>
          <div class="data-item">
            <div class="data-label">本书总字数:</div><div class="data-value">{{total_words_count_toString}}</div>
          </div>
          <div class="data-item">
            <div class="data-label">本次码字数:</div><div class="data-value">{{this_time_count}}</div>
          </div>
          <div class="data-item">
            <div class="data-label">码字速度:</div><div class="data-value">{{write_rate}}</div>
          </div>
          <div class="data-item">
            <div class="data-label">创作总天数:</div><div class="data-value">{{cost_days}}</div>
          </div>




        </div>
        <div class="plugin-area">
        </div>
      </div>

      <!-- 弹出框 书签名称-->
      <el-dialog
        v-model="get_markname"
        title="书签名称"
        :style="{ minWidth: '300px', maxWidth: '500px' }"
        align-center
        center
      >
      <el-input
        v-model="markname"
        placeholder="Please input"
        clearable
      />
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="get_markname = false">取消</el-button>
            <el-button type="primary" @click="add_mark">
              确认
            </el-button>
          </div>
        </template>
      </el-dialog>
</div>
</template>

<script>
import left_area from './left_area.vue';
import { useEventBusStore } from '../stores/eventBus';
import tinymce from 'tinymce';
import { reactive } from 'vue';
import { waitForPywebviewApi, simulateKeyPress} from '../customFuncs.js'
import '../tinymce-custom-plugins/custom_mark.js'



export default {
  name: 'write-page',
  components:{
    left_area
  },

  inject: ['startTime', 'startData', 'base_config'],

  data() {
    return {

      editor:null,
      novelContent: '', // 小说内容绑定的数据
      timer_cal:null, // 定时器
      timer_save:null, // 定时器
      words_count:0,
      total_words_count:0,
      total_words_count_toString:'0',
      this_time_count:0,
      write_rate:'0 字/小时',
      cost_days:0,
      book_id:'-1',
      bookname:'西游记',
      chapters:[
        // {
        //   id:'1_1',
        //   content:'',
        // },
      ],
      catalog_data:[
        {
          id:'0',
          label:this.bookname,
          children:[]
        },
      ], // 目录
      bookpath:this.base_config.bookPath,
      
      export_type:'txt',
      current_id:'0', //当前选中的章节id
      divWidth: [50, 100, 50], // 初始宽度
      isResizing: false,
      index: 1,
      update_chapters:[], //内容有修改的章节的id

      get_markname:false, // 获取书签名称
      markname:'',
      jumpmark_id:'', //跳转书签id

      // tinymce初始化
      textarea_init:{
        selector:"textarea#text-area",
        license_key: 'gpl', // 使用GPL许可
        
        init_instance_callback: this.onEditorInit,
        statusbar:false,
        menubar:false,
        toolbar_mode: 'sliding',
        toolbar:" fontfamily fontsize forecolor lineheight | copy paste pastetext | selectall backcolor strikethrough indent outdent removeformat",
        plugins: 'customContextMenu custom_mark',
        contextmenu: "paste | cut | copy | saveItem | saveAll | export | bookmark",
        contextmenu_never_use_native: true,
        language:"zh_CN",
        // skin:'oxide-dark',
        // content_css: 'dark',
        width:"100%",
        height:"100%",
        valid_elements: '*[*]', // 允许insertContent函数插入所有元素及其所有属性
        
        setup:editor => {
          this.editor = editor;
          // 保存 Vue 实例的 this 上下文到编辑器实例
          editor.vueInstance = this;
          editor.on('mousemove', (e) =>{
            const editorContainerRect = this.editor.getContainer().getBoundingClientRect();
            let event = {
              clientX: e.clientX + editorContainerRect.left
            }
            this.handleMouseMove(event);

          });

          editor.on('mouseup', (e) =>{
            this.isResizing = false;
          });


          editor.on('click', function(e) {
            const eventBus = useEventBusStore();
            eventBus.emit('click:textarea', e);
          });

          editor.on('init',()=>{
            this.editor.setContent(this.novelContent);

            // 去除四边圆角
            const editorContainer = editor.editorContainer;
            editorContainer.style.borderRadius = '0';
            
          });
          
          // 监听内容变化
          editor.on('input',()=>{
            this.novelContent = this.editor.getContent();
            console.log("addmark是：");
            console.log(this.novelContent);
          });

          // 快捷键
          editor.on('keydown', (e) =>{
            if(e.ctrlKey && e.altKey && e.keyCode == 83){
              // Ctrl+Alt+S 保存当前章节
              e.preventDefault();
              this.save_current_chapter();
              
            } else if(e.ctrlKey && e.keyCode == 83){
              // Ctrl+S 保存全部修改
              e.preventDefault();
              this.save_all();
              
            } else if(e.ctrlKey && e.keyCode == 84){
              // Ctrl+T 导出txt文件
              e.preventDefault();
              this.export_txt();
            } else if(e.ctrlKey && e.keyCode == 69){
              // Ctrl+E 导出EPUB文件
              e.preventDefault();
              this.export_epub();
            } else if(e.ctrlKey && e.keyCode == 77){
              // Ctrl+M 添加书签
              e.preventDefault();
              if (this.current_id.includes('_')){
                  this.get_markname = true;
                }
            } else if(e.ctrlKey && e.altKey && e.keyCode == 78){
              // Ctrl+Alt+N 新建卷
              e.preventDefault();
              const eventBus = useEventBusStore();
              eventBus.emit('newVolume');

            } else if(e.ctrlKey && e.keyCode == 78){
              // Ctrl+N 新建章节
              e.preventDefault();
              const eventBus = useEventBusStore();
              eventBus.emit('newChapter');

            }  else if(e.keyCode === 9){ // Tab键增加缩进
              e.preventDefault();  // 阻止默认行为
              if (e.shiftKey) {
                editor.execCommand('Outdent');  // 按住Shift键时执行减少缩进
              } else {
                editor.execCommand('Indent');  // 否则执行缩进
              }
            }
          });

          // 禁止默认快捷键
          editor.on('keydown', function (e) {
            // 允许的快捷键列表：Ctrl+C (复制), Ctrl+V (粘贴), Ctrl+A (全选)
            const allowedKeys = ['c', 'v', 'a'];
            if (e.ctrlKey || e.metaKey) {
              const key = String.fromCharCode(e.keyCode).toLowerCase();
              if (!allowedKeys.includes(key)) {
                e.preventDefault();
                e.stopPropagation();
              }
            }
          });

          
          // 右键菜单
          tinymce.PluginManager.add('customContextMenu', (editor) =>{
              // 注册自定义菜单项
              //保存本章
              //console.log("注册自定义菜单项!")
              editor.ui.registry.addMenuItem('saveItem', {
                text: '保存',
                icon: 'save',
                shortcut: 'Ctrl+Alt+S',
                onAction: () => {
                  this.save_current_chapter();
                }
              });

              //保存全部
              editor.ui.registry.addMenuItem('saveAll', {
                text: '保存全部',
                icon: 'save',
                shortcut: 'Ctrl+S',
                onAction: () => {
                  this.save_all();
                }
              });


              // 导出，子项
              editor.ui.registry.addMenuItem('exportText', {
                text: '导出TXT',
                shortcut: 'Ctrl+T',
                onAction: () => {
                  this.export_txt();
                }
              });

              editor.ui.registry.addMenuItem('exportEpub', {
                text: '导出EPUB',
                shortcut: 'Ctrl+E',
                onAction: () => {
                  this.export_epub();
                }
              });

              // 导出，父项
              editor.ui.registry.addMenuItem('export', {
                text: '导出',
                type: 'menuitem',  // 注意类型必须是'menuitem'，不是'menu'
                icon: 'export',  // 可选的图标
                getSubmenuItems: () => {  // 返回一个函数，这个函数返回子菜单项
                  return [
                    'exportText',
                    'exportEpub',
                  ];
                }
              });
            // 书签
            editor.ui.registry.addMenuItem('bookmark', {
              text: '书签',
              icon: 'bookmark',
              shortcut: 'Ctrl+M',
              onAction: () => {
                console.log('书签!');
                if (this.current_id.includes('_')){
                  this.get_markname = true;
                }
                
              }
            });

            // 注册右键菜单
            editor.ui.registry.addContextMenu('cut', {
              

              update: () => {
                // 获取当前选区
                const selection = editor.selection;
                // 如果选区是空的，不显示
                if (!selection.getContent()) {
                  return '';
                }

                // 如果选区非空，显示菜单项
                return 'cut';
              }


            });

            editor.ui.registry.addContextMenu('copy', {
              

              update: () => {
                // 获取当前选区
                const selection = editor.selection;
                // 如果选区是空的，不显示
                if (!selection.getContent()) {
                  return '';
                }

                // 如果选区非空，显示菜单项
                return 'copy';
              }


            });

            editor.ui.registry.addContextMenu('saveItem', {
              

              update: () => {
                // 获取当前选区
                const selection = editor.selection;
                // 如果选区是空的，返回菜单项的标识符，让它显示
                if (!selection.getContent()) {
                  return 'saveItem';
                }

                // 如果选区非空，返回空字符串，隐藏菜单项
                return '';
              }


            });

            editor.ui.registry.addContextMenu('saveAll', {
              

              update: () => {
                // 获取当前选区
                const selection = editor.selection;
                // 如果选区是空的，返回菜单项的标识符，让它显示
                if (!selection.getContent()) {
                  return 'saveAll';
                }

                // 如果选区非空，返回空字符串，隐藏菜单项
                return '';
              }


            });


            editor.ui.registry.addContextMenu('export', {
              update: () => {
                // 获取当前选区
                const selection = editor.selection;

                // 如果选区是空的，返回菜单项的标识符，让它显示
                if (!selection.getContent()) {
                  return 'export';
                }

                // 如果选区非空，返回空字符串，隐藏菜单项
                return '';
              }

            });

            editor.ui.registry.addContextMenu('bookmark', {

              update: () => {
                // 获取当前选区
                const selection = editor.selection;

                // 如果选区是空的，返回菜单项的标识符，让它显示
                if (!selection.getContent()) {
                  return 'bookmark';
                }

                // 如果选区非空，返回空字符串，隐藏菜单项
                return '';
              }

            });

          

            
          });
          
      
        },


      },




    };
  },

  created() {
    // 
    this.book_id = String(this.$route.params.book_id);
    this.bookname = this.$route.params.book_name;
    //初始界面显示书名
    //this.novelContent = this.bookname;
    console.log("book_id:");
    console.log(this.book_id);
    console.log("book_name:");
    console.log(this.bookname);


  },

  beforeUnmount() {
    // 清理事件总线监听
    const eventBus = useEventBusStore();
    eventBus.off('update:current_node_key', this.up_current_node_key);
    eventBus.off('update:new_chapter', this.new_chapter);
    eventBus.off('update:new_volume', this.new_volume);
    eventBus.off('update:delete_chapter', this.delete_chapter);
    eventBus.off('update:delete_volume', this.delete_volume);
    eventBus.off('update:rename_node', this.rename_node);
    eventBus.off('remove_mark', this.remove_mark);
    eventBus.off('jump_to_mark', this.jumpto_mark);

  },

  async mounted() {

    // 等待 pywebview 初始化完成
    await waitForPywebviewApi();
    this.bookpath = this.base_config.bookPath;
    this.$nextTick(() => {
      // 在 $nextTick 中获取宽度确保在 DOM 更新之后
      this.handleResize();

      
      // 初始化tinymce
      tinymce.remove();
      if (!this.editor){
        
        tinymce.init(this.textarea_init);
        this.editor = tinymce.get('text-area');

      }

    });

    await this.loadBook();
    
    // 显示天数
    this.showCostDays();
    // console.log('开始总字数为：');
    // console.log(this.startData);
    // console.log('mounted总字数为：');
    // console.log(this.total_words_count);
    // 更新书名
    if (this.bookname !== this.catalog_data[0].label){
      this.catalog_data[0].label = this.bookname;
      this.saveCatalog();
    }

    // 恢复上次写作位置
    if (this.$route.params.last_node === '0'){
        this.novelContent = this.bookname;
      } else {
        const eventBus = useEventBusStore();
        eventBus.emit('set-last-node-id', this.$route.params.last_node);
      }

    // 组件挂载后启动定时器
    this.startCalculateTask();
    this.startSaveTask();

    const eventBus = useEventBusStore();
    // 点击其他节点时，更新当前节点和显示区内容
    eventBus.on('update:current_node_key', this.up_current_node_key);

    eventBus.on('update:new_chapter', this.new_chapter);

    eventBus.on('update:new_volume', this.new_volume);

    eventBus.on('update:delete_chapter', this.delete_chapter);

    eventBus.on('update:delete_volume', this.delete_volume);

    eventBus.on('update:rename_node', this.rename_node);

    eventBus.on('remove_mark', this.remove_mark);

    eventBus.on('jump_to_mark', this.jumpto_mark);

    

    //this.load_catalog();
    document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    document.addEventListener('mouseup', this.stopResize);
    window.addEventListener('resize', this.handleResize);

    
  },

  beforeRouteLeave(to, from, next) {
    // 保存书籍信息
    this.save_all();
    this.novelContent = this.editor.getContent();
    this.count_total_words();
    let bookdata = [this.book_id, this.total_words_count, this.current_id];
    const eventBus = useEventBusStore();
    eventBus.emit('save-book-info',bookdata);
    // 销毁tinyMCE编辑器
    if (this.editor) {
      this.editor.remove();
      this.editor = null;
      this.novelContent = '';
      // console.log("beforeRouteLeave tinyMCE destroy is:");
      // console.log(this.editor);
    }
    // 清除定时器
    this.stopCalculateTask();
    this.stopSaveTask();
    next(); // 确保调用next()来继续导航
  },
  beforeDestroy() {

    // 保存书籍信息
    this.save_all();
    this.novelContent = this.editor.getContent();
    this.count_total_words();
    let bookdata = [this.book_id, this.total_words_count, this.current_id];
    const eventBus = useEventBusStore();
    eventBus.emit('save-book-info',bookdata);

    // 在组件销毁之前移除事件监听器
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('mouseup', this.stopResize);
    window.removeEventListener('resize', this.handleResize);
    console.log("组件已销毁")

    // 销毁tinyMCE编辑器
    if (this.editor) {
      this.editor.remove();
      this.editor = null;
      this.novelContent = '';

    }

    // 清除定时器
    this.stopCalculateTask();
    this.stopSaveTask();
    
  },

  
  watch: {

      // 监听novelContent的变化
      novelContent(newValue, oldValue) {
        // 下次点击保存按钮应该更新后台内容的章节
        if (this.current_id.includes('_') && (!this.update_chapters.includes(this.current_id))){
          this.update_chapters.push(this.current_id);
          console.log("update update_chapters is:");
          console.log(this.update_chapters)

        }

        
        // 将新的内容同步到编辑器
        if (this.editor && this.editor.selection &&newValue !== this.editor.getContent()){
          console.log("newValue is:");
          console.log(newValue);
          this.editor.setContent(newValue);

          if (this.jumpmark_id !== ''){
            this.jump_to_mark();
          } else {
            // 光标移到文本末尾
            this.editor.focus();
            this.editor.selection.select(this.editor.getBody(), true); // 插入空字符以确保光标移动到末尾
            this.editor.selection.collapse(false); // 设置光标位置
          }
      }
      // 计算字数
      this.count_words();
      
      }
    },

  methods: {

      up_current_node_key(keys){
        this.load_content(keys[0], keys[1]);
        this.current_id = keys[0];
      },

      startResize1(event) {
        if (event.button === 0) {
        //console.log('按下了:',1)
        this.isResizing = true;
        this.index = 1;

        }
      },

      startResize2(event) {
        if (event.button === 0) {
        //console.log('按下了:',0)
        this.isResizing = true;
        this.index = 0;
        }
      },

      handleMouseMove(event) {
      //console.log('坐标：',event.clientX,event.clientY)
      if (this.isResizing) {

        const topWidth = this.$refs.dev0.offsetWidth;
        if(event.clientX >= 0 && event.clientX <= topWidth){
          if(this.index){

              this.divWidth[0] = event.clientX
              this.divWidth[1] = topWidth - event.clientX - this.divWidth[2] - 6
              //console.log('左边')
              
            }else{

              this.divWidth[2] = topWidth - event.clientX
              this.divWidth[1] = event.clientX - this.divWidth[0] - 3
              //console.log('右边')
            }
        }
      }
    },

      stopResize() {

        this.isResizing = false;
      },

      // 窗口大小变化时，三个分区比例恢复默认值
      handleResize() {
      // 获取 div 宽度
      const myDiv = this.$refs.dev0;

      if (myDiv) {
        const topWidth = myDiv.offsetWidth;
        this.divWidth = [Math.floor(topWidth*0.2), topWidth-2*Math.floor(topWidth*0.2)-6, Math.floor(topWidth*0.2)];
        //console.log('Div Width:', this.divWidth);
      }
      
      
    },

    onEditorInit(){

      // 计算字数
      // this.count_words();
      // this.count_total_words();
      
      console.log('editor初始化完成了a!');

    },

    showCostDays() {
      let index1 = this.startData.findIndex(item => item.id === this.book_id);
      if (index1 !== -1){
        if (this.startData[index1].book_status === '写作中'){
          this.cost_days = Math.floor((new Date() - new Date(this.startData[index1].book_create_time)) / (1000 * 60 * 60 * 24));
          
        } else {
          this.cost_days = Math.floor((new Date(this.startData[index1].book_finish_time) - new Date(this.startData[index1].book_create_time)) / (1000 * 60 * 60 * 24));
        }
      }
      
    },

    // 定时器任务
    calculateTask() {   
      this.calculate_rate(); 
    },
    // 启动定时器
    startCalculateTask() {
      this.timer_cal = setInterval(this.calculateTask, 1 * 60 * 1000); // 每1分钟执行一次
    },
    // 清除定时器
    stopCalculateTask() {
      console.log("清除cal定时器");
      console.log(this.timer_cal);
      if (this.timer_cal !== null) {
        
        clearInterval(this.timer_cal);
        this.timer_cal = null;
      }
    },


    calculate_rate(){
      // 先计算当前总字数和本次码字数
      this.count_total_words();
      let index1 = this.startData.findIndex(item => item.id === this.book_id);
      if (index1 !== -1){
        // 计算本次码字数
        this.this_time_count = this.total_words_count - Number(this.startData[index1].total_words);

      }

      let index = this.startTime.findIndex(item => item.id === this.book_id);
      if (index !== -1){
        //console.log("更新了数据！")
        let now_time = new Date();
        let write_time = this.startTime[index].start_time;
        // 计算时间差（毫秒）
        let timeDifferenceInMilliseconds = Math.abs(now_time.getTime() - write_time.getTime());
        if (timeDifferenceInMilliseconds < 2000){
          this.write_rate = '0 字/小时';

        } else{
          // 转换为小时
          let timeDifferenceInHours = timeDifferenceInMilliseconds / (1000 * 60 * 60);

          // 计算码字速度并取整
          this.write_rate = Math.floor(this.this_time_count / timeDifferenceInHours);
          this.write_rate = this.write_rate + ' ' + '字/小时';
        }
      }
      
    },


    count_total_words(){
      
      
      this.total_words_count = 0;
      // console.log("current_id is:");
      // console.log(this.current_id);
      // console.log("chapters is:");
      // console.log(this.chapters);
      
      if (this.current_id.includes('_')){
        //更新chapters
        let index = this.chapters.findIndex(item => item.id === this.current_id);
        if (index !== -1){
          this.chapters[index].content = this.novelContent;
        }
        
        //console.log("确实");
        }
      
      for(let item of this.chapters) {
        // console.log("count内容是：")
        // console.log(item.content);
        // 统计汉字
        this.total_words_count += item.content.replace(/[^\u4e00-\u9fa5]/g, '').length;
        
          
      }


      // console.log('当前总字数为：');
      
      // console.log(this.total_words_count);
      let word_count = String(this.total_words_count);
      
      if (word_count.length > 5){
        // 字数过十万后，显示单位万，省略小数位
        word_count = word_count.slice(0,-4) + " 万";
      } else if (word_count.length > 4){
        // 字数过万后，显示单位万,保留一位小数
        word_count = word_count.slice(0,-4) + '.' + word_count.slice(-4,-3) + " 万";
      }
      
      this.total_words_count_toString = word_count;


    },
    count_words(){
      let hanziCount = this.novelContent.replace(/[^\u4e00-\u9fa5]/g, '').length;
      this.words_count = hanziCount;

    },

    async loadBook(){
      let book_index = [this.bookpath, this.book_id];
      try {
        // 等待Promise完成，并捕获可能出现的错误
        const res = await window.pywebview.api.loadBook(book_index);
        console.log("loadBook res is:");
        console.log(res);
        
        if (res){
          this.catalog_data = res[0];
          this.chapters = res[1];
          this.calculate_rate();
          
        } else{
          this.$message({
              message: '加载失败!',
              type: 'error'
            });
        }
      } catch (error) {
        // 处理错误
        this.$message({
              message: '程序异常!',
              type: 'error'
            });
      }

    },

    saveChapter(id){
        let index = this.chapters.findIndex(item => item.id === id);
        let chapter_data = [this.bookpath, this.book_id, id, this.chapters[index].content];
      return  window.pywebview.api.saveChapter(chapter_data).then(res => {
          
          if (res === 1){
            // 保存过的章节从更新列表中删除
            let index = this.update_chapters.indexOf(id);
            if (index !== -1) {
              this.update_chapters.splice(index, 1);
              console.log("save update_chapters is:");
              console.log(this.update_chapters)
              }
          }
          return res;
        }).catch(error => {
          throw error;
        })

    },

    saveCatalog(){
      let catalog = [this.bookpath, this.book_id, this.catalog_data];
      return window.pywebview.api.saveCatalog(catalog).then(res => {
          return res;
        }).catch(error => {
          throw error;
        })
    },

    async save_current_chapter(){

      try {
        if (this.current_id.includes('_')){
          // 先更新当前章节内容到chapters
          this.novelContent = this.editor.getContent();
          let index = this.chapters.findIndex(item => item.id === this.current_id);
          this.chapters[index].content = this.novelContent;
          const [res1, res2] = await Promise.all([this.saveCatalog(), this.saveChapter(this.current_id)]);
          // 在这里处理函数A和B的结果
          if (res1 === 1 && res2 === 1){
            this.$message({
              message: '当前章节保存成功!',
              type: 'success'
            });
          }else{
            this.$message({
              message: '保存失败!',
              type: 'error'
            });
          }
        }

      } catch (error) {
          // 如果任何一个函数调用失败，这里可以处理错误
          this.$message({
              message: '保存失败!',
              type: 'error'
            });
      }

    },


    // 定时器任务
    saveTask() {
      // 保存书籍
      this.save_all();
      console.log("保存了一次！");
    },
    // 启动定时器
    startSaveTask() {
      this.timer_save = setInterval(this.saveTask, 10 * 60 * 1000); // 每10分钟执行一次
    },
    // 清除定时器
    stopSaveTask() {
      console.log("清除save定时器");
      console.log(this.timer_save);
      if (this.timer_save !== null) {
        
        clearInterval(this.timer_save);
        this.timer_save = null;
      }
    },

    async save_all(){

      // 先更新当前章节内容到chapters
      if (this.current_id.includes('_')){
        this.novelContent = this.editor.getContent();
        let index = this.chapters.findIndex(item => item.id === this.current_id);
        this.chapters[index].content = this.novelContent;
      }
      // this.novelContent = this.editor.getContent();
      // this.chapters[this.current_id] = this.novelContent;
      // 所有保存操作添加到promises中
      const promises = this.update_chapters.map(chapter => this.saveChapter(chapter));
      promises.push(this.saveCatalog());
      try {
        const results = await Promise.all(promises);
        // 所有保存操作完成后，这里处理所有结果
        let is_success = true;
        for (let i = 0; i < results.length; i++) {
          if (results[i] === 0) {
            // 如果某个保存操作失败，弹出错误提示框
            this.$message({
              message: '保存失败!',
              type: 'error'
            });
            is_success = false;
            break;
          }
        } 
          // 如果接收到的所有参数都不为0，提示保存成功
          if (is_success){
            this.$message({
              message: '全部保存成功!',
              type: 'success',
              duration: 1500
            });
          }
      } catch (error) {
        // 如果有任何一个保存操作失败，这里处理错误
        this.$message({
              message: '保存失败!',
              type: 'error'
            });
      }

    },



    //  点击导出TXT选项后，弹出一个路径先择对话框，选择路径后，进行导出操作
    export_txt(){
      const bookdata = [this.bookpath, this.book_id, this.bookname];
      window.pywebview.api.exportTxt(bookdata).then(res => {
          if (res === 1){
            this.$message({
              message: '导出成功!',
              type: 'success'
            });
          } else if (res === 0){
            this.$message({
              message: '导出失败!',
              type: 'error'
            });
          }
        }).catch(error => {
          throw error;
        })
      

    },

    export_epub(){

      const bookdata = [this.bookpath, this.book_id, this.bookname];
      window.pywebview.api.exportEpub(bookdata).then(res => {
          if (res === 1){
            this.$message({
              message: '导出成功!',
              type: 'success'
            });
          } else if (res === 0){
            this.$message({
              message: '导出失败!',
              type: 'error'
            });
          }
        }).catch(error => {
          throw error;
        })

    },


    
    load_content(current_key, old_key){

      // 保存旧内容
      if (old_key.includes('_')){

        //更新chapters
        let index1 = this.chapters.findIndex(item => item.id === old_key);
        if (index1 !== -1){
          this.chapters[index1].content = this.novelContent;
        }

      }
      // 加载新内容
      if (current_key === '0'){
        this.novelContent = this.bookname;
      } else if (!current_key.includes('_')){

        const index = this.catalog_data[0].children.findIndex(volume => volume.id === current_key);
        if (index !== -1){
          this.novelContent = this.catalog_data[0].children[index].label;
        }

        
      } else{

        // 更新novelContent
        let index2 = this.chapters.findIndex(item => item.id === current_key);
        // console.log('切换了内容！');
        // console.log(current_key);
        // console.log(index2);
        // console.log(this.chapters[index2]);
        if (index2 !== -1){
          this.novelContent = this.chapters[index2].content;
        }
        

      }

    },

    new_chapter(new_id){

      const vol_id = new_id.split('_')[0];

      // 更新catalog_data
      // 能找到卷id，直接创建章
      let index = this.catalog_data[0].children.findIndex(volume => volume.id === vol_id);
      if (index !== -1){
        this.catalog_data[0].children[index].children.push({
          id: new_id,
          label:'新建章',
        });
        
      } else{
        // 找不到卷id，先创建卷，再创建章
        this.catalog_data[0].children.push({
          id: vol_id,
          label:'新建卷',
          children: [{
            id: new_id,
            label:'新建章',
          }]
        });
      }
      // 更新chapters
      this.chapters.push({id: new_id, content: ''});
      this.update_chapters.push(new_id);
      console.log("add update_chapters is:");
      console.log(this.update_chapters)
    },

    new_volume(new_id){

      this.catalog_data[0].children.push({
        id: new_id,
        label:'新建卷',
        children: []
      });

    },

    delete_ch(delete_id){
      let chapter_index =[this.bookpath, this.book_id, delete_id];
      return window.pywebview.api.deleteChapter(chapter_index).then(res => {

        if (res === 1){
            // 删除的章节从更新列表中删除
            let index = this.update_chapters.indexOf(delete_id);
            if (index !== -1) {
              this.update_chapters.splice(index, 1);
              console.log("delete update_chapters is:");
              console.log(this.update_chapters)
              }

            
          }
          return res;
        }).catch(error => {
          throw error;
        })

    },

    async delete_chapter(delete_id){
      const vol_id = delete_id.split('_')[0];

      let index = this.catalog_data[0].children.findIndex(volume => volume.id === vol_id);
      if (index !== -1){
        this.catalog_data[0].children[index].children = this.catalog_data[0].children[index].children.filter(chapter => chapter.id !== delete_id);
        let index2 = this.chapters.findIndex(item => item.id === delete_id);
        if (index2 !== -1){
          this.chapters.splice(index2, 1);
        }
        
        // console.log("delete删掉的是：");
        
        // console.log(this.chapters);
        
        const [res1, res2] = await Promise.all([this.delete_ch(delete_id), this.saveCatalog()]);
        if (res1 === 1 && res2 === 1){
          this.$message({
            message: '已删除!',
            type: 'success'
          });
        }else{
          this.$message({
            message: '删除失败!',
            type: 'error'
          });
        }

      }

    },

    async delete_volume(delete_id){

      let index = this.catalog_data[0].children.findIndex(volume => volume.id === delete_id);
      if (index !== -1){
        // 删除该volume下的所有章节
        const promises = []
        this.catalog_data[0].children[index].children.forEach(chapter => {
          let chapter_index = this.chapters.findIndex(item => item.id === chapter.id);
          if (chapter_index !== -1){
            this.chapters.splice(chapter_index, 1);
          }
          promises.push(this.delete_ch(chapter.id));

        });
        try {
          const results = await Promise.all(promises);
          // 所有删除操作完成后，这里处理所有结果
          let is_success = true;
          for (let i = 0; i < results.length; i++) {
            if (results[i] === 0) {
              // 如果某个删除操作失败，弹出错误提示框
              this.$message({
                message: '删除失败!',
                type: 'error'
              });
              is_success = false;
              break;
            }
          } 
            // 如果接收到的所有参数都不为0，提示删除成功
            if (is_success){
              this.$message({
                message: '删除成功!',
                type: 'success'
              });
            }
        } catch (error) {
          // 如果有任何一个删除操作失败，这里处理错误
          this.$message({
                message: '删除失败!',
                type: 'error'
              });
        }

        // 删除volume
        this.catalog_data[0].children.splice(index, 1);
        this.saveCatalog();

        
      }
    },


    rename_node(data){

      if (data[0] === '0'){
        // 修改书名
        this.bookname = data[1];
        this.catalog_data[0].label = data[1];
      }else if (!data[0].includes('_')){
        // 修改卷名
        let index = this.catalog_data[0].children.findIndex(volume => volume.id === data[0]);
        if (index !== -1){
          this.catalog_data[0].children[index].label = data[1];
        }
      } else {
        // 修改章名
        let vol_id = data[0].split('_')[0];
        let index = this.catalog_data[0].children.findIndex(volume => volume.id === vol_id);
        if (index !== -1){
          let index2 = this.catalog_data[0].children[index].children.findIndex(chapter => chapter.id === data[0]);
          if (index2 !== -1){
            this.catalog_data[0].children[index].children[index2].label = data[1];
          }
        }
      }


      },

    add_mark(){
      this.get_markname = false;
      const markid = 'mark' + Date.now();
      let mark_data = [this.current_id, markid, this.markname];
      this.editor.myPlugin.insertMark(markid);
      let index = this.chapters.findIndex(item => item.id === this.current_id);
      if (index !== -1){
        this.chapters[index].content = this.editor.getContent();
      }
      const eventBus = useEventBusStore();
      eventBus.emit('add_mark', mark_data);
      
    },
    jumpto_mark(markid){
      this.jumpmark_id = markid;
      this.jump_to_mark();
    },

    jump_to_mark(){
      let chapter_id = this.jumpmark_id.split('-')[0];
      if (chapter_id !== this.current_id){
        return;
      }
      let mark_id =  this.jumpmark_id.split('-')[1];

      const subElement = this.editor.dom.get(mark_id);

      if (subElement) {
        console.log(`jump_to_mark:${mark_id}`);
        // 创建一个 Range 对象
        const rng = this.editor.dom.createRng();

        // 将 Range 设置在 <sub> 标签之后
        rng.setStartAfter(subElement);
        rng.setEndAfter(subElement);

        // 将这个 Range 应用于当前选择（移动光标）
        this.editor.selection.setRng(rng);

        // 确保光标折叠在 Range 的结束位置（即在 <sub> 标签之后）
        this.editor.selection.collapse(false);
        // 插入空字符,使光标跳出sub 标签
        const mark2 = `<span class="text">&#8203;</span>`;
        this.editor.insertContent(mark2);
        this.editor.focus();
        this.jumpmark_id = '';

      }


    },

    remove_mark(markid){
      let chapter_id = markid.split('-')[0];
      let m_id = markid.split('-')[1];
      let index = this.chapters.findIndex(item => item.id === chapter_id);
      if (index !== -1){
        
        // 创建一个临时的DOM节点
        const divContainer = document.createElement('div');

        // 将HTML字符串设置为这个DOM节点的innerHTML
        divContainer.innerHTML = this.chapters[index].content;

        // 查找并删除特定ID的<span>元素,即书签
        const spanElement = divContainer.querySelector(`#${m_id}`);
        if (spanElement) {
            const parentElement = spanElement.parentNode;
            parentElement.removeChild(spanElement);
        }

        // 获取处理后的HTML字符串
        this.chapters[index].content = divContainer.innerHTML;

        // 如果删除的是当前章节的书签，删除完重新加载该章节
        if (this.chapters[index].id === this.current_id){
          this.novelContent = this.chapters[index].content;
        }
      }

    }


    


    },
};
</script>

<style scoped>

body, html {
    margin: 0;
    height: 100%;
    /* overflow: hidden; */
  }
.left {
  /* position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%; */
  position: relative;
  height: 100%;
  background-color: var(--writeview-left-bg-color);
  /* flex-grow: 1; */
  /* display: flex;
  flex-direction: column; */
  }
.top {
  display: flex;
  height: 100%;
  /* background-color: rgb(251, 4, 127); */
}
.resizeable {
    overflow: hidden;
    position: relative;
  }
  
.resize-handle {
  width: 5px;
  /* background-color: aliceblue; */
  cursor: ew-resize;

}
/* .writing-area {
  width: 100%;
  height: 100%;
} */

textarea {
  width: 100%;
  height: 100%;
  padding: 20px 20px 20px 20px;
  font-size: 16px;
  background-color: bisque;
}
#dev1{
  /* background-color: rgb(172, 179, 40); */
  /* position: relative;
  display: flex; */
}
#dev2{
  background-color: rgb(112, 112, 28);
}
#dev3{
  /* background-color: rgb(0, 204, 255); */
  display: flex;
  flex-direction: column;

}
.data-area{
  background-color: var(--writeview-right-dataarea-bg-color);
  height: 200px;
  width: 100%;
  padding-top: 20px;
  overflow: hidden;
  margin-bottom: 2px;

}
.data-area > :nth-child(1){
  margin-left: 25px;
  
}
.data-area > :nth-child(2){
  /* margin-left: 38px; */
  color: black;
  
}
.data-area > :nth-child(3){
  /* margin-left: 25px; */
  color: black;
  
}
.data-area > :nth-child(4){
  margin-left: 25px;
  
}
.data-item{
  margin: 10px;
  display: flex;
  align-items: center;
  overflow: hidden; /* 隐藏溢出内容 */
  white-space: nowrap; /* 禁止文本换行 */
}
.data-label{
  color: black;
  
}
.data-value{
  padding-left: 15px;
  
}
.plugin-area{
  background-color: var(--writeview-right-pluginarea-bg-color);
  flex: 1;
}
</style>
