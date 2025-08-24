<template>
    <div class="top1">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="left1">
        <el-tab-pane label="目录" name="tab1" >
          
            <catalog :catalog_data="catalog_data" class="catalog"/>
          
        </el-tab-pane>

        <el-tab-pane label="大纲" name="tab2" class="tab-pane">
          
            <!-- Tab 2 的内容 -->
            <div v-if="listView" class="outlineList">
              <el-card
                v-for="(item,index) in outlines"
                :key="index"
                shadow="hover" 
                @click="handleCardClick(item)"
                class="outlineCard">
                <div class="outlinetitle">
                <span>{{ item.title }}</span>
                <el-button type="danger" @click.stop="removeCard(index,item)"><el-icon><ele-Delete /></el-icon></el-button>
                </div>
              </el-card>
              <el-card class="addCard" @click="addCard()"><el-icon><ele-Plus /></el-icon></el-card>
            </div>
            <div v-else class="outlineContent">
              <div class="option">
                <el-button type="primary" text @click="back_to_cards" class="option_item">返回</el-button>
                <el-button type="primary" text @click="save_outline" class="option_item">保存</el-button>
                <el-button type="primary" text @click="export_outline" class="option_item">导出</el-button>

                <el-popover
                  placement="bottom-end"
                  title="操作"
                  width="250"
                  trigger="hover"
                >
                  <template #reference>
                    <el-button type="primary" text  class="option_item">说明</el-button>
                  </template>
                  <template #default>
                    <div style="white-space: normal;">
                      Tab: 添加节点前缀或缩进两个空格;<br>
                      <br>
                      Ctrl+Tab: 添加节点前缀或反缩进两个空格。
                    </div>
                  </template>
              </el-popover>
                
              </div>
              <div class="outline_box">
                <div class="outline">
                  
                  <textarea ref="textarea_outline" v-model="mytext" @keydown="handleKeyDown" @dblclick="handleTextAreaDoubleClick" class="myoutline"></textarea>
                  
                </div>
                <div v-if="showMind" class="outline">
                  <Markmap :markdown="mytext" class="markmap"/>
                </div>
            </div>
              
            </div>
          
        </el-tab-pane>
        <el-tab-pane label="书签" name="tab3">
          
            <!-- Tab 3 的内容 -->
            <el-card
            v-for="(item,index) in marks"
                :key="index"
                shadow="hover"
                @click="handleMarkClick(item)"
            >
            <div class="outlinetitle">
                <span>{{ item.content }}</span>
                <el-button type="danger" @click.stop="removeMark(index)"><el-icon><ele-Delete /></el-icon></el-button>
            </div>
            </el-card>
          
        </el-tab-pane>
        <el-tab-pane label="素材" name="tab4">
          
            <!-- Tab 4 的内容 -->
            <p>Content of Tab 4</p>
          
        </el-tab-pane>
      </el-tabs>
    </div>
  </template>
  
  <script>
  import catalog from './catalog.vue';
  import Markmap from './Markmap.vue';
  import { waitForPywebviewApi } from '../customFuncs.js'
  import { useEventBusStore } from '../stores/eventBus';
  
  export default {

    props: ['catalog_data', 'book_path', 'book_name', 'book_id'],

    components:{
      catalog,
      Markmap,
  },
    data() {
      return {
        activeTab: 'tab1',
        listView: true,
        outlines: [],// {id: 1, title: '', content: ''}
        outline_id:0,// 大纲卡片的id
        max_id: 0,
        mytext:'',// 大纲文字内容
        showMind: true,
        marks: [],// {id: 1_1_markid, content: ''}

      };
    },

    beforeUnmount() {
      // 清理事件总线监听
      const eventBus = useEventBusStore();
      eventBus.off('add_mark', this.addMark);
      eventBus.off('update:delete_chapter', this.handle_c_v_delete);
      eventBus.off('update:delete_volume', this.handle_c_v_delete);
    },
    async mounted() {

      // 等待 pywebview 初始化完成
      await waitForPywebviewApi();

      // 加载大纲数据和书签
      this.load_outlines();
      this.loadMark();
      const eventBus = useEventBusStore();
      eventBus.on('add_mark', this.addMark);

      eventBus.on('update:delete_chapter', this.handle_c_v_delete);

      eventBus.on('update:delete_volume', this.handle_c_v_delete);

    },
    methods: {

      saveMark(){
        const markdata = [this.book_path, this.book_id, this.marks];
        window.pywebview.api.addmark(markdata).then(res => {
          if (res === 0){
            this.$message({
              message: '书签添加失败!',
              type: 'error'
            });
          } 
        })
      },
      addMark(markdata){
        const m_id = markdata[0] + '-' + markdata[1];
        this.marks.push({id: m_id, content: markdata[2]});
        this.saveMark();
      },
      removeMark(index){
        const eventBus = useEventBusStore();
        eventBus.emit('remove_mark', this.marks[index].id);
        this.marks.splice(index, 1);
        this.saveMark();
      },
      // 如果删除了卷或章节，其中的书签也需要删除
      handle_c_v_delete(c_v_id){
        this.marks = this.marks.filter(item => !item.id.startsWith(c_v_id));
        this.saveMark();
      },

      loadMark(){
        console.log("加载书签数据！");
        const markdata = [this.book_path, this.book_id];
        window.pywebview.api.load_marks(markdata).then(res => {
          if (res !== 0){
            if (res.length > 0){
              this.marks = res;
            }
            
          }else{
            this.$message({
              message: '书签加载失败!',
              type: 'error'
            });
          } 
        }).catch(error=> {
          throw error;
        })
      },

      // 点击书签,跳转到对应位置
      handleMarkClick(mark_data){
        const eventBus = useEventBusStore();
        eventBus.emit('jump_to_mark', mark_data['id']);
      },

      load_outlines(){
        console.log("加载思维导图数据！");
        const data = [this.book_path, this.book_id];
        
        window.pywebview.api.load_outline(data).then(res => {
          if (res !== 0){
            if (res.length > 0){
              this.outlines = res;
              if (this.outlines && this.outlines.length > 0){
                  this.max_id = Math.max(...this.outlines.map(item => item.id));
                }
            }
            
          }else{
            this.$message({
              message: '大纲加载失败!',
              type: 'error'
            });
          } 
        }).catch(error => {
          throw error;
        })
      },

      handleTabClick(tab) {
        // 监听 tab-click 事件，切换时更新 activeTab 的值
        this.activeTab = tab.props.name;
      },

      handleCardClick(card_data) {
        console.log("当前思维导图：" + card_data.id+ "_" + card_data.title);
        
        const index = this.outlines.findIndex(item => item.id === card_data.id);
        if(index !== -1){
          this.outline_id = this.outlines[index].id;
          this.mytext = this.outlines[index].content;
          this.listView = false;
          
        }
        // 监听 card-click 事件，执行相应的操作
        //console.log('Card clicked!');
      },

      removeCard(index){
        this.outlines.splice(index, 1);
        this.outline_id = 0;
        this.mytext = ''; 
        this.listView = true;
        
        const outlinedata = [this.book_path, this.book_id, this.outlines];
        window.pywebview.api.save_outline(outlinedata).then(res => {
          if (res === 0){
            this.$message({
              message: '删除失败!',
              type: 'error'
            });
          } 
        }).catch(error => {
          throw error;
        })


      },

      addCard(){
        var maxid = this.max_id + 1;
        this.outlines.push({id: maxid, title: 'Outline_' + maxid, 'content':'- '+ 'Outline_' + maxid});
        
        this.outline_id = maxid;
        this.max_id = maxid;
      },

      handleTextAreaDoubleClick(event){
        event.preventDefault(); // 阻止默认的双击选中行为
        event.stopPropagation(); // 阻止事件冒泡
        this.showMind = !this.showMind;
      },

      handleKeyDown(event){

        if (event.key === 'Tab' && event.ctrlKey){
          
          event.preventDefault();
          // 获取当前光标位置
          const cursorPosition = this.$refs.textarea_outline.selectionStart;
            console.log("当前光标位置：" + cursorPosition+' '+this.mytext[cursorPosition]);
            
            // 获取当前行的起始位置
            let currentLineStart = cursorPosition;
            while (currentLineStart > 0 && this.mytext[currentLineStart - 1] !== '\n') {
              currentLineStart--;
            }
            
            if (currentLineStart === 0){
              if (this.mytext[currentLineStart] !== '-'){
                  this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(currentLineStart);
                  this.$nextTick(() => {
                  // 保持光标位置不变
                  this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                  this.$refs.textarea_outline.focus();
                });
              }
            } else{
              //找到当前行非空格字符的起始位置
              let notSpaceLineStart = currentLineStart;
              while (this.mytext[notSpaceLineStart] === ' ' && notSpaceLineStart < this.mytext.length) {
                notSpaceLineStart++;
              }

              if (notSpaceLineStart < this.mytext.length - 1){
                if (this.mytext[notSpaceLineStart] === '-'){
                  if (notSpaceLineStart !== currentLineStart){
                    if (notSpaceLineStart - 2 < currentLineStart){
                      this.mytext = this.mytext.slice(0, currentLineStart) + this.mytext.slice(notSpaceLineStart);
                      this.$nextTick(() => {
                      // 保持光标位置不变
                      this.$refs.textarea_outline.setSelectionRange(cursorPosition - 1, cursorPosition - 1);
                      this.$refs.textarea_outline.focus();
                    });
                    }else{
                      this.mytext = this.mytext.slice(0, notSpaceLineStart - 2) + this.mytext.slice(notSpaceLineStart);
                      this.$nextTick(() => {
                      // 保持光标位置不变
                      this.$refs.textarea_outline.setSelectionRange(cursorPosition - 2, cursorPosition - 2);
                      this.$refs.textarea_outline.focus();
                    });
                    }
                  }
                }else{
                  if (notSpaceLineStart === currentLineStart){
                    this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(notSpaceLineStart);
                    this.$nextTick(() => {
                      // 保持光标位置不变
                      this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                      this.$refs.textarea_outline.focus();
                    });

                  } else {
                    if (notSpaceLineStart - 2 < currentLineStart){
                      this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(notSpaceLineStart);
                      this.$nextTick(() => {
                      // 保持光标位置不变
                      this.$refs.textarea_outline.setSelectionRange(cursorPosition + 1, cursorPosition + 1);
                      this.$refs.textarea_outline.focus();
                    });
                    } else {
                      this.mytext = this.mytext.slice(0, notSpaceLineStart - 2) + '- ' + this.mytext.slice(notSpaceLineStart);
                      this.$nextTick(() => {
                      // 保持焦点
                      this.$refs.textarea_outline.focus();
                    });
                    }
                    
                  }
                }

              }else{
                if (notSpaceLineStart - 2 < currentLineStart){
                  this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(currentLineStart);
                  this.$nextTick(() => {
                  // 保持光标位置不变
                  this.$refs.textarea_outline.setSelectionRange(this.mytext.length, this.mytext.length);
                  this.$refs.textarea_outline.focus();
                });

                }else{
                  this.mytext = this.mytext.slice(0, notSpaceLineStart - 2) + '- ' + this.mytext.slice(notSpaceLineStart);
                  this.$nextTick(() => {
                  // 保持焦点
                  this.$refs.textarea_outline.focus();
                });
                }
              }

            }

          } else if (event.key === 'Tab') {

            event.preventDefault();

            // 获取当前光标位置
            const cursorPosition = this.$refs.textarea_outline.selectionStart;
            console.log("当前光标位置：" + cursorPosition+' '+this.mytext[cursorPosition]);
            
            // 获取当前行的起始位置
            let currentLineStart = cursorPosition;
            while (currentLineStart > 0 && this.mytext[currentLineStart - 1] !== '\n') {
              currentLineStart--;
            }
            
            if (currentLineStart === 0){
              if (this.mytext[currentLineStart] !== '-'){
                  this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(currentLineStart);
                  this.$nextTick(() => {
                  // 保持光标位置不变
                  this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                  this.$refs.textarea_outline.focus();
                });
              }
            } else{
              // 找到当前行非空格内容的开头
              while (this.mytext[currentLineStart] === ' ' && currentLineStart < this.mytext.length) {
                currentLineStart++;
              }
              if (currentLineStart < this.mytext.length - 1){
                if (this.mytext[currentLineStart] === '-'){
                  this.mytext = this.mytext.slice(0, currentLineStart) + '  ' + this.mytext.slice(currentLineStart);

                  this.$nextTick(() => {
                    // 保持光标位置不变
                    this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                    this.$refs.textarea_outline.focus();
                  });

                }else{
                  this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(currentLineStart);

                  this.$nextTick(() => {
                    // 保持光标位置不变
                    this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                    this.$refs.textarea_outline.focus();
                  });
                }

              }else{

                this.mytext = this.mytext.slice(0, currentLineStart) + '- ' + this.mytext.slice(currentLineStart);

                  this.$nextTick(() => {
                    // 保持光标位置不变
                    this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
                    this.$refs.textarea_outline.focus();
                  });

              }
              // 插入两个空格到当前行的行首
              //this.mytext = this.mytext.slice(0, currentLineStart) + '  ' + this.mytext.slice(currentLineStart);

            }

            //确保更新后的文本立即反映在textarea中并保持焦点
            // this.$nextTick(() => {
            //   // 保持光标位置不变
            //   this.$refs.textarea_outline.setSelectionRange(cursorPosition + 2, cursorPosition + 2);
            //   this.$refs.textarea_outline.focus();
            // });
        } else if (event.key === 'Enter') {

          event.preventDefault();
          // 获取当前光标位置,光标还没有跳转到下一行
          const cursorPosition = this.$refs.textarea_outline.selectionStart;
            console.log("当前光标位置：" + cursorPosition+' '+this.mytext[cursorPosition]);
            
            // 获取这一行的起始位置
            let currentLineStart = cursorPosition;
            while (currentLineStart > 0 && this.mytext[currentLineStart - 1] !== '\n') {
              currentLineStart--;
            }
            // 找到此行的非空格内容的开头
            let notSpaceLineStart = currentLineStart;
            while (this.mytext[notSpaceLineStart] === ' ' && notSpaceLineStart < this.mytext.length) {
              notSpaceLineStart++;
            }
            // 给下一行开头添加空格，保证鼠标起始位置和本行的内容开头对齐
            let space_count = notSpaceLineStart - currentLineStart;
            this.mytext = this.mytext.slice(0, cursorPosition) + '\n' +  ' '.repeat(space_count)  + this.mytext.slice(cursorPosition);
            this.$nextTick(() => {
              // 保持光标位置不变
              this.$refs.textarea_outline.setSelectionRange(cursorPosition + space_count+1, cursorPosition + space_count+1);
              this.$refs.textarea_outline.focus();
            });

        }


      },

      save_outline(){
        const index = this.outlines.findIndex(item => item.id === this.outline_id);
        if (index === -1){
          this.$message({
              message: '保存失败!',
              type: 'error'
            });
          return;
        }
        this.outlines[index].content = this.mytext;
        if (this.mytext.length > 0) {
            //console.log("非空字符串");
            this.outlines[index].title = this.mytext.split('\n',1)[0];

        }else{
          this.outlines[index].title = '';
        }

        const outlinedata = [this.book_path, this.book_id, this.outlines];
        window.pywebview.api.save_outline(outlinedata).then(res => {
          if (res === 0){
            this.$message({
              message: '保存失败!',
              type: 'error'
            });
          }else{
            this.$message({
              message: '已保存!',
              type: 'success'
            });
          } 
        }).catch(error => {
          throw error;
        })


      },

      back_to_cards(){
        this.listView = true;
        this.save_outline();
        this.outline_id = 0;
        this.mytext = '';
      },

      export_outline(){
        const index = this.outlines.findIndex(item => item.id === this.outline_id);
        if (index === -1){
          this.$message({
              message: '导出失败!',
              type: 'error'
            });
          return;
        }
        this.outlines[index].content = this.mytext;
        if (this.mytext.length > 0) {
            //console.log("非空字符串");
            this.outlines[index].title = this.mytext.split('\n',1)[0];

        }else{
          this.outlines[index].title = '';
        }
        const outlinedata = [this.book_name, this.outlines[index]];
        window.pywebview.api.export_outline(outlinedata).then(res => {
          if (res === 0){
            this.$message({
              message: '导出失败!',
              type: 'error'
            });
          }else if (res === 1){
            this.$message({
              message: '导出成功!',
              type: 'success'
            });
          } 
        }).catch(error => {
          throw error;
        })
      },







    },
  };
  </script>
  
  <style>
  
