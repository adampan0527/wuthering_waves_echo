import tkinter as tk
from tkinter import messagebox, ttk
import time
from collections import deque, defaultdict
import json
import os


class DataRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("鸣潮声骸强化词条统计")

        self.data_counts = defaultdict(int)
        self.last_operations = deque(maxlen=20)
        self.load_data()

        self.create_widgets()
        self.sort_var.set("降序")
        self.update_probabilities()

    def create_widgets(self):
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        self.data_buttons = {}
        self.data_name = ['','暴击率', '暴击伤害', '小防御', '大防御',
                     '小生命', '大生命', '小攻击', '大攻击',
                     '共鸣效率', '共鸣解放', '共鸣技能', '普通攻击', '重击']
        for i in range(1, 14):
            data_button = tk.Button(self.buttons_frame, text=self.data_name[i], command=lambda t=i: self.add_data(self.data_name[t]))
            data_button.grid(row=(i - 1) // 4, column=(i - 1) % 4, padx=5, pady=5)
            self.data_buttons[self.data_name[i]] = data_button

        self.revert_button = tk.Button(self.root, text="回退上一条操作", command=self.revert_last)
        self.revert_button.pack(pady=5)

        self.save_button = tk.Button(self.root, text="保存", command=self.save_data)
        self.save_button.pack(pady=5)

        self.sort_var = tk.StringVar(value="降序")
        self.sort_menu = ttk.Combobox(self.root, textvariable=self.sort_var, values=["升序", "降序", "不排序"])
        self.sort_menu.pack(pady=5)
        self.sort_menu.bind("<<ComboboxSelected>>", lambda _: self.update_probabilities())

        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.probabilities_tree = ttk.Treeview(self.table_frame, columns=("name", "count", "probability"), show="headings", height=14)
        self.probabilities_tree.heading("name", text="声骸词条")
        self.probabilities_tree.heading("count", text="出现次数")
        self.probabilities_tree.heading("probability", text="出现比例")

        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.probabilities_tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.probabilities_tree.xview)
        self.probabilities_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.probabilities_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

    def add_data(self, data_type):
        current_time = time.time()
        if len(self.last_operations) == self.last_operations.maxlen:
            operation_time, operation_data_type = self.last_operations.popleft()
            self.data_counts[operation_data_type] -= 1
        self.last_operations.append((current_time, data_type))
        self.data_counts[data_type] += 1
        self.update_probabilities()

    def revert_last(self):
        if not self.last_operations:
            messagebox.showinfo("Info", "没有操作可以回退")
            return

        last_time, last_data_type = self.last_operations.pop()
        self.data_counts[last_data_type] -= 1
        self.update_probabilities()

    def save_data(self):
        save_file = "data_operations.json"
        try:
            if os.path.exists(save_file):
                with open(save_file, "r") as file:
                    saved_operations = json.load(file)
            else:
                saved_operations = []

            for operation in self.last_operations:
                if operation not in saved_operations:
                    saved_operations.append(operation)

            with open(save_file, "w") as file:
                json.dump(saved_operations, file)

            messagebox.showinfo("Info", "数据保存成功")
        except Exception as e:
            messagebox.showerror("Error", f"保存数据失败: {e}")

    def load_data(self):
        save_file = "data_operations.json"
        if os.path.exists(save_file):
            try:
                with open(save_file, "r") as file:
                    saved_operations = json.load(file)
                for operation in saved_operations:
                    _, data_type = operation
                    self.last_operations.append(operation)
                    self.data_counts[data_type] += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def update_probabilities(self):
        total_counts = sum(self.data_counts.values())
        for row in self.probabilities_tree.get_children():
            self.probabilities_tree.delete(row)

        data_list = [(self.data_name[i], self.data_counts[self.data_name[i]]) for i in range(1, 14)]
        data_list.append(('总强化次数', total_counts))

        if self.sort_var.get() == "升序":
            data_list.sort(key=lambda x: x[1] / total_counts if total_counts > 0 else 0)
        elif self.sort_var.get() == "降序":
            data_list.sort(key=lambda x: x[1] / total_counts if total_counts > 0 else 0, reverse=True)

        for data_type, count in data_list:
            probability = count / total_counts if total_counts > 0 else 0
            self.probabilities_tree.insert("", tk.END, values=(data_type, count, f"{probability:.2%}"))


if __name__ == "__main__":
    root = tk.Tk()
    app = DataRecorderApp(root)
    root.mainloop()
