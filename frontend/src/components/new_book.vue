<template>
  <div>
    <el-dialog v-model="isopen" title="新建书籍"  align-center @close="closeDialog" :style="{ minWidth: '500px', maxWidth: '800px' }">
      <!-- 对话框内容 -->
      <el-form ref="form" :model="form" labelPosition="right" label-width="auto">
    <el-form-item label="书名">
      <el-input v-model="form.name"></el-input>
    </el-form-item>
    <el-form-item label="作者">
      <el-input v-model="form.author"></el-input>
    </el-form-item>
    
    <!-- <el-form-item label="计划完稿">
      <el-col :span="11">
        <el-date-picker type="date" placeholder="选择日期" v-model="form.date" style="width: 100%;"></el-date-picker>
      </el-col>
    </el-form-item> -->
    
    <el-form-item label="简介">
      <el-input type="textarea" v-model="form.desc"></el-input>
    </el-form-item>
      
    <el-form-item label="本书标签">
      <!-- <el-input v-model="form.tags" placeholder="多个标签请用中文逗号隔开"></el-input> -->

      <div  class="book_tags">
        <el-tag
          v-for="(tag,index) in form.tags"
          :key="index"
          closable
          
          @close="deleteTag(index)"
          type="primary"
          size="small"
          class="book_tag"
          >
          {{ tag }}
        </el-tag>

        <el-input
          v-if="newTagVisible"
          
          ref="newTagInput"
          v-model="newTagValue"
          class="InputTag"
          size="small"
          @keyup.enter="newTagInputConfirm"
          @blur="newTagInputConfirm"
        />
        <el-button v-else class="button-new-tag" size="small" @click="showTagInput">
          + 新标签
        </el-button>


      </div>


    </el-form-item>

    <el-form-item label="所有标签">
      <div>
        <el-tag
          v-for="tag in all_tags"
          :key="tag"
          class="book_tag"
          @click="addToNewBook(tag)">
          {{tag}}
        </el-tag>
    </div>
    </el-form-item>


    
    <el-form-item>
      <div class="result_button">
        <el-button type="success" @click="onSubmit" style="margin-right: 30px;">创建</el-button>
        <el-button type="primary" @click="closeDialog">取消</el-button>
      </div>
    </el-form-item>
  </el-form>


      
    </el-dialog>
  </div>
</template>

<script>

import { useEventBusStore } from '../stores/eventBus';

export default {
  

  props: ['newbook', 'all_tags'],
  data() {
    return {
      isopen: this.newbook,
      form: {
          name: '',
          author: '',
          // date: '',
          type: [],
          desc: '',
          tags: [],

        },
      newTagVisible:false,
      newTagValue:'',
      //newTags:[],
  
    };
  },
  methods: {
    
    closeDialog() {
      this.form = {
                    name: '',
                    author: '',
                    // date: '',
                    type: [],
                    desc: '',
                    tags: [],

                  }
      this.newTagVisible = false;
      this.newTagValue = '';
      this.isopen = false;
      this.$emit('closediag', this.isopen);
    },
    onSubmit() {
        const currentDate = new Date();
        // 转换为指定格式的字符串: YYYY-MM-DD
        const year = currentDate.getFullYear();
        const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
        const day = currentDate.getDate().toString().padStart(2, '0');
        const formattedDate = `${year}-${month}-${day}`;
        
        let new_book_info = {
            book_id: 0,
            book_name: this.form.name,
            book_author: this.form.author,
            book_status: '写作中',
            total_words: '0',
            book_create_time: formattedDate,
            book_finish_time: '--',
            book_intro: this.form.desc,
            book_cover: '#',
            book_tags: this.form.tags,
            book_last_read_chapter_id: '0',
            
          }
          const eventBus = useEventBusStore();
          eventBus.emit('new_book_data', new_book_info);

          // 将变量值恢复为初始状态
          this.form = {
                    name: '',
                    author: '',
                    // date: '',
                    type: [],
                    desc: '',
                    tags: [],

                  }
          this.newTagVisible = false;
          this.newTagValue = '';
          this.isopen = false;

      },

    handleClose(tag) {
      this.dynamicTags.splice(this.dynamicTags.indexOf(tag), 1);
    },

    showTagInput(){
      this.newTagVisible = true;
      this.$nextTick(() => {
          // 设置焦点
          this.$refs.newTagInput.focus();
      });
    },

    deleteTag(index){
      
      this.form.tags.splice(index, 1);
       
    },
    newTagInputConfirm(){
      if (this.newTagValue && !this.form.tags.includes(this.newTagValue)) {
        this.form.tags.push(this.newTagValue);
      }
      this.newTagVisible = false;
      this.newTagValue = '';
    },

    addToNewBook(tag){
      if (!this.form.tags.includes(tag)){
        this.form.tags.push(tag);
      } 
    },


  },

  watch: {
    newbook(newValue) {
      // 监听父组件传递的 prop 的变化，并同步到本地的 localProp
      this.isopen = newValue;
      console.log('newbook is :',this.isopen)
    }
  },
}
</script>

<style scoped>

.book_tags{
  position: relative;
  /* display: flex;
  flex-wrap: wrap; */
}
.book_tag{
  position: relative;
  margin: 3px;
}
.button-new-tag{
  position: relative;
  margin: 2px;
}
.InputTag{
  position: relative;
  margin: 2px;
  width: 60px;

}
.result_button{
  position: relative;
  margin: 20px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}


</style>