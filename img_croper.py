import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IMAGE-CROPER")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)

        self.img = None
        self.photo = None
        self.save_folder = None  # 保存路径
        self.crop_mode = tk.StringVar(value="Select Mode")  # 存储当前裁剪模式
        self.crop_size = tk.StringVar(value="")  # 用户输入的裁剪大小
        self.crop_rect = None  # 当前绘制的裁剪框
        self.draw_start = None  # 记录绘制矩形的起点
        self.draw_rect = None  # 绘制矩形的对象
        self.mouse_preview_rect = None  # 鼠标预览矩形框

        self.setup_ui()

    def setup_ui(self):
        # 创建按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # 加载图片按钮
        load_button = tk.Button(button_frame, text="Load Image", command=self.load_image)
        load_button.pack(pady=10, side=tk.LEFT)

        # 保存路径按钮
        save_button = tk.Button(button_frame, text="Save Path", command=self.choose_save_folder)
        save_button.pack(pady=10, side=tk.LEFT)

        # 创建裁剪模式下拉菜单
        crop_mode_label = tk.Label(button_frame, text="Crop Mode:")
        crop_mode_label.pack(pady=10, side=tk.LEFT)
        crop_mode_dropdown = ttk.Combobox(
            button_frame, textvariable=self.crop_mode, values=["click crop", "draw crop"], state="readonly"
        )
        crop_mode_dropdown.pack(pady=10, side=tk.LEFT)
        crop_mode_dropdown.bind("<<ComboboxSelected>>", self.on_crop_mode_change)

        # 创建裁剪大小输入框和标签（默认隐藏）
        self.crop_size_label = tk.Label(button_frame, text="Crop Size:")
        self.crop_size_entry = tk.Entry(button_frame, textvariable=self.crop_size)
        self.crop_size_set_button = tk.Button(button_frame, text="Set", command=self.set_crop_size)
        self.crop_size_label.pack_forget()  # 初始状态隐藏
        self.crop_size_entry.pack_forget()  # 初始状态隐藏
        self.crop_size_set_button.pack_forget()  # 初始状态隐藏

        # 创建画布用于显示图片
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定画布大小调整事件
        self.canvas.bind("<Configure>", lambda event: self.update_image())
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # 绑定鼠标点击事件
        self.canvas.bind("<B1-Motion>", self.on_canvas_draw)  # 绑定鼠标拖动事件
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)  # 绑定鼠标释放事件
        self.canvas.bind("<Motion>", self.update_mouse_preview)  # 绑定鼠标移动事件
        self.root.bind("<Return>", self.save_cropped_image)  # 绑定回车键事件

    def on_crop_mode_change(self, event):
        if self.save_folder is None:
            messagebox.showwarning("warning", "choose the savepath first!")
            self.crop_mode.set("Select Mode")
            return

        if self.crop_mode.get() == "click crop":
            self.crop_size_label.pack(pady=10, side=tk.LEFT)
            self.crop_size_entry.pack(pady=10, side=tk.LEFT)
            self.crop_size_set_button.pack(pady=10, side=tk.LEFT)
            self.canvas.delete("crop_rect")  # 清除“draw crop”模式下的选框
            self.draw_rect = None  # 重置绘制矩形
        else:
            self.crop_size_label.pack_forget()
            self.crop_size_entry.pack_forget()
            self.crop_size_set_button.pack_forget()
            self.canvas.delete("crop_rect")  # 清除“click crop”模式下的选框
            self.crop_rect = None  # 重置点击模式裁剪框
            self.canvas.delete("mouse_preview_rect")  # 清除鼠标预览框

    def set_crop_size(self):
        if self.save_folder is None:
            messagebox.showwarning("warning", "choose the savepath first!")
            return
        crop_size = self.crop_size.get()
        if crop_size.isdigit():
            print(f"Crop size set to: {crop_size}")
            messagebox.showinfo("Crop Size", f"Size set to {crop_size}")
        else:
            messagebox.showwarning("Invalid Input", "Crop size must be a numeric value.")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.img = Image.open(file_path)
            self.update_image()

    def update_image(self):
        if self.img:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.img.size

            # 计算图片缩放比例以保持宽高比
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            resized_img = self.img.resize((new_width, new_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_img)
            self.canvas.image = self.photo  # 保持引用以避免垃圾回收
            self.canvas.delete("all")  # 清除之前的图片
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=self.photo)

    def update_mouse_preview(self, event):
        if self.crop_mode.get() == "click crop" and self.crop_size.get().isdigit():
            crop_size = int(self.crop_size.get())
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.img.size

            if self.photo:
                scale = min(canvas_width / img_width, canvas_height / img_height)
                scaled_size = crop_size * scale

                x1 = event.x - scaled_size // 2
                y1 = event.y - scaled_size // 2
                x2 = event.x + scaled_size // 2
                y2 = event.y + scaled_size // 2

                self.canvas.delete("mouse_preview_rect")
                #设置鼠标预览裁剪框的形状和颜色
                self.mouse_preview_rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, outline="blue", width=3, dash=(6, 2), tags="mouse_preview_rect"
                )

    def on_canvas_click(self, event):
        if self.crop_mode.get() == "click crop":
            crop_size = self.crop_size.get()
            if not crop_size.isdigit():
                messagebox.showwarning("Invalid Input", "Please set a numeric crop size before cropping.")
                return

            crop_size = int(crop_size)
            if self.photo:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                img_width, img_height = self.img.size

                # 计算图像与画布的缩放比例
                scale = min(canvas_width / img_width, canvas_height / img_height)

                # 点击位置在图像上的坐标
                click_x = int((event.x - (canvas_width - img_width * scale) / 2) / scale)
                click_y = int((event.y - (canvas_height - img_height * scale) / 2) / scale)

                # 计算裁剪框的坐标
                left = max(click_x - crop_size // 2, 0)
                right = min(click_x + crop_size // 2, img_width)
                top = max(click_y - crop_size // 2, 0)
                bottom = min(click_y + crop_size // 2, img_height)

                # 显示裁剪框
                self.canvas.delete("crop_rect")
                rect_left = (left * scale) + (canvas_width - img_width * scale) / 2
                rect_right = (right * scale) + (canvas_width - img_width * scale) / 2
                rect_top = (top * scale) + (canvas_height - img_height * scale) / 2
                rect_bottom = (bottom * scale) + (canvas_height - img_height * scale) / 2
                self.crop_rect = self.canvas.create_rectangle(
                    rect_left, rect_top, rect_right, rect_bottom, outline="red", width=2, tags="crop_rect"
                )
                self.crop_coords = (left, top, right, bottom)

        elif self.crop_mode.get() == "draw crop":
            if self.photo:
                # 删除旧的选区
                self.canvas.delete("crop_rect")
                self.crop_rect = None
                self.draw_start = (event.x, event.y)

    def on_canvas_draw(self, event):
        if self.crop_mode.get() == "draw crop" and self.draw_start:
            self.canvas.delete("draw_rect")
            self.draw_rect = self.canvas.create_rectangle(
                self.draw_start[0], self.draw_start[1], event.x, event.y, outline="blue", width=2, tags="draw_rect"
            )

    def on_canvas_release(self, event):
        if self.crop_mode.get() == "draw crop" and self.draw_start:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.img.size

            scale = min(canvas_width / img_width, canvas_height / img_height)

            # 转换起点和终点为图像坐标
            x1, y1 = self.draw_start
            x2, y2 = event.x, event.y

            rect_left = int((min(x1, x2) - (canvas_width - img_width * scale) / 2) / scale)
            rect_top = int((min(y1, y2) - (canvas_height - img_height * scale) / 2) / scale)
            rect_right = int((max(x1, x2) - (canvas_width - img_width * scale) / 2) / scale)
            rect_bottom = int((max(y1, y2) - (canvas_height - img_height * scale) / 2) / scale)

            # 确保裁剪框在图像范围内
            rect_left = max(0, rect_left)
            rect_top = max(0, rect_top)
            rect_right = min(img_width, rect_right)
            rect_bottom = min(img_height, rect_bottom)

            self.crop_coords = (rect_left, rect_top, rect_right, rect_bottom)
            self.canvas.delete("draw_rect")  # 清除蓝色框
            self.crop_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline="red", width=2, tags="crop_rect"
            )
            self.draw_start = None  # 重置绘制状态

    def save_cropped_image(self, event):
        if self.crop_rect and self.img and self.save_folder:
            left, top, right, bottom = self.crop_coords
            cropped_img = self.img.crop((left, top, right, bottom))

            # 生成唯一文件名
            counter = 1
            while True:
                cropped_file = os.path.join(self.save_folder, f"cropped_image_{counter}.png")
                if not os.path.exists(cropped_file):
                    break
                counter += 1

            cropped_img.save(cropped_file)
            print(f"Cropped image saved as {cropped_file}")

            # 更新选框颜色
            self.canvas.itemconfig(self.crop_rect, outline="green")
            messagebox.showinfo("Success", f"Cropped image saved as {cropped_file}")

    def choose_save_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.save_folder = folder_path
            print(f"Save folder selected: {self.save_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
