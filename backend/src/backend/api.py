#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import json
from tkinter import filedialog
import tkinter as tk
import webview
from ebooklib import epub
from bs4 import BeautifulSoup
import traceback
from datetime import datetime
from backend.writeShelfApi import *


class API():
    '''业务层API，供前端JS调用'''
    def __init__(self):
        self._window = None  # 注意下划线

    def set_window(self, window):
        self._window = window

    # 屏蔽 window 属性被 pywebview 反射
    def __getattr__(self, name):
        if name == 'window':
            raise AttributeError()
        return super().__getattribute__(name)

    def exit_app(self):
        """
        退出程序
        """
        self._window.destroy()
        sys.exit(0)
    
    def get_bookConfig(self):
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包
            BASE_DIR = os.path.dirname(sys.executable)
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        path = os.path.join(BASE_DIR, 'appConfig.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                config = json.load(file)
                path = config.get('bookPath', '')
                setting = config.get('settings')
                current_setting = setting.get(config.get('currentSetting', '0'), None)
                return {"path":path, "current_setting":current_setting}
        else:
            # 如果不存在配置文件，就创建一个默认的
            default_config = {
                "bookPath": "",
                "currentSetting": "0",
                "settings": {
                    "0": {}
                }
            }
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, ensure_ascii=False, indent=4)

            return {"path":"", "current_setting":"0"}
    
    def create_book_path(self):
        """
        弹出文件夹选择框，选择书籍存储路径
        """
        folder_path = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if folder_path:
            # 检查选择的路径是否存在
            if os.path.exists(folder_path[0]):
                # 检查是否为目录
                if os.path.isdir(folder_path[0]):
                    # 保存路径到配置文件
                    if getattr(sys, 'frozen', False):
                        # 打包后
                        BASE_DIR = os.path.dirname(sys.executable)
                    else:
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(BASE_DIR, 'appConfig.json')
                    # 1. 读取
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                    # 2. 修改路径
                    config['bookPath'] = folder_path[0]

                    # 3. 写回
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    return folder_path[0]
                else:
                    return "0"
            else:
                return "0"
        else:
            return ""
        
    def saveChapter(self, chapterdata):
        """
        chpterdata共4个元素，书籍存储路径，书籍id，章节id，章节内容
        """
        # 检查书籍存储路径是否已设置好了
        if os.path.exists(chapterdata[0]):
            if os.path.isdir(chapterdata[0]):
                # 判断是否有书籍id做名称的文件夹，如果没有就先创建这个文件夹
                if not os.path.exists(os.path.join(chapterdata[0], chapterdata[1])):
                    os.mkdir(os.path.join(chapterdata[0], chapterdata[1]))

                # 写入书籍
                file_path = os.path.join(chapterdata[0],chapterdata[1], chapterdata[2]+'.html')
                with open(file_path,'w', encoding='utf-8') as file:
                    file.write(chapterdata[3])
            
            else:
                return 0
        else:
            return 0
        return 1
    
    def saveCatalog(self,catalog):
        """
        catalog共3个元素，书籍存储路径，书籍id，目录数据
        """
        # 检查书籍存储路径是否已设置好了
        if os.path.exists(catalog[0]):
            if os.path.isdir(catalog[0]):
                # 判断是否有书籍id做名称的文件夹，如果没有就先创建这个文件夹
                if not os.path.exists(os.path.join(catalog[0], catalog[1])):
                    os.mkdir(os.path.join(catalog[0], catalog[1]))

                # 写入书籍目录
                file_path = os.path.join(catalog[0],catalog[1], 'catalog.json')
                with open(file_path,'w',encoding="utf-8") as json_file:
                    json.dump(catalog[2],json_file,ensure_ascii=False)
            
            else:
                return 0
        else:
            return 0
        return 1
    
    def loadBook(self, bookdata):
        """
        bookdata:[书籍存储路径,书籍id]
        """
        catalog_data = []
        chapter_data = []
        book_path = os.path.join(bookdata[0], bookdata[1])
        print("the bookpath is:",book_path)
        if os.path.exists(book_path):
            if os.path.isdir(book_path):
                catalog = os.path.join(book_path, 'catalog.json')
                try:
                    with open(catalog, 'r', encoding="utf-8") as json_file:
                        catalog_data = json.load(json_file)
                        # print(catalog_data)
                        for volume in catalog_data[0]["children"]:
                            for chapter in volume["children"]:
                                
                                chapter_path = os.path.join(book_path, chapter["id"]+'.html')
                                #print(chapter_path)
                                with open(chapter_path, 'r', encoding='utf-8') as file:
                                    
                                    content = file.read()
                                    #print(content)
                                    chapter_data.append({'id':chapter["id"],'content':content})
                except Exception:
                    print('目录文件读取失败')
                    return 0
            else:
                print('找不到书籍')
                return 0
        else:
            print('找不到书籍')
            return 0
        return catalog_data, chapter_data
    
    def deleteChapter(self, chapter_index):
        """
        chapter_index:[书籍存储路径,书籍id,章节id]
        """
        chapter_path = os.path.join(chapter_index[0], chapter_index[1], chapter_index[2]+'.html')
        try:
            if os.path.exists(chapter_path):
                os.remove(chapter_path)
                return 1
            else:
                # 找不到文件说明已经删除或还没保存，也返回1
                return 1
        except Exception:
            return 0
    
    def exportTxt(self,bookdata):
        """
        bookdata:[书籍存储路径,书籍id, 书名]
        """
        bookpath = os.path.join(bookdata[0], bookdata[1])
        if os.path.exists(bookpath):
            if os.path.isdir(bookpath):
                table_path = os.path.join(bookpath, 'catalog.json')
                try:
                    catalog_data = []
                    with open(table_path, 'r', encoding="utf-8") as json_file:
                        catalog_data = json.load(json_file)
                    
                    #弹出文件夹选择框
                    file_path =  self._window.create_file_dialog(webview.SAVE_DIALOG, directory=bookpath, file_types=("Text files (*.txt)",), save_filename=bookdata[2]+'.txt')
                    
                    if not file_path:
                        return 2
                        
                    # 导出txt
                    with open(file_path,'w',encoding='utf-8') as file_txt:
                        for volume in catalog_data[0]['children']:
                            volume_name = volume['label']
                            for index,chapter in enumerate(volume['children']):
                                chapter_name = chapter['label']
                                chapter_path = os.path.join(bookpath, chapter['id']+'.html')
                                content = ''
                                with open(chapter_path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                
                                # 获取纯文本
                                soup = BeautifulSoup(content, 'lxml')
                                content = soup.get_text()
                                
                                # 写入文件
                                if index == 0:
                                    file_txt.write(volume_name+'\n')
                                file_txt.write(chapter_name+'\n')
                                file_txt.write(content+'\n\n')
                    return 1

                                    
                except Exception:
                    print('目录文件读取失败')
                    print(Exception)
                    return 0
            else:
                print('找不到书籍')
                return 0
        else:
            print('找不到书籍')
            return 0
        
    # 导出epub
    def exportEpub(self,bookdata):
        """
        bookdata:[书籍存储路径,书籍id, 书名]
        """
        bookpath = os.path.join(bookdata[0], bookdata[1])
        if os.path.exists(bookpath):
            if os.path.isdir(bookpath):
                table_path = os.path.join(bookpath, 'catalog.json')
                try:
                    catalog_data = []
                    with open(table_path, 'r', encoding="utf-8") as json_file:
                        catalog_data = json.load(json_file)
                    
                    #弹出文件夹选择框
                    file_path =  self._window.create_file_dialog(webview.SAVE_DIALOG, directory=bookpath, file_types=("Epub files (*.epub)",), save_filename=bookdata[2]+'.epub')
                    
                    if not file_path:
                        return 2
                    
                    book = epub.EpubBook()

                    # 获取当前时间
                    current_time = datetime.now()
                    # 将当前时间格式化为字符串，这里使用ISO 8601标准格式
                    formatted_time = current_time.isoformat()
                    book.set_identifier(f'bookhub.publish.{formatted_time}')
                    book.set_title(bookdata[2])
                    book.set_language('zh-CN')
                    book.add_author('青衫')
                    # print("恢复数据返回数据：")
                    # nav_doc = epub.EpubNav()
                    # print(nav_doc)
                    # book.add_item(nav_doc)
                    book.toc = []


                    for index1,volume in enumerate(catalog_data[0]['children']):
                
                        vol = epub.EpubHtml(title=volume['label'], file_name=volume['id']+'.xhtml', lang='zh-CN')
                        vol.content = volume['label']
                        book.add_item(vol)
                        book.toc.append((vol, []))
                        for chapter in volume['children']:
                            
                            chap = epub.EpubHtml(title=chapter['label'], file_name=chapter['id']+'.xhtml', lang='zh-CN')
                            chapter_path = os.path.join(bookpath, chapter['id']+'.html')
                            content = ''
                            with open(chapter_path, 'r', encoding='utf-8') as file:
                                content = file.read()
                            if content == '':
                                content = '<p></p>'
                            chap.content = content
                            book.add_item(chap)
                            book.toc[index1][1].append(chap)

                    # 阅读顺序
                    
                    spine_list = []
                    for item in book.toc:
                        spine_list.append(item[0])
                        spine_list.extend(item[1])

                    book.spine = ['nav'] + spine_list
                    
                    # 生成epub
                    book.add_item(epub.EpubNcx())
                    book.add_item(epub.EpubNav())
                    
                    epub.write_epub(file_path, book)
                    
                    return 1
                    
                except Exception:
                    print('目录文件读取失败')
                    # 输出报错信息
                    traceback.format_exc()
                    
                    return 0
            else:
                print('找不到书籍')
                return 0
        else:
            print('找不到书籍')
            return 0
        
    # 保存大纲数据
    def save_outline(self, outline_data):
        """
        outline_data = [
            书籍存储路径,
            书籍id,
            大纲数据:[{id:xxx,title:xxx,content:xxx}]
        ]
        """
        # 检查书籍存储路径是否已设置好了
        if os.path.exists(outline_data[0]):
            if os.path.isdir(outline_data[0]):
                # 判断是否有书籍id做名称的文件夹，如果没有就先创建这个文件夹
                if not os.path.exists(os.path.join(outline_data[0], outline_data[1])):
                    os.mkdir(os.path.join(outline_data[0], outline_data[1]))
                
                # 写入文件
                file_path = os.path.join(outline_data[0],outline_data[1], 'outline.json')
                with open(file_path,'w',encoding="utf-8") as json_file:
                    json.dump(outline_data[2],json_file,ensure_ascii=False)
            
            else:
                return 0
        else:
            return 0
        return 1
    
    # 加载大纲文件
    def load_outline(self, outline_data):
        """
        outline_data = [
            书籍存储路径,
            书籍id,
        ]
        """
        outline_path = os.path.join(outline_data[0], outline_data[1])
        if os.path.exists(outline_path):
            if os.path.isdir(outline_path):
                outline_name = os.path.join(outline_path, 'outline.json')
                if not os.path.exists(outline_name):
                    return []
                with open(outline_name, 'r', encoding="utf-8") as json_file:
                    outline = json.load(json_file)
                return outline
            else:
                return 0
        else:
            return 0
    
    # 导出大纲数据
    def export_outline(self, outline_data):
        """
        outline_data = [
            书名,
            大纲数据:{id:xxx,title:xxx,content:xxx}
        ]
        """
        try:
            # 弹出文件夹选择框
            root = tk.Tk()
            root.withdraw() # 隐藏tk根窗口
            root.iconbitmap(None)
            folder_path = filedialog.askdirectory(parent=root, title='请选择导出目录')
            root.destroy()
            if folder_path == '':
                return 2
            
            # 导出md文件
            file_name = outline_data[0]+outline_data[1]['title']+'.md'
            file_path = os.path.join(folder_path, file_name)
            
            with open(file_path,'w',encoding='utf-8') as f:
                f.write(outline_data[1]['content'])

            return 1
        except Exception:
            print('目录文件读取失败')
            # 输出报错信息
            traceback.format_exc()
            return 0
        
    
    def load_books_surface_data(self, bookpath):
        try:
            return get_book_surface_data(bookpath)
        except Exception:
            print('目录文件读取失败')
            return 0
        
    def load_tags_to_books(self, bookpath):
        try:
            return get_tags_to_books(bookpath)
        except Exception:
            print('目录文件读取失败api')
            # 输出报错信息
            traceback.format_exc()
            return 0
        
        
    def save_book_info(self, bookData):
        try:
            return save_book_data(bookData)
        except Exception:
            print('目录文件读取失败')
            return 0
        
    def create_new_book(self, bookData):
        # try:
        return create_new_book_api(bookData)
        # except Exception:
        #     print('目录文件读取失败ss')
        #     return 0
    
    def deleteBook(self, bookData):
        return delete_book_api(bookData)
    
    def addmark(self, markData):
        """
        markData = [
            书籍存储路径,
            书籍id,
            书签数据:[{id:xxx,content:xxx}]
        ]
        """
        book_path = os.path.join(markData[0], markData[1])
        if os.path.exists(book_path):
            if os.path.isdir(book_path):
                mark_path = os.path.join(book_path, 'marks.json')
                with open(mark_path, 'w', encoding="utf-8") as json_file:
                    json.dump(markData[2],json_file,ensure_ascii=False)
                return 1
            else:
                return 0
        else:
            return 0
        
    # 加载大纲文件
    def load_marks(self, mark_data):
        """
        mark_data = [
            书籍存储路径,
            书籍id,
        ]
        """
        book_path = os.path.join(mark_data[0], mark_data[1])
        if os.path.exists(book_path):
            if os.path.isdir(book_path):
                mark_path = os.path.join(book_path, 'marks.json')
                if not os.path.exists(mark_path):
                    return []
                with open(mark_path, 'r', encoding="utf-8") as json_file:
                    marks = json.load(json_file)
                return marks
            else:
                return 0
        else:
            return 0