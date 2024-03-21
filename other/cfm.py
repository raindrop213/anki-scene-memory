import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def split_filename(filename, pre_text, post_text):
    try:
        start = len(pre_text)
        if post_text:
            end = filename.rfind(post_text)
        else:
            end = len(filename)
        mid_text = filename[start:end]
        return pre_text, mid_text, post_text
    except:
        return None, None, None

def rename_files(folder_path, video_ext, video_pre, video_post, subtitle_ext, subtitle_pre, subtitle_post):
    try:
        # 获取所有文件
        files = os.listdir(folder_path)

        # 分类视频和字幕文件
        video_files = [f for f in files if f.endswith(video_ext)]
        subtitle_files = [f for f in files if f.endswith(subtitle_ext)]

        # 处理文件
        for video in video_files:
            _, mid_video, _ = split_filename(video, video_pre, video_post)

            for subtitle in subtitle_files:
                _, mid_subtitle, _ = split_filename(subtitle, subtitle_pre, subtitle_post)

                if mid_video and mid_subtitle and mid_video == mid_subtitle:
                    new_subtitle_name = f'{video_pre}{mid_video}{video_post}{subtitle_ext}'
                    os.rename(os.path.join(folder_path, subtitle), os.path.join(folder_path, new_subtitle_name))
        messagebox.showinfo("完成", "文件重命名完成！")
    except Exception as e:
        messagebox.showerror("错误", str(e))

# GUI界面
root = tk.Tk()
root.title("批量重命名工具")

# 设置布局
folder_path = tk.StringVar()
tk.Label(root, text="文件夹").grid(row=0, column=0)
tk.Entry(root, textvariable=folder_path, width=50).grid(row=0, column=1, columnspan=4)
tk.Button(root, text="浏览", command=lambda: folder_path.set(filedialog.askdirectory())).grid(row=0, column=5, sticky='EW')

video_ext = tk.StringVar()
video_pre = tk.StringVar()
video_post = tk.StringVar()
tk.Label(root, text="视频格式").grid(row=1, column=0)
tk.Entry(root, textvariable=video_ext).grid(row=1, column=1)
tk.Label(root, text="前").grid(row=1, column=2)
tk.Entry(root, textvariable=video_pre).grid(row=1, column=3)
tk.Label(root, text="后").grid(row=1, column=4)
tk.Entry(root, textvariable=video_post).grid(row=1, column=5)

subtitle_ext = tk.StringVar()
subtitle_pre = tk.StringVar()
subtitle_post = tk.StringVar()
tk.Label(root, text="字幕格式").grid(row=2, column=0)
tk.Entry(root, textvariable=subtitle_ext).grid(row=2, column=1)
tk.Label(root, text="前").grid(row=2, column=2)
tk.Entry(root, textvariable=subtitle_pre).grid(row=2, column=3)
tk.Label(root, text="后").grid(row=2, column=4)
tk.Entry(root, textvariable=subtitle_post).grid(row=2, column=5)

tk.Button(root, text="执行", command=lambda: rename_files(folder_path.get(), video_ext.get(), video_pre.get(), video_post.get(), subtitle_ext.get(), subtitle_pre.get(), subtitle_post.get())).grid(row=4, column=1, columnspan=4,sticky='EW')

# 视频格式下拉列表
video_formats = ['.mkv', '.mp4', '.avi', '.mov', '.wmv']  # 添加更多格式
video_ext_combobox = ttk.Combobox(root, textvariable=video_ext, values=video_formats)
video_ext_combobox.grid(row=1, column=1)
video_ext_combobox.set('.mkv')  # 设置默认值

# 字幕格式下拉列表
subtitle_formats = ['.ass', '.srt', '.sub']  # 添加更多格式
subtitle_ext_combobox = ttk.Combobox(root, textvariable=subtitle_ext, values=subtitle_formats)
subtitle_ext_combobox.grid(row=2, column=1)
subtitle_ext_combobox.set('.ass')  # 设置默认值

# 运行GUI
root.mainloop()
