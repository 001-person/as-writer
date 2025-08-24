<template>
  
  <div class="mainView">
    
      <router-view ></router-view>
  </div>

</template>

<script>
import { useEventBusStore } from '../stores/eventBus';
  
  export default {
    data() {
    return {
      
      startTime:[],
      startData:[],
    }
  },

  provide(){
    return {
      startTime:this.startTime,
      startData:this.startData,
    }
  },

  beforeDestroy() {
    this.startTime = [];
    this.startData = [];
  },
  beforeUnmount() {
    // 清理事件总线监听
    const eventBus = useEventBusStore();
    eventBus.off('to_writeshelf', to_writeshelf);
  },

  mounted() {
    // eventBus.on('write', message => {
      
    //   this.$router.push('/write-page')
    // });
    const eventBus = useEventBusStore();
    
    eventBus.on('to_writeshelf' , this.to_writeshelf);
    // eventBus.on('data_statistics', message => {
      
    //   this.$router.push({name: 'dataStatistics',});
    // });
    // eventBus.on('read', message => {
      
    //   this.$router.push('/read-page')
    // });


    eventBus.on('start-write',book_data => {
      let index = this.startData.findIndex(item => item.id === book_data.id);
      if (index === -1){

        this.startData.push(book_data);
      }

      let index2 = this.startTime.findIndex(item => item.id === book_data.id);
      if (index2 === -1){
        let now_time = new Date();
        this.startTime.push({
          id: book_data.id,
          start_time:now_time
        });
      }

    });
  },
    methods: {
      to_writeshelf(data){
        this.$router.push({name: 'writeShelf',});
      }
      // writePage() {
      //   this.isshow = false
      //   // 使用 router.push 进行页面跳转
      //   this.$router.push('/write-page')
        
      // },

      // readPage() {
      //   this.isshow = false
      //   // 使用 router.push 进行页面跳转
      //   this.$router.push('/read-page')
        
      // }

    }
  }

</script>


<style scoped>

/* a {
  color: #b94254;
} */
.start {
  /* background-color: rgb(177, 167, 191); */
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 100vh; /* 或者设置一个固定的高度 */
}

.mainView {
  position: relative;
  background-color: rgb(12, 242, 242);
}
.page-turn{
  /* background-color: #060606; */
  position: relative;
  width: 100%;
  height: 100%;
  /* overflow: auto; */
}

</style>
