<template>
    <div class="catalog">
        <el-tree 
          ref="tree" 
          :data="catalog_data" 
          node-key="id" 
          :props="defaultProps" 
          :expand-on-click-node="false"
          :current-node-key="current_node_key"
          :highlight-current="true"
          :check-on-click-node="true"
          @node-click="handleNodeClick" 
          @node-contextmenu="handleRightClick" 
          class="tree">

          <template #default="{ node, data }">
            <span class="custom-tree-node">
              <el-input v-if="node === editingNode" ref= "input" v-model="data.label" @blur="handleEditEnd(data)" @keyup.enter="handleEditEnd(data)" class="tree_node"/>
              <span v-else @dblclick="handleNodeDblClick(node)" class="tree_node">{{ node.label }}</span>
                 
            </span>
          </template>

        </el-tree>
        
      
        <div id="contextmenu"
           v-show="menuVisible"
           class="menu">
        <div class="contextmenu__item"
             @click="new_chapter">新建章</div>
        <div class="contextmenu__item"
             @click="new_volume">新建卷</div>
        <div class="contextmenu__item"
             @click="delete_this">删除</div>
        
        </div>
        
        

    </div>

    

</template>
<script>
import { useEventBusStore } from '../stores/eventBus';
  
  export default {
    
    props: ['catalog_data'],

    data() {
      return {
        data: [
            {
              id:'0',
          label: '书',
          children: [{
            id:'1',
            label: '卷',
            children: [{
              id:'1_1',
              label: '章'
            }]
          }]
        }, 
        
        ],
        defaultProps: {
          children: 'children',
          label: 'label'
        },

        menuVisible: false,
        current_node_key: '0',



        editingNode: null,


      };
    },

    beforeUnmount() {
      // 清理事件总线监听
      const eventBus = useEventBusStore();
      eventBus.off('click:textarea', this.close_Rightmenu);
      eventBus.off('set-last-node-id', this.set_last_node_id);
      eventBus.off('jump_to_mark', this.jump_to_mark);
      eventBus.off('newChapter', this.new_chapter);
      eventBus.off('newVolume', this.new_volume);
    },
    mounted(){
      const eventBus = useEventBusStore();
      eventBus.on('click:textarea', this.close_Rightmenu);

      eventBus.on('set-last-node-id', this.set_last_node_id);
      eventBus.on('jump_to_mark', this.jump_to_mark);

      eventBus.on('newChapter', this.new_chapter);

      eventBus.on('newVolume', this.new_volume);
    },

      // 监测this.current_node_key的变化,当变化时，调用一个函数把节点的key值传给父组件
      watch: {
      current_node_key(newValue, oldValue) {
        const eventBus = useEventBusStore();
        eventBus.emit('update:current_node_key', [newValue, oldValue]);

        this.$nextTick(() => {
          this.$refs.tree.setCurrentKey(newValue);
        });

        
      }
    },

    methods: {

      set_last_node_id(node_id) {
        this.current_node_key = node_id;
      },

      jump_to_mark(markid) {
        let chapter_id = markid.split("-")[0];
        if (chapter_id !== this.current_node_key) {
          this.current_node_key = chapter_id;
        }
      },



      handleNodeClick(data) {
        this.menuVisible = false
        //console.log(data);
        const key = this.$refs.tree.getCurrentKey();
        console.log('当前选中节点的 key 值为:', key);
        this.current_node_key = this.$refs.tree.getCurrentKey();

      },

      handleRightClick(event,data,node){
        // console.log(" event is:")
        // console.log(event)
        // console.log(" data is:")
        // console.log(data)
        // console.log(" node is:")
        // console.log(node)

        this.menuVisible = false // 先把模态框关死，防止连续两次右击
        this.menuVisible = true // 显示模态窗口，跳出自定义菜单栏
        event.preventDefault();
        var menu = document.querySelector('.menu')
        menu.style.left = event.clientX + 1 + 'px'
        if (event.clientY+100 > window.innerHeight) {
          menu.style.top = event.clientY - 101 + 'px'
      } else {
          menu.style.top = event.clientY + 1 + 'px'
      }
        document.addEventListener('click', this.closeRightmenu)

        this.current_node_key = data.id;

      },
      close_Rightmenu(e){
        this.closeRightmenu();
      },
      closeRightmenu() {
      // 取消鼠标监听事件 菜单栏
      this.menuVisible = false
      document.removeEventListener('click', this.closeRightmenu) // 关掉监听，
      //console.log("关掉监听了！")
    },
    
    new_chapter(){
      const tree = this.$refs.tree;
      var parent_Node = tree.getNode(this.current_node_key).parent;
      
      
      if (this.current_node_key !== '0') {
        // 右键某章或某卷新增章节时，在本卷新增一章
        if (!this.current_node_key.includes("_")){
          parent_Node = tree.getNode(this.current_node_key);
        }
        let max_id = -1;
        if (parent_Node.childNodes && parent_Node.childNodes.length > 0) {
            parent_Node.childNodes.forEach(childNode => {
              let temp_id = parseInt(childNode.key.split("_")[1]);
              if (max_id < temp_id){
                max_id = temp_id;
              } 
            });
        } else {
          max_id = 0;
        }
        const new_id = parent_Node.key+'_'+ (max_id + 1);
        //const newNode = { id: new_id, label: '新建章' };
        //tree.append(newNode, parent_Node.data);
        const eventBus = useEventBusStore();
        eventBus.emit('update:new_chapter', new_id);
        this.current_node_key = new_id;


        
        
      } else {
        
        // 右键书名新增章节时，在最后一卷新增一章，没有卷时，自动创建第一卷第一章
        const the_node = this.$refs.tree.getNode(this.current_node_key);
        const lastChild = the_node.childNodes[the_node.childNodes.length - 1];
        
        if (lastChild) {
          

          let max_id = -1;
          if (lastChild.childNodes && lastChild.childNodes.length > 0) {
            lastChild.childNodes.forEach(childNode => {
                let temp_id = parseInt(childNode.key.split("_")[1]);
                if (max_id < temp_id){
                  max_id = temp_id;
                } 
              });
          } else {
            max_id = 0;
          }
          let new_id = lastChild.key+'_'+ (max_id + 1);
          //const new_Node = { id: new_id, label: '新建章' };

          //tree.append(new_Node, lastChild.data);
          const eventBus = useEventBusStore();
          eventBus.emit('update:new_chapter', new_id);
          this.current_node_key = new_id;
          

        } else {
          // let first_volume = {id:'1', 
          //                 label: '新建卷', 
          //                 children: [
          //                   {
          //                     id:'1_1',
          //                     label: '新建章'
          //                   },
          //                 ]};
          //tree.append(first_volume, the_node.data);
          const eventBus = useEventBusStore();
          eventBus.emit('update:new_chapter', '1_1');
          this.current_node_key = '1_1';
          
        }
    
      }

    },


    new_volume(){
      // 右键新增卷时，在卷尾新增一卷，没有卷时，新增第一卷
      const tree = this.$refs.tree;
      var parent_Node = tree.getNode('0');
      // console.log("得到的节点是：");
      // console.log(parent_Node);
      let max_id = -1;
      if (parent_Node.childNodes && parent_Node.childNodes.length > 0) {
        parent_Node.childNodes.forEach(childNode => {
            let temp_id = parseInt(childNode.key);
            if (max_id < temp_id){
              max_id = temp_id;
            } 
          });
      } else {
        max_id = 0;
      }
      let new_id = (max_id + 1).toString();
      //const new_Node = { id: new_id, label: '新建卷' ,children: []};

      //tree.append(new_Node, parent_Node.data);
      const eventBus = useEventBusStore();
      eventBus.emit('update:new_volume', new_id);
      this.current_node_key = new_id;
      
    },

    delete_this(){
      console.log('当前key值是：');
      console.log(this.current_node_key);
      if (this.current_node_key === '0'){
        console.log('选中了书名！');
        this.$message({
          showClose: true,
          message: '请从书架删除',
          duration: 1400,
        });
      } else {

        const tree = this.$refs.tree;
        const node = tree.getNode(this.current_node_key); // 根据 node-key 获取节点数据对象

        if (this.current_node_key.includes('_')) {
          

          this.$confirm('将永久删除本章，是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {

            const nextNode = this.getNextSiblingKey(this.current_node_key, tree);
            if (nextNode){
              this.current_node_key = nextNode;
            } else {
              const preNode = this.getPreviousKey(this.current_node_key, tree);
              if (preNode){
                this.current_node_key = preNode;
              } else {
                this.current_node_key = this.current_node_key.split('_')[0];
              }
            }
            const eventBus = useEventBusStore();
            eventBus.emit('update:delete_chapter', node.key);
            //tree.remove(node.data); // 调用 remove 方法删除节点

            // this.$message({
            //   type: 'success',
            //   message: '已删除!'
            // });
          }).catch(() => {
            this.$message({
              type: 'info',
              message: '已取消'
            });          
          });



        } else {
          

          this.$confirm('将永久删除本卷及其中全部章节，是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {


            const nextNode = this.getNextSiblingKey(this.current_node_key, tree);
            if (nextNode){
              this.current_node_key = nextNode;
            } else {
              const pernode = this.getPreviousKey(this.current_node_key, tree);
              if (pernode){
                this.current_node_key = pernode;
              } else {
                this.current_node_key = '0';
              }
            }
            const eventBus = useEventBusStore();
            eventBus.emit('update:delete_volume', node.key);
            //tree.remove(node.data); // 调用 remove 方法删除节点


            // this.$message({
            //   type: 'success',
            //   message: '已删除!'
            // });
          }).catch(() => {
            this.$message({
              type: 'info',
              message: '已取消'
            });          
          });



        }

      }

    },

    
    getNextSiblingKey(nodeKey, tree) {
      // 通过getNode检查给定node_key是否存在
      const node = tree.getNode(nodeKey);
      if (!node) {
        console.error(`Node with key ${nodeKey} not found.`);
        return false; // 如果节点不存在，则直接返回
      }

      const parentNode = node.parent;
      if (!parentNode) {
        console.error(`Parent node for node with key ${nodeKey} not found.`);
        return false; // 如果父节点不存在，也直接返回
      }

      const childNodes = parentNode.childNodes;
      // 寻找最后一个子节点
      const lastChild = childNodes[childNodes.length - 1];
      if (nodeKey === lastChild.key) {
        return null; // 如果当前节点是最后一个子节点，则没有下一个兄弟节点
      }

      // 找到当前节点在childNodes中的索引，然后返回下一个索引对应的key
      const currentIndex = childNodes.findIndex(child => child.key === nodeKey);

      // 确保下一个索引在有效范围内
      const nextIndex = Math.min(currentIndex + 1, childNodes.length - 1);
      const nextSibling = childNodes[nextIndex];

      return nextSibling.key;
      },


    getPreviousKey(nodeKey, tree) {
        // 通过getNode检查给定node_key是否存在
        const node = tree.getNode(nodeKey);
        if (!node) {
          console.error(`Node with key ${nodeKey} not found.`);
          return false; // 如果节点不存在，则直接返回
        }

        const parentNode = node.parent;
        if (!parentNode) {
          console.error(`Parent node for node with key ${nodeKey} not found.`);
          return false; // 如果父节点不存在，也直接返回
        }

        const childNodes = parentNode.childNodes;
        // 寻找最后一个子节点
        const firstChild = childNodes[0];
        if (nodeKey === firstChild.key) {
          return null; // 如果当前节点是第一个子节点，则没有
        }

        // 找到当前节点在childNodes中的索引，然后返回下一个索引对应的key
        const currentIndex = childNodes.findIndex(child => child.key === nodeKey);

        // 确保下一个索引在有效范围内
        const firstIndex = Math.max(currentIndex - 1, 0);
        const previousSibling = childNodes[firstIndex];

        return previousSibling.key;
        },


      //  双击节点，重命名
      handleNodeDblClick(node){
        
        this.editingNode = node;
        this.$nextTick(() => {
          const input = this.$refs.input;
          
          if (input) {
            input.focus();
            input.select();
          }
        });

      },

      handleEditEnd(data){
        const eventBus = useEventBusStore();
        this.editingNode = null;
        eventBus.emit('update:rename_node', [data.id, data.label]);
      },

    }
  };
</script>
<style scoped>

.contextmenu__item {
  display: block;
  line-height: 34px;
  text-align: center;
}
.contextmenu__item:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}
.menu {
  position: fixed;
  background-color: var(--color-background-mainview);
  width: 100px;
  /*height: 106px;*/
  font-size: 12px;
  color: #444040;
  border-radius: 4px;
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.175);
  white-space: nowrap;
  z-index: 1000;
}

.catalog {
  width: 100%;
}

.tree {
  border: 1px solid #ebeef5;
  /* margin: 5px; */
  /* background-color: #66b1ff; */
  width: 100%;
  
}

.tree_node {
  margin: 10px;
  width: 100%;
  padding: 2px;
}
.contextmenu__item:hover {
  cursor: pointer;
  background: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}


</style>