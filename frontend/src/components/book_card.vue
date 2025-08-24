<template>
    <div class="book_card">
        <div class="book_surface">


          <el-popover
            placement="bottom-start"
            :width="150"
            trigger="hover"
            :auto-close="1000"
          >
            <template #reference>
              <div  class="book_cover">
                <div class="book_img" 
                  @click.stop="to_write_view"
                >
                  {{book_info.book_name}}
                  <!-- <img :src="book_info.book_cover" alt="#"> -->
                </div>
                
                <div class="book_editor">
                  <el-button type="primary" text @click.stop="more_book" class="more_button"><el-icon><ele-More /></el-icon></el-button>
                </div>
              </div>
            </template>

            <div class="book_info">

              <el-table :data="lessBookTableData" :show-header="false" style="width: 100%" :cell-style="{fontSize:'12px'}">
                <el-table-column prop="data_type" label="数据项" min-width="50%" />
                <el-table-column prop="data_value" label="值" min-width="50%" />
                
              </el-table>
            </div>
          </el-popover>


        </div>

        <div>

          <el-dialog v-model="more_info" :show-close="false" align-center :style="{ minWidth: '500px', maxWidth: '800px' }">
            <template #header>
              <div class="more-header">
                <h4>详细信息</h4>
                <div v-if="!editing" class="more-header-edit">
                  <el-button type="primary" text @click="editor_book">
                    <el-icon><ele-Edit /></el-icon>
                  </el-button>
                  <el-button type="primary" text @click="delete_book"><el-icon><ele-Delete /></el-icon></el-button>
                </div>
                <div v-else class="more-header-edit">
                  <el-button type="primary" text @click="restore_book_info"><el-icon><ele-RefreshLeft /></el-icon></el-button>
                  <el-button type="primary" text @click="confirm_edit"><el-icon><ele-Check /></el-icon></el-button>
                </div>
              </div>
            </template>
            <div class="book_info">

              <el-table :data="moreBookTableData" :show-header="false" style="width: 100%" :cell-style="{fontSize:'15px'}">
                <el-table-column prop="data_type" label="数据项" min-width="20%" align="right">
                </el-table-column>
                <el-table-column prop="data_value" label="值" min-width="80%" >
                  <template #default="scope">
                    <div v-if="editing && scope.row.id === 7 && scope.row.canEdit" class="book_tags">
                      <el-tag
                        v-for="(tag,index) in scope.row.data_value"
                        :key="index"
                        closable
                        :disable-transitions="false"
                        @close="deleteTag(tag)"
                        type="primary"
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

                    <div v-else-if="editing && scope.row.id === 3 && scope.row.canEdit ">

                      <el-select v-model="scope.row.data_value" >
                        <el-option label="已完结" value="已完结" />
                        <el-option label="写作中" value="写作中" />
                      </el-select>

                    </div>


                    <div v-else-if="editing && scope.row.id === 8">
          
                        <el-tag
                          v-for="tag in all_tags"
                          :key="tag"
                          class="book_tag"
                          @click="addToThisBook(tag)">
                          {{tag}}
                        </el-tag>
                      </div>

                    <el-input 
                      v-else-if="editing && scope.row.canEdit" 
                      v-model="scope.row.data_value"
                      size="mini" />
                    <div v-else-if="scope.row.id === 7">
                      <el-tag
                        v-for="(tag,index) in scope.row.data_value"
                        :key="index"
                        class="book_tag"
                        type="primary">
                        {{ tag }}
                      </el-tag>
                    </div>
                    <span v-else>{{ scope.row.data_value }}</span>
                  </template>
                </el-table-column>
                
              </el-table>
            </div>
          </el-dialog>

        </div>



    </div>
    
</template>
  
