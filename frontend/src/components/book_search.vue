<template>
    <div class="search_container">
      
        <el-collapse accordion  @change="handleChange">
          <el-collapse-item  name="1">

            <template #title>
                
                <div v-if="isfold" class="simple_search">
                    <el-input
                        v-model="simple_input"
                        style="width: 400px"
                        placeholder="Please input"
                        class="custom-input"
                        @click="search_input"
                        @keydown.enter="start_search"
                    >
                    <template #prepend>
                        <el-select v-model="simple_select" placeholder="选择" style="width: 100px" class="search-select">
                            <el-option label="书名" value="bookName" />
                            <el-option label="作者" value="bookAuthor" />
                            <el-option label="标签" value="bookTag" />
                        </el-select>
                    </template>
                    <template #append>
                        <el-button @click="start_search"><el-icon><ele-Search /></el-icon></el-button>
                    </template>
                    </el-input>
                </div>
                <div v-else class="simple_search">搜索</div>


            </template>

          <div class="search_items">
          

          <el-form  :model="search_form" labelPosition="right" label-width="auto" style="max-width: 800px">
            <el-form-item label="书名">
              <el-input
                clearable
                placeholder="请输入书名"
                v-model="search_form.bookName"
                style="max-width: 200px;"
                class="search-input"
                >
              </el-input>
            </el-form-item>
            <el-form-item label="作者">
              <el-input
                clearable
                placeholder="请输入作者"
                v-model="search_form.bookAuthor"
                style="max-width: 200px;"
                class="search-input"
                >
              </el-input>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="search_form.bookStatus" placeholder="是否完结" style="max-width: 200px;" >
                <el-option label="写作中" value="写作中" />
                <el-option label="已完结" value="已完结" />
              </el-select>
            </el-form-item>
            <el-form-item label="创建于">
              <el-date-picker
                v-model="search_form.bookCreateTime"
                type="daterange"
                unlink-panels
                range-separator="至"
                start-placeholder="起始日期"
                end-placeholder="结束日期"
                style="max-width: 300px;"
                >
              </el-date-picker>
            </el-form-item>
            <el-form-item label="标签">
              <el-checkbox :indeterminate="isIndeterminate" v-model="checkAll" @change="handleCheckAllChange">全选</el-checkbox>
              <el-checkbox-group v-model="search_form.bookTag" @change="handleCheckedlabelsChange">
                <el-checkbox v-for="lab in book_tags" :label="lab" :key="lab">{{lab}}</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item>
              <div class="result_button">
                <el-button type="primary" @click="reset_filter">重置</el-button>
                <el-button type="success" @click="filt_done" style="margin-right: 30px;">筛选</el-button>
                
              </div>
            </el-form-item>
          </el-form>

        </div>

          </el-collapse-item>
        </el-collapse>
  
  
    </div>
    
  </template>
  
  <script>
  import { defineComponent, ref } from 'vue';
  import { useEventBusStore } from '../stores/eventBus';
  
  
    export default defineComponent({

    props: ['book_tags'],
  
    components: {
      
    },
      data() {
        return {
          
          checkAll: false,
          isIndeterminate: true,

          simple_input:'',
          simple_select:'bookName',
          isfold:true,

          search_form:{
            bookName:'',
            bookAuthor:'',
            bookStatus:'',
            bookCreateTime:null,
            bookTag:[]
          },
    
        }
      },
      methods: {
        handleChange(val) {
            this.isfold = !this.isfold;
            console.log(val);
        },

        start_search(event){
            event.stopPropagation();
            const search_data = [this.simple_select, this.simple_input];
            const eventBus = useEventBusStore();
            eventBus.emit('simple-search',search_data);

        },

        search_input(event){
            event.stopPropagation(); // 阻止焦点事件冒泡
        },
  
        handleCheckAllChange(val) {
          this.search_form.bookTag = val ? this.book_tags : [];
          this.isIndeterminate = false;
        },
        handleCheckedlabelsChange(value) {
          let checkedCount = value.length;
          this.checkAll = checkedCount === this.book_tags.length;
          this.isIndeterminate = checkedCount > 0 && checkedCount < this.book_tags.length;
        },

        filt_done(){
          //console.log(this.search_form);
          const eventBus = useEventBusStore();
          eventBus.emit('filt-search',this.search_form);
          // this.reset_filter();

        },

        reset_filter(){
          this.search_form = {
            bookName:'',
            bookAuthor:'',
            bookStatus:'',
            bookCreateTime:null,
            bookTag:[]
          }
          this.checkAll = false;
          this.isIndeterminate = true;
        }

        
      },
    })
  </script>
  
  
  
    <style scoped>
  
  body, html {
      margin: 0;
      height: 100%;
      /* overflow: hidden; */
    }

    .simple_search{
        position: relative;
        margin-left: 20px;
        display: flex;
        align-items: center;
        overflow: hidden;
    }

    
    /* 修改折叠面板的背景色 */
    ::v-deep .el-collapse-item__wrap {
     /*background-color: #3e3d3d;  修改内容区域的背景色 */
      border: 0px !important;
    }

    ::v-deep .el-collapse-item__header {
      background-color: var(--color-background-mainview-shelf);  /* 修改标题区域的背景色 */
      /* color: rgb(255, 255, 255); */
      border: 0px !important;
    }

    ::v-deep .el-collapse-item__wrap.is-active {
      border: 0px !important;
    }


    .search-select :deep(.el-select__wrapper) {
     /* background-color: #393838;  背景色 */
    }

    .custom-input{
        max-width: 600px;
    }
    /* 使用 :deep() 选择器 */
    .custom-input :deep(.el-input__wrapper) {
    /* background-color: #393838;  背景色 */
    }
    .custom-input :deep(.el-input__wrapper:focus) {
    /*  background-color: #5b5c5d;  聚焦时的背景色 */
    }
    .custom-input :deep(.el-input__inner) {
    /*  color: rgb(227, 225, 227);  文字颜色 */
    }

    .custom-input :deep(.el-input__inner:focus) {
    /*  color: rgb(255, 255, 255);  文字颜色 */
    }

    /* 使用 :deep() 选择器 */
    .search-input :deep(.el-input__wrapper) {
    /*  background-color: #393838;  背景色 */
    }
    .search-input :deep(.el-input__wrapper:focus) {
    /*  background-color: #5b5c5d;  聚焦时的背景色 */
    }
    .search-input :deep(.el-input__inner) {
    /*  color: rgb(227, 225, 227);  文字颜色 */
    }

    .search-input :deep(.el-input__inner:focus) {
    /*  color: rgb(255, 255, 255);  文字颜色 */
    }
    
      
    .search_items{
        padding-top: 20px;
        padding-left: 20px;
        /* background-color: rgb(16, 239, 239); */
    }
    .result_button{
      position: relative;
      margin: 20px;
      width: 100%;
      display: flex;
      gap:50px;
      justify-content: center;
      align-items: center;
    }
    .bookname{
    display: flex;
    }
    .create_time{
    display: flex;

    }
    .booktag{
    display: flex;
    }
    .search_done{
    margin-left: auto;
    margin-right: auto;
    }
    .input {
    width: 150px;
    }

    .search_container {
    display: flex;
    /* background-color: aqua; */
    flex-direction: column;
    height: 100%;
    }
      
    </style>