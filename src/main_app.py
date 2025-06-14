import customtkinter as ctk
from tkinter import filedialog, messagebox # Added messagebox for API key prompt
from PIL import Image, ImageTk
from attributes import ATTRIBUTE_DATA
from ocr_service import perform_ocr
from attribute_parser import parse_ocr_text
from collections import defaultdict
import json
import os
from config_manager import load_api_key, save_api_key # New import

STATS_FILE_PATH = "data/echo_stats.json"

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("鸣潮声骸词条统计器")
        self.geometry("800x750") # Increased height for API key input
        self.image_path = None
        self.attribute_statistics = defaultdict(int)

        # Load API Key
        self.api_key = load_api_key()
        if not self.api_key:
            self.api_key = "YOUR_API_KEY_HERE" # Default placeholder
            # Optionally, inform user or prompt for key here if first time
            # For now, status bar will reflect it.

        self.load_statistics() # Load attribute statistics

        # --- API Key Configuration Frame ---
        api_key_frame = ctk.CTkFrame(self)
        api_key_frame.pack(pady=(10,0), padx=10, fill="x")

        ctk.CTkLabel(api_key_frame, text="OCR.space API Key:").pack(side="left", padx=(5,5))
        self.api_key_entry = ctk.CTkEntry(api_key_frame, width=300)
        self.api_key_entry.pack(side="left", padx=(0,5), expand=True, fill="x")
        self.api_key_entry.insert(0, self.api_key)

        self.save_api_key_button = ctk.CTkButton(api_key_frame, text="保存 API Key", command=self.gui_save_api_key)
        self.save_api_key_button.pack(side="left", padx=(0,5))

        # --- Top Controls Frame (Image Load, Stats Save/Clear) ---
        top_controls_frame = ctk.CTkFrame(self)
        top_controls_frame.pack(pady=10, padx=10, fill="x")

        image_frame = ctk.CTkFrame(top_controls_frame)
        image_frame.pack(side="left", expand=True, fill="x", padx=(0,10))

        self.image_display_label = ctk.CTkLabel(image_frame, text="No image selected.", height=50)
        self.image_display_label.pack(side="left", padx=(0,10), expand=True, fill="x")

        self.load_button = ctk.CTkButton(image_frame, text="载入图片并识别", command=self.trigger_image_processing)
        self.load_button.pack(side="left")

        stats_buttons_frame = ctk.CTkFrame(top_controls_frame) # Renamed for clarity
        stats_buttons_frame.pack(side="left")

        self.save_stats_button = ctk.CTkButton(stats_buttons_frame, text="保存统计", command=self.save_statistics) # Renamed variable
        self.save_stats_button.pack(side="top", pady=(0,5))

        self.clear_button = ctk.CTkButton(stats_buttons_frame, text="清空统计", command=self.clear_statistics)
        self.clear_button.pack(side="top")

        # --- Statistics Display Textbox ---
        self.stats_display = ctk.CTkTextbox(self, width=780, height=450) # Adjusted height
        self.stats_display.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self, text="就绪. (Ready.)", height=20) # anchor="w"
        self.status_bar.pack(pady=(0,5), padx=10, fill="x")

        self.update_stats_display() # Initial display
        if self.api_key == "YOUR_API_KEY_HERE":
            self.status_bar.configure(text="提示: 请在上方输入框配置你的 OCR.space API Key。(Hint: Configure your OCR.space API Key above.)")


    def gui_save_api_key(self):
        new_key = self.api_key_entry.get()
        if not new_key:
            self.status_bar.configure(text="API Key 不能为空。(API Key cannot be empty.)")
            messagebox.showwarning("API Key Error", "API Key field cannot be empty.")
            return

        if save_api_key(new_key):
            self.api_key = new_key
            self.status_bar.configure(text="API Key 已保存。(API Key saved.)")
            messagebox.showinfo("API Key", "API Key saved successfully.")
        else:
            self.status_bar.configure(text="API Key 保存失败。(Failed to save API Key.)")
            messagebox.showerror("API Key Error", "Failed to save API Key. Check console for details.")

    def trigger_image_processing(self):
        if self.api_key == "YOUR_API_KEY_HERE" or not self.api_key:
            self.status_bar.configure(text="错误: 请先配置有效的 API Key。(Error: Please configure a valid API Key.)")
            messagebox.showerror("API Key Missing", "Please configure your OCR.space API Key before processing images.")
            return

        self.load_image()
        if self.image_path:
            self.process_image_with_ocr()

    def load_image(self):
        filepath = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=(("PNG files", "*.png"), ("JPG files", "*.jpg;*.jpeg"), ("All files", "*.*"))
        )
        if filepath:
            self.image_path = filepath
            self.image_display_label.configure(text=f"Selected: {filepath.split('/')[-1]}")
            self.status_bar.configure(text=f"图片已选择: {filepath.split('/')[-1]}")
        else:
            self.image_path = None # Reset if no file chosen
            self.image_display_label.configure(text="No image selected.")
            self.status_bar.configure(text="未选择图片.")

    def process_image_with_ocr(self):
        if not self.image_path:
            self.status_bar.configure(text="错误：请先载入图片。")
            self.stats_display.delete("0.0", "end")
            self.stats_display.insert("0.0", "错误：请先载入图片。 (Error: Please load an image first.)")
            return

        self.status_bar.configure(text=f"正在识别图片: {self.image_path.split('/')[-1]}...")
        self.stats_display.delete("0.0", "end")
        self.stats_display.insert("0.0", f"正在识别图片: {self.image_path.split('/')[-1]}...\n(Processing image: {self.image_path.split('/')[-1]}...)\n")
        self.update()

        # Use self.api_key
        ocr_text_result = perform_ocr(self.image_path, self.api_key)

        current_content = self.stats_display.get("0.0", "end").strip() + "\n\n"
        self.stats_display.delete("0.0", "end")
        self.stats_display.insert("0.0", current_content)

        if ocr_text_result and not ocr_text_result.startswith("OCR Error:") and not ocr_text_result.startswith("Network Error:") and not ocr_text_result.startswith("Error:"):
            self.stats_display.insert("end", f"原始识别文字 (Raw OCR Text):\n{ocr_text_result}\n\n")

            found_attributes_in_image = parse_ocr_text(ocr_text_result)

            if not found_attributes_in_image:
                self.stats_display.insert("end", "图片中未找到有效词条。\n(No valid attributes found in the image.)\n")
                self.status_bar.configure(text="识别完成，未找到有效词条。")
            else:
                current_image_summary = []
                for attr, count in found_attributes_in_image.items():
                    self.attribute_statistics[attr] += count
                    current_image_summary.append(f"{attr}: {count}")
                self.stats_display.insert("end", f"本次识别到的词条 (Attributes found in this image):\n  {', '.join(current_image_summary)}\n\n")
                self.status_bar.configure(text="识别成功！已更新统计数据。")

            self.update_stats_display(from_process=True)
        else:
            self.stats_display.insert("end", f"识别失败 (Recognition Failed):\n{ocr_text_result}\n")
            self.status_bar.configure(text="识别失败.")

    def update_stats_display(self, from_process=False):
        current_content_for_stats = ""
        if from_process:
            current_content_for_stats = self.stats_display.get("0.0", "end").strip()
            if current_content_for_stats: # Add newlines if there's existing text
                 current_content_for_stats += "\n\n"

        self.stats_display.delete("0.0", "end") # Clear before re-populating

        display_text = ""
        if not self.attribute_statistics:
            display_text = "当前统计为空。请载入图片进行识别。\n(Current statistics are empty. Load an image to begin.)"
        else:
            header = "--- 累计词条统计 (Cumulative Attribute Statistics) ---\n"
            display_text += header

            total_attributes_count = sum(self.attribute_statistics.values())

            sorted_attributes = sorted(self.attribute_statistics.items(), key=lambda item: item[1], reverse=True)

            for attr, count in sorted_attributes:
                percentage = (count / total_attributes_count * 100) if total_attributes_count > 0 else 0
                display_text += f"  {attr}: {count} ({percentage:.2f}%)\n"

            display_text += f"\n--- 总计 (Total) ---\n  所有词条总数 (Total number of all attributes): {total_attributes_count}\n"

        # Prepend existing content (like OCR raw text) if this is called from process_image_with_ocr
        final_display_text = current_content_for_stats + display_text
        self.stats_display.insert("0.0", final_display_text)


    def clear_statistics(self):
        self.attribute_statistics.clear()
        self.image_path = None
        self.image_display_label.configure(text="No image selected.")
        self.update_stats_display()
        self.status_bar.configure(text="统计数据已清空.")
        print("Statistics cleared.")

    def save_statistics(self):
        try:
            data_dir = os.path.dirname(STATS_FILE_PATH)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            with open(STATS_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.attribute_statistics, f, ensure_ascii=False, indent=4)
            self.status_bar.configure(text=f"统计数据已保存到 {STATS_FILE_PATH}.")
        except Exception as e:
            self.status_bar.configure(text=f"保存失败: {e}.")
            messagebox.showerror("Save Error", f"Could not save statistics: {e}")


    def load_statistics(self):
        if os.path.exists(STATS_FILE_PATH):
            try:
                with open(STATS_FILE_PATH, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)
                    self.attribute_statistics = defaultdict(int, loaded_stats)
                # Status updated by caller or at end of __init__
            except Exception as e:
                self.attribute_statistics = defaultdict(int)
                # Status updated by caller
                print(f"Error loading statistics: {e}. Starting with empty stats.")
        else:
            self.attribute_statistics = defaultdict(int)
            print("No statistics file found. Starting with empty stats.")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
