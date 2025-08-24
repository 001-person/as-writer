// src/tinymce-plugins/custom_mark.js
tinymce.PluginManager.add('custom_mark', function(editor, url) {
    let vueInstance = editor.vueInstance;

    editor.myPlugin = {
        insertMark: function(id) {
            if (!vueInstance.current_id.includes('_')){
                return;
            }
            const mark = `<sub id="${id}" class="mymark">【&#x2618;】</sub>`;
            // 插入内容
            editor.insertContent(mark);
            // 插入空字符,使光标跳出sub 标签
            const mark2 = `<span class="text">&#8203;</span>`;
            editor.insertContent(mark2);

            console.log("发动法僧官");
            console.log(editor.getContent());
            vueInstance.novelContent = editor.getContent();
    
        }
    };
    

    // 监听快捷键 Ctrl + M (KeyCode for M is 77)
    // editor.on('keydown', function(e) {
    //     if (e.ctrlKey && e.keyCode === 77) { // Ctrl + M
    //         e.preventDefault();
    //         insertMark();
    //     } else if (e.ctrlKey && e.keyCode === 76) { // Ctrl + L
    //         e.preventDefault();
    //         showMarks();
    //     }
    // });
});