.top1 {
  padding-left: 5px;
  padding-right: 5px;
}
.left1 {
  
  width: 100%;
  height: 100%;
  /* background-color: rgb(131, 233, 165); */
  flex-grow: 1;
  /* overflow: hidden; */
  display: flex;
  flex-direction: column;
  }


.left1 > .el-tabs__content {
    flex-grow: 1;
    /* background-color: rgb(38, 212, 239); */
    
  }


  .tab-pane{
    position: relative;
    height: 100%;
    /* background-color: rgb(73, 79, 77); */
  }

  .outlineList{
    position: relative;
    height: 100%;
    margin-top: 5px;
    /* background-color: rgb(238, 148, 238); */
  }
  .outlineCard{
    margin-bottom: 5px;
    overflow: hidden;
    /* padding: 2px; */
    
  }
  .outlinetitle{
    display: flex;
    justify-content: space-between;
    align-items: center;
    /* background-color: aqua; */
  }
  .addCard{
    margin-bottom: 5px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .outlineContent{
    position: relative;
    height: 100%;
    /* background-color: rgb(71, 42, 165); */
    display: flex;
    flex-direction: column;

  }

  .option {
    height: 40px;
    /* background-color: bisque; */
    display: flex;
    align-items: center;
    margin-bottom: 3px;
    border-bottom: 1px solid rgb(220, 220, 220);
    
  }
  .option_item{

    flex-grow: 1;
  }

  .outline_box{
    position: relative;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }

  .outline {
    position: relative;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    /* background-color: bisque; */
  }
  .myoutline{
    position: relative;
    padding-left: 15px;
    padding-top: 20px;
    padding-right: 5px;
    flex-grow: 1;
    resize: none;
    border: none;
    background-color: transparent;
    font-family: Arial, sans-serif; /* 设置字体族，Arial为首选，若不可用则使用用户计算机的无衬线字体 */
    font-size: 16px; /* 设置字体大小为16像素 */
    /* 禁止双击选中文本 */
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10+ and Edge */
    user-select: none; /* Standard syntax */
    
  }

  .markmap{
    position: relative;
    flex-grow: 1;
  }
  
  </style>