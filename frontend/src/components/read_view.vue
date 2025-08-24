<template>
    <div class="reading-area">
      <textarea v-model="novelContent" placeholder="开始阅读了..."></textarea>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        novelContent: '', // 小说内容绑定的数据
      };
    },
  };
  </script>
  
  <style scoped>
  .reading-area {
    width: 100%;
    height: 100%;
  }
  
  textarea {
    width: 100%;
    height: 100%;
    padding: 10px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: bisque;
  }
  </style>
  