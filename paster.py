# -*- coding: utf-8 -*-
"""
自动粘贴小工具
版本: 1.0
功能: 顺序粘贴账号列表，支持导入TXT，自动保存
"""
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import keyboard
import pyperclip
import time
import threading
import sys
import os
import json

class AutoPaster:
    def __init__(self, root):
        self.root = root
        root.title("自动粘贴小工具")
        root.geometry("450x350")
        root.attributes('-topmost', True)

        if getattr(sys, 'frozen', False):
            self.data_dir = os.path.dirname(sys.executable)
        else:
            self.data_dir = os.path.abspath(".")
        self.data_file = os.path.join(self.data_dir, "自动粘贴小工具数据.json")
        
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(top_frame, text="账号列表 (一行一个):").pack(side=tk.LEFT)
        
        self.import_btn = tk.Button(top_frame, text="导入", command=self.import_file,
                                    bg="#2196F3", fg="white", font=("微软雅黑", 9), 
                                    width=7, cursor="hand2")
        self.import_btn.pack(side=tk.RIGHT)
        
        self.text_area = scrolledtext.ScrolledText(root, height=12, font=("微软雅黑", 10))
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(root, text="点击软件外面，按 Ctrl+V 粘贴下一个", 
                fg="gray", font=("微软雅黑", 9)).pack(pady=5)
        
        self.status = tk.Label(root, text="准备就绪", fg="blue", font=("微软雅黑", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=3)
        
        self.current_index = 0
        self.lines = []
        self.running = True
        self.enabled = True
        
        root.bind('<FocusIn>', lambda e: self.set_enabled(False))
        root.bind('<FocusOut>', lambda e: self.set_enabled(True))
        self.text_area.bind('<FocusIn>', lambda e: self.set_enabled(False))
        self.text_area.bind('<FocusOut>', lambda e: self.set_enabled(True))
        self.text_area.bind('<KeyRelease>', lambda e: self.auto_save())
        
        self.load_data()
        self.listener_thread = threading.Thread(target=self.listen_key, daemon=True)
        self.listener_thread.start()
    
    def set_enabled(self, value):
        self.enabled = value
        self.status.config(text="准备就绪" if value else "编辑中...", 
                          fg="blue" if value else "orange")
    
    def auto_save(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump({"content": content}, f, ensure_ascii=False)
            except:
                pass
    
    def save_data(self):
        content = self.text_area.get("1.0", tk.END).strip()
        if not content:
            return
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({"content": content}, f, ensure_ascii=False)
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            self.status.config(text=f"已保存 {len(lines)} 个账号", fg="green")
        except:
            pass
    
    def load_data(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = data.get("content", "")
                if content:
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", content)
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    self.status.config(text=f"已加载 {len(lines)} 个账号", fg="green")
        except:
            pass
    
    def import_file(self):
        file_path = filedialog.askopenfilename(
            title="选择账号文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        
        encodings = ['utf-8', 'gbk', 'gb2312', 'ansi', 'cp1252', 'latin-1']
        content = None
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except:
                continue
        
        if content is None:
            messagebox.showerror("错误", "无法解析文件，请用 UTF-8 或 GBK 保存。")
            return
        
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        self.status.config(text=f"已导入 {len(lines)} 个账号", fg="green")
        self.save_data()
        
    def listen_key(self):
        def on_ctrl_v():
            if not self.enabled:
                return
            content = self.text_area.get("1.0", tk.END).strip()
            if not content:
                self.status.config(text="没有账号")
                keyboard.send('ctrl+v')
                return
            self.lines = [line.strip() for line in content.split('\n') if line.strip()]
            if not self.lines:
                keyboard.send('ctrl+v')
                return
            if self.current_index >= len(self.lines):
                self.current_index = 0
            current_line = self.lines[self.current_index]
            pyperclip.copy(current_line)
            time.sleep(0.05)
            keyboard.send('ctrl+v')
            self.status.config(text=f"已粘贴: {current_line} ({self.current_index + 1}/{len(self.lines)})")
            self.current_index += 1
        
        keyboard.add_hotkey('ctrl+v', on_ctrl_v, suppress=True)
        while self.running:
            time.sleep(0.1)
    
    def on_closing(self):
        self.running = False
        keyboard.unhook_all()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(".")
        root.iconbitmap(os.path.join(base_path, 'icon.ico'))
    except:
        pass
    app = AutoPaster(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()