<script>
  import { defineComponent, ref } from 'vue';
  import { useEventBusStore } from '../stores/eventBus';

    
  
    export default defineComponent({
        props:['book_info','all_tags'],
    
      data() {
        return {
          value: false,
          book_cover:'',
          init_book_status:'',
          lessBookTableData:[
            // {
            //   data_type:"作者:",
            //   data_value:"吴承恩"
            // },
            // {
            //   data_type:"状态:",
            //   data_value:"已完结"
            // },
            // {
            //   data_type:"字数:",
            //   data_value:"100万"
            // },
            
          ],
          moreBookTableData:[
            // {
            //   id: 1,
            //   data_type:"书名:",
            //   data_value:"西游记",
            //   canEdit:true
            // },
            // {
            //   id: 2,
            //   data_type:"作者:",
            //   data_value:"吴承恩",
            //   canEdit:true
            // },
            // {
            //   id: 3,
            //   data_type:"状态:",
            //   data_value:"已完结",
            //   canEdit:true
            // },
            // {
            //   id: 4,
            //   data_type:"字数:",
            //   data_value:"100万",
            //   canEdit:false
            // },
            // {
            //   id: 5,
            //   data_type:"创作于:",
            //   data_value:"2024.06.05",
            //   canEdit:false
            // },
            // {
            //   id: 6,
            //   data_type:"完结于:",
            //   data_value:"2024.06.06",
            //   canEdit:false
            // },
            // {
            //   id: 7,
            //   data_type:"标签:",
            //   data_value:['历史','神话'],
            //   canEdit:true
            // },
            
          ],
          editing:false,
          more_info:false,
          newTagValue:'',
          newTagVisible:false,
    
        }
      },

      mounted() {
        this.init_BookTableData();

      },

      watch:{
        book_info:{
          handler(newValue,oldValue){
            this.init_BookTableData();
          },
          deep:true
        }
      },
      methods: {

        to_write_view(){
          const eventBus = useEventBusStore();
          eventBus.emit('to_write_view',this.book_info.book_id);
        },

        
        init_BookTableData(){
          // 记录书籍是否完结
          this.init_book_status = this.book_info.book_status;
          // 字数过万后，显示单位万
          let word_count = this.book_info.total_words
          if (this.book_info.total_words.length > 4){
            word_count = this.book_info.total_words.slice(0,-4) + '.' + this.book_info.total_words.slice(-4,-3) + " 万";
          }
          // 字数过十万后，省略小数位
          if (this.book_info.total_words.length > 5){
            word_count = this.book_info.total_words.slice(0,-4) + " 万";
          }
          this.lessBookTableData = [
            {
              data_type:"作者:",
              data_value:this.book_info.book_author
            },
            {
              data_type:"状态:",
              data_value:this.book_info.book_status
            },
            {
              data_type:"字数:",
              data_value:word_count
            },
          ]

          this.moreBookTableData = [
            {
              id: 1,
              data_type:"书名:",
              data_value:this.book_info.book_name,
              
              canEdit:true
            },
            {
              id: 2,
              data_type:"作者:",
              data_value:this.book_info.book_author,
              canEdit:true
            },
            {
              id: 3,
              data_type:"状态:",
              data_value:this.book_info.book_status,
              canEdit:true
            },
            {
              id: 4,
              data_type:"字数:",
              data_value:word_count,
              canEdit:false
            },
            {
              id: 5,
              data_type:"创作于:",
              data_value:this.book_info.book_create_time,
              canEdit:false
            },
            {
              id: 6,
              data_type:"完结于:",
              data_value:this.book_info.book_finish_time,
              canEdit:false
            },
            {
              id: 7,
              data_type:"本书标签:",
              data_value:this.book_info.book_tags.slice(),
              canEdit:true
            },
          ]

        },
        more_book(){
          this.more_info = true;
          this.init_book_status = this.book_info.book_status;
        },

        editor_book(){
          this.editing = true;
          this.moreBookTableData.push({
            id: 8,
            data_type:"所有标签:",
            data_value:this.all_tags,
            canEdit:false
          })

        },

        delete_book(){
          this.$confirm('将永久删除本书，是否继续?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            const eventBus = useEventBusStore();
            eventBus.emit('delete-book', this.book_info.book_id);
            this.more_info = false;
            
          }).catch((error) => {
            throw error;
            this.$message({
              type: 'info',
              message: '已取消了'
            });          
          });
        },

        deleteTag(tag){
          const index = this.moreBookTableData[6].data_value.indexOf(tag);
          if (index !== -1) {
            this.moreBookTableData[6].data_value.splice(index, 1);
          }
          
        },
        addToThisBook(tag){
          if (!this.moreBookTableData[6].data_value.includes(tag)){
            this.moreBookTableData[6].data_value.push(tag);
          }
        },

        showTagInput(){
          this.newTagVisible = true;
          this.$nextTick(() => {
              // 设置焦点
              this.$refs.newTagInput.focus();
          });
        },

        newTagInputConfirm(){
          if (this.newTagValue && !this.moreBookTableData[6].data_value.includes(this.newTagValue)) {
            this.moreBookTableData[6].data_value.push(this.newTagValue);
          }
          this.newTagVisible = false;
          this.newTagValue = '';
        },

        restore_book_info(){
          this.init_BookTableData();
          this.moreBookTableData.push({
            id: 8,
            data_type:"所有标签:",
            data_value:this.all_tags,
            canEdit:false
          })
          
        },

        confirm_edit(){
          this.editing = false;
          this.moreBookTableData.splice(7, 1);
          // 更新lessBookTableData
          this.lessBookTableData[0].data_value = this.moreBookTableData[1].data_value;
          this.lessBookTableData[1].data_value = this.moreBookTableData[2].data_value;

          console.log("完结相关打印1：");
          console.log(this.init_book_status);
          console.log(this.moreBookTableData[2].data_value);

          if (this.init_book_status !== '已完结' && this.moreBookTableData[2].data_value === '已完结'){
            const currentDate = new Date();
            // 转换为指定格式的字符串: YYYY-MM-DD
            const year = currentDate.getFullYear();
            const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
            const day = currentDate.getDate().toString().padStart(2, '0');
            const formattedDate = `${year}-${month}-${day}`;


            this.moreBookTableData[5].data_value = formattedDate;

          } else if (this.init_book_status === '已完结' && this.moreBookTableData[2].data_value !== '已完结'){
            this.moreBookTableData[5].data_value = '--';
          }

          console.log("完结相关打印2：");
          console.log(this.moreBookTableData[5].data_value);
          

          let delete_tags = [];
          for (const item of this.book_info.book_tags){
            if (!this.moreBookTableData[6].data_value.includes(item)){
              delete_tags.push(item);
            }
          }
          
          let new_book_info = [{
            book_id: this.book_info.book_id,
            book_name: this.moreBookTableData[0].data_value,
            book_author: this.moreBookTableData[1].data_value,
            book_status: this.moreBookTableData[2].data_value,
            total_words: this.book_info.total_words,
            book_create_time: this.book_info.book_create_time,
            book_finish_time: this.moreBookTableData[5].data_value,
            book_intro: this.book_info.book_intro,
            book_cover: this.book_info.book_cover,
            book_tags: this.moreBookTableData[6].data_value,
            book_last_read_chapter_id: this.book_info.book_last_read_chapter_id,
            
          },
          delete_tags
          ]
          const eventBus = useEventBusStore();
          eventBus.emit('update_book_info', new_book_info);
        },

 
      },
    })
