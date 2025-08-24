<template>
    <div class="write-shelf-top">
      <div class="header">
        <div class="left_header">
        
            <BookSearch :book_tags="book_tags" class="search" />
        </div>
        <div class="right_header">
        
          <el-button link @click="create_book" class="right_btn"><el-icon><ele-DocumentAdd /></el-icon></el-button>
          <!-- <el-button link @click="change_view" class="right_btn"><el-icon><ele-Files /></el-icon></el-button> -->
          <BookCreate :newbook="isopen" :all_tags="book_tags" @closediag="book_done"></BookCreate>
          
        </div>
      </div>
  
      <div class="main-shelf">
  
        <BookView :books_surface_data="selected_books" :all_tags="book_tags"/>
  
      </div>
      
    </div>
    
  </template>
  
  <script>
  import { defineComponent, ref } from 'vue';
  import { useEventBusStore } from '../stores/eventBus';
  import { intersection, waitForPywebviewApi, waitbookpathinit} from '../customFuncs.js'
  import BookCreate from './new_book.vue'
  import BookSearch from './book_search.vue'
  import BookView from './book_shelf.vue'
  import { inject } from 'vue';
  
    export default defineComponent({
      name: 'writeShelf',
    components: {
      BookCreate,
      BookSearch,
      BookView,
    },

    inject: ['base_config'],
      data() {
        return {
          isopen: false,
          value: false,
          book_tags:[], // 搜索页面要显示的所有标签
          book_path:'', // 书籍路径
          books_surface_data:[],
          tags_to_books:[],
          max_book_id:0, // 获取最大book_id
          selected_books:[],
    
        }
      },
      beforeUnmount() {
        // 清理事件总线监听
        const eventBus = useEventBusStore();
        eventBus.off('update_book_info',this.update_bookInfo);
        eventBus.off('new_book_data',this.create_book_done);
        eventBus.off('delete-book',this.delete_book);
        eventBus.off('simple-search',this.simple_search);
        eventBus.off('filt-search',this.filt_search);
        eventBus.off('to_write_view',this.to_write_view);
        eventBus.off('save-book-info',this.upgrade_book_info);
      },
      async mounted() {

        // 等待 pywebview 初始化完成
        await waitForPywebviewApi();
        await waitbookpathinit(this.base_config);
        this.book_path = this.base_config.bookPath;
        console.log("mout book_path is:");
        console.log(this.book_path);
        await this.load_books_surface_data();
        await this.load_tags_to_books();
        // 默认展示全部书籍
        this.selected_books = this.books_surface_data;

        const eventBus = useEventBusStore();
        eventBus.on('select_book_path', this.sel_book_path);
        eventBus.on('update_book_info',this.update_bookInfo);

        eventBus.on('new_book_data',this.create_book_done);

        eventBus.on('delete-book',this.delete_book);

        eventBus.on('simple-search',this.simple_search);

        eventBus.on('filt-search',this.filt_search);

        
        // 跳转到写作界面
        eventBus.on('to_write_view',this.to_write_view);

          
        // 离开写作页面时，保存书籍信息
        eventBus.on('save-book-info',this.upgrade_book_info);
      },
      methods: {

        sel_book_path(path) {
          this.book_path = path;
          console.log("writeshelf选择的书籍路径bookPath为：", this.base_config.bookPath);
          console.log("writeshelf选择的书籍路径为：", this.book_path);
        },

        upgrade_book_info(bookdata){
          const index = this.books_surface_data.findIndex(book => String(book.book_id) === bookdata[0]);
          if (index !== -1){
            this.books_surface_data[index].total_words = String(bookdata[1]);
            this.books_surface_data[index].book_last_read_chapter_id = bookdata[2];
            console.log("更新书籍信息成功！");
            console.log(this.books_surface_data[index]);
            this.saveBook_info();
          }
        },
        

        to_write_view(book_id){
          const book_data = this.books_surface_data.find(book => book.book_id === book_id);
            console.log("传递的数据是");
            console.log(book_data);
            this.$router.push({
            name: 'writePage',
            params: {
              book_id: book_data.book_id,
              book_name: book_data.book_name,
              last_node: book_data.book_last_read_chapter_id
            }
          });

          // 传递数据
          let bookdata = {
            id: String(book_data.book_id),
            total_words: book_data.total_words,
            book_status: book_data.book_status,
            book_create_time: book_data.book_create_time,
            book_finish_time: book_data.book_finish_time
          }
          const eventBus = useEventBusStore();
          eventBus.emit('start-write',bookdata);
        },

        saveBook_info(){
          // 更新后台数据
          const bookData = [this.book_path, this.books_surface_data, this.tags_to_books];
            window.pywebview.api.save_book_info(bookData).then(res => {
              if (res !== 1){
                this.$message({
                  message: '保存失败!',
                  type: 'error'
                });
              } 
            }).catch(error => {
              this.$message({
                  message: '程序异常啊!',
                  type: 'error'
                });
              throw error;
              
            })
        },

        async load_books_surface_data(){
          //console.log('加载书籍封面数据！');

          try {
            console.log("book_path is:");
            console.log(this.book_path);
            const res = await window.pywebview.api.load_books_surface_data(this.book_path)
              if (res !== 0){
                this.books_surface_data = res;
                this.max_book_id = this.books_surface_data.reduce((max, book) => Math.max(max, book.book_id), 0);
              } else {
                this.$message({
                  message: '书籍列表加载失败!',
                  type: 'error'
                });
              }
              
              //console.log(this.books_surface_data);
          } catch (error) {
            this.$message({
                  message: '书籍列表加载失败，异常!',
                  type: 'error'
                });
            throw error;
          }
          
        },

        async load_tags_to_books(){

          //console.log('加载书籍标签数据！');
          try {

            const res = await window.pywebview.api.load_tags_to_books(this.book_path);
            if (res !== 0){
              this.tags_to_books = res;
              this.book_tags = this.tags_to_books.map(item => item.tag);
            } else {
              this.$message({
                message: '书籍标签加载失败!',
                type: 'error'
              });
            }
            
            //console.log(this.tags_to_books);

          } catch (error) {
            this.$message({
                  message: '书籍标签加载失败，异常!',
                  type: 'error'
                });
            throw error;
          }
          
          
        },

        update_bookInfo(book_data){
          const index = this.books_surface_data.findIndex(item => item.book_id === book_data[0].book_id);
          if (index !== -1) {
            // 更新books_surface_data
            this.books_surface_data[index] = book_data[0];
            // 更新tags_to_books
            for ( const tag of book_data[0].book_tags){
              const index2 = this.tags_to_books.findIndex(item => item.tag === tag);
              if (index2 !== -1){
                this.tags_to_books[index2].books.push(book_data[0].book_id);
              } else{
                this.tags_to_books.push({'tag':tag,'books':[book_data[0].book_id]});
              }
            }
            for (const tag2 of book_data[1]){
              const index3 = this.tags_to_books.findIndex(item => item.tag === tag2);
              if (index3 !== -1){
                const index4 = this.tags_to_books[index3].books.findIndex(item => item === book_data[0].book_id);
                if (index4 !== -1){
                  this.tags_to_books[index3].books.splice(index4, 1);
                  if (this.tags_to_books[index3].books.length === 0){
                    this.tags_to_books.splice(index3, 1);
                  }
                }
              }
            }
            // 更新book_tags
            this.book_tags = this.tags_to_books.map(item => item.tag);

            // 更新后台数据
            // const bookData = [this.book_path, this.books_surface_data, this.tags_to_books];
            // window.pywebview.api.save_book_info(bookData).then(res => {
            //   if (res !== 1){
            //     this.$message({
            //       message: '保存失败!',
            //       type: 'error'
            //     });
            //   } 
            // }).catch(error => {
            //   this.$message({
            //       message: '程序异常!',
            //       type: 'error'
            //     });
            //   throw error;
              
            // })
            this.saveBook_info();

        }

        },

        simple_search(search_data){
          // console.log('搜索数据是：')
          // console.log(search_data)
          if (search_data[1] === ''){
            this.selected_books = this.books_surface_data;
            return;
          }
          this.selected_books = [];

          if (search_data[0] === 'bookName'){
            for (const item of this.books_surface_data){
              if (item.book_name.includes(search_data[1])){
                this.selected_books.push(item);
              }
            }

            // console.log('搜索结果是：')
            // console.log(this.selected_books)

          } else if (search_data[0] === 'bookAuthor'){
            for (const item of this.books_surface_data){
              if (item.book_author.includes(search_data[1])){
                this.selected_books.push(item);
              }
            }

            // console.log('搜索结果是：')
            // console.log(this.selected_books)

          } else {

            for (const item of this.tags_to_books){
              if (item.tag.includes(search_data[1])){
                for (const book_id of item.books){
                  const index = this.books_surface_data.findIndex(book => book.book_id === book_id);
                  if (index !== -1){
                    this.selected_books.push(this.books_surface_data[index]);
                  }
                }
                
              }
            }

            // console.log('搜索结果是：')
            // console.log(this.selected_books)

          }

        },

        filt_search(search_data){
          if (search_data.bookName === '' && search_data.bookAuthor === '' && search_data.bookStatus === '' && search_data.bookCreateTime === '' && search_data.bookTag.length === 0){
            this.selected_books = this.books_surface_data;
            return;
          }
          this.selected_books = [];

          let bookname_res = new Set();
          let bookauthor_res = new Set();
          let bookstatus_res = new Set();
          let bookcreatetime_res = new Set();
          let booktag_res = new Set();

          // 书名
          if (search_data.bookName !== ''){
            
            for (const item of this.books_surface_data){
              if (item.book_name.includes(search_data.bookName)){
                bookname_res.add(item.book_id);
              }
            }
          } else {
            bookname_res = new Set(this.books_surface_data.map(obj => obj.book_id));
          }

          // 作者
          if (search_data.bookAuthor !== ''){
            
            for (const item of this.books_surface_data){
              if (item.book_author.includes(search_data.bookAuthor)){
                bookauthor_res.add(item.book_id);
              }
            }
          } else {
            bookauthor_res = new Set(this.books_surface_data.map(obj => obj.book_id));
          }

          console.log('状态搜索数据是：')
            console.log(search_data.bookStatus)
          // 状态
          if (search_data.bookStatus !== ''){
            
            for (const item of this.books_surface_data){
              if (item.book_status === search_data.bookStatus){
                bookstatus_res.add(item.book_id);
              }
            }
          } else{
            bookstatus_res = new Set(this.books_surface_data.map(obj => obj.book_id));
          }

          // 创建时间
          if (search_data.bookCreateTime !== null){
            
            let daterange = search_data.bookCreateTime;
            
            for (const item of this.books_surface_data){
              let create_time = new Date(item.book_create_time);
              if (create_time >= daterange[0] && create_time <= daterange[1]){
                bookcreatetime_res.add(item.book_id);
              }
            }
          } else{
            bookcreatetime_res = new Set(this.books_surface_data.map(obj => obj.book_id));
          }

          // 标签
          if (search_data.bookTag.length !== 0){
            
            for (const item of this.tags_to_books){
              if (search_data.bookTag.includes(item.tag)){
                
                for (const book_id of item.books){
                  booktag_res.add(book_id);
                }
      
              }
            }
            
          } else{
            booktag_res = new Set(this.books_surface_data.map(obj => obj.book_id));

          }

          // 取所有条件的交集
          let final_res = intersection(bookname_res, bookauthor_res);
          final_res = intersection(final_res, bookstatus_res);
          final_res = intersection(final_res, bookcreatetime_res);
          final_res = intersection(final_res, booktag_res);
          for (const item of this.books_surface_data){
            if (final_res.has(item.book_id)){
              this.selected_books.push(item);
            }
          }

          
        },

  
        create_book(){
  
          this.isopen = true;
          
  
        },
        create_book_done(book_data){
          this.isopen = false;
          // this.max_book_id += 1;
          // book_data.book_id = this.max_book_id;
          // this.books_surface_data.push(book_data);
          // for (const tag of book_data.book_tags){
          //   const index1 = this.tags_to_books.findIndex(item => item.tag === tag);
          //   if (index1 === -1){
          //     this.tags_to_books.push({'tag':tag,'books':[book_data.book_id]});
          //   } else{
          //     const index = this.tags_to_books.findIndex(item => item.tag === tag);
          //     this.tags_to_books[index].books.push(book_data.book_id);
          //   }
          // }

          // console.log("tags_to_books is:");
          // console.log(this.tags_to_books);



          // this.book_tags = this.tags_to_books.map(item => item.tag);

          // const bookData = [this.book_path, this.books_surface_data, this.tags_to_books];
          // window.pywebview.api.create_new_book(bookData).then(res => {
          //   if (res !== 1){
          //     this.$message({
          //       message: '创建失败!',
          //       type: 'error'
          //     });
          //   } 
          // }).catch(error => {
          //   this.$message({
          //       message: '程序异常了!',
          //       type: 'error'
          //     });
          //     throw error;
              
          // })



          this.$nextTick(() => {
            

            this.max_book_id += 1;
          book_data.book_id = this.max_book_id;
          this.books_surface_data.push(book_data);
          for (const tag of book_data.book_tags){
            const index1 = this.tags_to_books.findIndex(item => item.tag === tag);
            if (index1 === -1){
              this.tags_to_books.push({'tag':tag,'books':[book_data.book_id]});
            } else{
              const index = this.tags_to_books.findIndex(item => item.tag === tag);
              this.tags_to_books[index].books.push(book_data.book_id);
            }
          }

          console.log("tags_to_books is:");
          console.log(this.tags_to_books);



          this.book_tags = this.tags_to_books.map(item => item.tag);
          this.book_path =  this.base_config.bookPath;
          console.log("new book_path is:", this.book_path);
          const bookData = [this.book_path, this.books_surface_data, this.tags_to_books];
          window.pywebview.api.create_new_book(bookData).then(res => {
            if (res !== 1){
              this.$message({
                message: '创建失败!',
                type: 'error'
              });
            } 
          }).catch(error => {
            this.$message({
                message: '程序异常了!',
                type: 'error'
              });
              throw error;
              
          })




          });



        },

        book_done(isopen){
          this.isopen = isopen;

        },

        delete_book(book_id){
          const index = this.books_surface_data.findIndex(item => item.book_id === book_id);
          console.log('delete bookid is:');
          console.log(book_id);
          if (index !== -1){
            let tags = this.books_surface_data[index].book_tags;
            this.books_surface_data.splice(index, 1);
            for (const tag of tags){
              const index1 = this.tags_to_books.findIndex(item => item.tag === tag);
              if (index1 !== -1){
                const index2 = this.tags_to_books[index1].books.findIndex(item => item === book_id);
                if (index2 !== -1){
                  this.tags_to_books[index1].books.splice(index2, 1);
                  if (this.tags_to_books[index1].books.length === 0){
                    this.tags_to_books.splice(index1, 1);
                    this.book_tags = this.tags_to_books.map(item => item.tag);
                  }
                }
              }
            }
            
            // 删除书籍
            let bookData = [this.book_path, String(book_id), this.books_surface_data, this.tags_to_books];
            window.pywebview.api.deleteBook(bookData).then(res => {

              if (res !== 1){
                this.$message({
                  message: '删除失败!',
                  type: 'error'
                });
              } 
            }).catch(error => {
              this.$message({
                  message: '程序异常!',
                  type: 'error'
                  })
                  throw error;
                  
            })


          }
        },

        
      },
    })
  </script>
  
  
  
    <style scoped>
  
  body, html {
      margin: 0;
    }

    .write-shelf-top {
        /* background-color: rgb(58, 9, 66); */
        height: 100%;
        display: flex;
        flex-direction: column;
        min-height: 0;
      }

      .header{
        position: relative;
        /* background-color: var(--color-background-mainview-shelf);; */
        display: flex;
        flex: 0 0 auto;
      }

      .main-shelf {
        position: relative;
        background-color: var(--color-background-mainview-shelf);
        flex: 1 1 auto;
        
        min-height: 0;
        margin-top: 2px;
      }

      .left_header{
        position: relative;
        width: 60%;
        /* background-color: #1abb08; */
      }
      .right_header{
        width: 40%;
        background-color: var(--color-background-mainview-shelf);
        display: flex;
        justify-content: flex-end;
        align-self: flex-start;
        
        padding-right: 20px;
        margin-left: 2px;
      }

      .right_btn{
        margin: 15px;
      }
      

      
      
      
      
    </style>