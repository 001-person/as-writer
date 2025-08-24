import os
import json
from tkinter import filedialog
import shutil


def get_book_surface_data(bookpath):
    """
    获取书籍列表
    :param bookpath: 书籍列表路径
    :return: 书籍列表
    [
        {
            "book_id": 1,
            "book_name": "书名",
            "book_author": "作者",
            "book_status": "完结/未完结",
            "total_words": "总字数",
            "book_create_time": "创建时间",
            "book_finish_time": "完结时间",
            "book_intro": "简介",
            "book_cover":"",
            "book_tags": ['标签列表',],
            "book_last_read_chapter_id": "上次阅读章节的id",
        },
    ]
    """
    if bookpath == "请设置书籍路径":
        return []
    if os.path.exists(bookpath):
        if os.path.isdir(bookpath):
            books_surface_data_path = os.path.join(bookpath, 'books_surface_data.json')
            if not os.path.exists(books_surface_data_path):
                init_books_surface_data = [
                    # {
                    #     "book_id": '1',
                    #     "book_name": "西游记",
                    #     "book_author": "吴承恩",
                    #     "book_status": "未完结",
                    #     "total_words": "12000",
                    #     "book_create_time": "2024-06-15",
                    #     "book_finish_time": "2024-06-19",
                    #     "book_intro": "西天取经，家喻户晓的故事。",
                    #     "book_cover":r"C:\Users\青衫\Pictures\月岛雯2.png",
                    #     "book_tags": ['玄幻','历史'],
                    #     "book_last_read_chapter_id": "上次阅读章节的id",
                    # },
                ]
                with open(books_surface_data_path, 'w', encoding='utf-8') as f:
                    json.dump(init_books_surface_data,f,ensure_ascii=False)
                return init_books_surface_data
            with open(books_surface_data_path, 'r', encoding='utf-8') as f:
                book_surface_data = json.load(f)
            return book_surface_data
        return 0
    return 0

def get_tags_to_books(bookpath):
    """
    获取标签列表
    :param bookpath: 书籍列表路径
    :return: 
    [
        {
            "tag":"标签名",
            "books":["book_id",]
        },
    ]

    """
    if bookpath == "请设置书籍路径":
        return []
    if os.path.exists(bookpath):
        if os.path.isdir(bookpath):
            tags_to_books_path = os.path.join(bookpath, 'tags_to_books.json')
            if not os.path.exists(tags_to_books_path):
                with open(tags_to_books_path, 'w', encoding='utf-8') as f:
                    init_tags_to_books = [
                        {
                            "tag":"武侠",
                            "books":[]
                        },
                        {
                            "tag":"玄幻",
                            "books":[]
                        },
                        {
                            "tag":"历史",
                            "books":[]
                        },
                        {
                            "tag":"科幻",
                            "books":[]
                        },
                        {
                            "tag":"修仙",
                            "books":[]
                        },
                        {
                            "tag":"都市",
                            "books":[]
                        },
                    ]
                    json.dump(init_tags_to_books,f,ensure_ascii=False)
                return init_tags_to_books
            with open(tags_to_books_path, 'r', encoding='utf-8') as f:
                tags_to_books = json.load(f)
            return tags_to_books
        return 0
    return 0

def save_book_data(bookData):
    """
    保存书籍信息
    :param bookData:[bookpath,book_surface_data,tags_to_books]
    :return:
    """
    bookpath = bookData[0]
    if os.path.exists(bookpath):
        if os.path.isdir(bookpath):
            books_surface_data_path = os.path.join(bookpath, 'books_surface_data.json')
            tags_to_books_path = os.path.join(bookpath, 'tags_to_books.json')
            
            with open(books_surface_data_path, 'w', encoding='utf-8') as f:
                    json.dump(bookData[1],f,ensure_ascii=False)

            with open(tags_to_books_path, 'w', encoding='utf-8') as f:
                json.dump(bookData[2],f,ensure_ascii=False)
            return 1
        return 0
    return 0


def create_new_book_api(bookData):

    res = save_book_data(bookData)
    if res == 0:
        return 0
    bookpath = bookData[0]
    new_book = bookData[1][-1]
    book_id = str(new_book['book_id'])
    new_book_path = os.path.join(bookpath, book_id)
    if not os.path.exists(new_book_path):
        print('创建了新文件夹',new_book_path)
        os.mkdir(new_book_path)
    # 初始化书籍目录文件
    file_path = os.path.join(new_book_path, 'catalog.json')
    catalog = [
        {
            'id':'0',
          'label': new_book['book_name'],
          'children': [{
            'id':'1',
            'label': '第一卷',
            'children': [{
              'id':'1_1',
              'label': '第一章'
            }]
          }]
        }, 
    ]
    with open(file_path,'w',encoding="utf-8") as json_file:
        json.dump(catalog,json_file,ensure_ascii=False)

    # 初始化书籍内容文件
    file_path = os.path.join(new_book_path,'1_1.html')
    with open(file_path,'w', encoding='utf-8') as file:
        file.write('')
    
    return 1

def delete_book_api(bookData):
    """
    删除书籍
    :param bookData:[bookpath,book_id,book_surface_data,tags_to_books]
    :return:
    """
    bookData1 = [bookData[0], bookData[2], bookData[3]]
    res = save_book_data(bookData1)
    if res == 0:
        return 0
    bookpath = os.path.join(bookData[0],bookData[1])
    print('bookpath is:')
    print(bookpath)
    if os.path.exists(bookpath):
        if os.path.isdir(bookpath):
            
            shutil.rmtree(bookpath)
    return 1