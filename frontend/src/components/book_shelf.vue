<template>
    <div class="shelf_container">
  
      <div class="main_view">
        
          
        <BookCard 
          v-for="(book, index) in books_surface_data" 
          :key="index" 
          :book_info="book" 
          :all_tags="all_tags"
          class="book_cards" />

      </div>
        <!-- <div class="shelf_footer">
            <el-pagination
                layout="prev, pager, next"
                :total="100"
                :hide-on-single-page="value">
            </el-pagination>

        </div> -->
        
    </div>
    
  </template>
  
<script>
  import { defineComponent, ref } from 'vue';
  import { useEventBusStore } from '../stores/eventBus';
  import BookCard from './book_card.vue'
  
  
    export default defineComponent({

        props:['books_surface_data','all_tags'],
  
        components: {
            BookCard,
        },
      data() {
        return {
          value: false,

        }
      },
      mounted() {
        // eventBus.on('update_book_info',(e)=>{
        //   eventBus.emit('update_book', e);

        //   });
        
      },
      methods: {

        
      },
    })
  </script>
  
  
  
    <style scoped>
  
  body, html {
      margin: 0;
    }

    .shelf_container {
        position: relative;
        /* background-color: rgb(11, 254, 254); */
        
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        
        
      }
      
      .shelf_footer {
        position: relative;
        /* background-color: #92f787; */
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
      }
      
      
      .main_view {
        padding: 20px;
        position: relative;
        /* background-color: var(--color-background); */
        flex: 1 1 auto;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 100px));
        gap:20px;
        
        overflow: auto;
        
        
        
      }

      .book_cards{
        position: relative;

      }
      
      
    </style>