</script>
  
  
  
<style scoped>

body, html {
      margin: 0;
      /* height: 100%; */
      /* overflow: hidden; */
    }
  
 .book_card{
    position: relative;
    background-color: bisque;
    border-radius: 10px;
    /* margin: 10px; */
    /* width: 150px; */
    height: 150px;
      }

.book_surface{
    position: relative;
    width: 100%;
    height: 100%;
    background-color: rgb(69, 61, 52);
    display: flex;
    flex-direction: column;
    padding: 2px;
      }
/* .card_body{
    position: relative;
    width: 100%;
    height: 100%;
    background-color: rgb(227, 14, 14);
    display: flex;
    flex-direction: column;
      } */
.book_cover{
    position: relative;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    background-color: rgb(87, 190, 241);
      }
.book_img{
  position: relative;
  flex-grow: 9;
  padding-left: 2px;
  padding-top: 2px;
}
.book_editor{
  position: relative;
  flex-grow: 1;
  background-color: aqua;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0px;
}
.book_info{
    position: relative;
    width: 100%;
    background-color: rgb(139, 219, 49);
    /* overflow: hidden; */
  }
.more-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  height: 20px;
}

.more-header-edit{
  display: flex;
  position: relative;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.book_tags{
  position: relative;
  /* display: flex;
  flex-wrap: wrap; */
}
.book_tag{
  position: relative;
  margin: 2px;
}
.InputTag{
  position: relative;
  margin: 2px;
  width: 60px;

}
.button-new-tag{
  position: relative;
  margin: 2px;
}

    
/* .editor_button{
  
} */
      
      
</style>