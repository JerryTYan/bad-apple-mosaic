import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageEnhance
import os
import sys
import video_generator
import time
import config
import threading

class BadAppleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bad Appleify")
        self.config(padx=50, pady=50)
        self.iconbitmap(config.ICON_FILE)
        self.eval('tk::PlaceWindow . center')

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize attributes
        self.selected_img_path = None
        self.selected_img_extension = None

        # Keep a reference to the processing thread
        self.processing_thread = None

        # Setup the user interface
        self.setup_ui()

        # Set the protocol handler for window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def setup_ui(self):
        # Configure grid layout
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        self.grid_rowconfigure((0, 2, 3, 4), weight=1, uniform="row")
        self.grid_rowconfigure(1, weight=3)

        # Title Label
        titleLbl = ctk.CTkLabel(
            master=self, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center"
        )
        titleLbl.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        # Display Image
        image_path = config.IMAGE_FILE
        img = Image.open(image_path)
        ctkImg = ctk.CTkImage(light_image=img, size=(200, 200))
        self.imgLbl = ctk.CTkLabel(master=self, image=ctkImg, anchor="center", text="")
        self.imgLbl.grid(row=1, column=0, columnspan=3, pady=10)
        self.imgLbl.image = ctkImg

        # Select Image Button
        selectImageBtn = ctk.CTkButton(
            master=self, text="Select Image", border_width=1, border_color="#dfe6e9",
            fg_color="#6c5ce7", hover_color="#5f27cd", command=self.select_file_handler
        )
        selectImageBtn.grid(row=2, column=0, pady=10, sticky="ew")

        # File Name Label
        self.fileNameLbl = ctk.CTkLabel(
            master=self, text="No file selected", fg_color="#636e72", anchor="w", corner_radius=5
        )
        self.fileNameLbl.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

        # Image Requirements Label
        imgReqLbl = ctk.CTkLabel(
            master=self, text="*Your file must be an image file.", anchor="center"
        )
        imgReqLbl.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        # Upload Button
        uploadBtn = ctk.CTkButton(
            master=self, text="Upload", border_width=1, border_color="#dfe6e9",
            fg_color="#6c5ce7", hover_color="#5f27cd", command=self.upload_file_handler
        )
        uploadBtn.grid(row=4, column=0, columnspan=3, pady=10)

    def select_file_handler(self):
        """
        Opens a file dialog to select an image, displays the selected image in the GUI,
        and saves the file path for further processing.
        """
        file_path = filedialog.askopenfilename(
            initialdir="/", title="Select An Image",
            filetypes=[
                ('All files', "*.png *.jpg *.jpeg *.png *.webp *.bmp *.gif *.tiff *.tif *.ppm *.pgm *.pbm *.ico *.dds *.pcx *.psd *.tga"),
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg *.jpeg'),
                ('WEBP files', '*.webp'),
                ('BMP files', '*.bmp'),
                ('GIF files', '*.gif'),
                ('TIFF files', '*.tiff *.tif'),
                ('PPM files', '*.ppm *.pgm *.pbm'),
                ('ICO files', '*.ico'),
                ('DDS files', '*.dds'),
                ('PCX files', '*.pcx'),
                ('PSD files', '*.psd'),
                ('TGA files', '*.tga'),
            ]
        )

        if file_path:
            max_length = 40
            displayed_file_path = ('...' + file_path[-(max_length - 3):]) if len(file_path) > max_length else file_path
            self.fileNameLbl.configure(text=displayed_file_path)

            img = Image.open(file_path).convert('RGB')
            img.thumbnail((200, 200))

            ctkImg = ctk.CTkImage(light_image=img, size=(200, 200))
            self.imgLbl.configure(image=ctkImg)
            self.imgLbl.image = ctkImg

            self.selected_img_path, self.selected_img_extension = os.path.splitext(file_path)

    def upload_file_handler(self):
        """
        Uploads the selected file, saves it in multiple formats, and triggers video generation.
        """
        if not self.selected_img_path:
            messagebox.showerror("Error", "No valid file was selected.")
            return

        save_dir = config.UPLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)

        self.show_progress_bar()

        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_images_and_generate_video, daemon=True)
        self.processing_thread.start()

    def process_images_and_generate_video(self):
        try:
            save_file_name = "upload.png"
            save_path = os.path.join(config.UPLOAD_DIR, save_file_name)

            img = Image.open(self.selected_img_path + self.selected_img_extension).convert('RGB')
            img.save(save_path, "PNG")

            resized_img = img.resize((40, 40))
            resized_img.save(os.path.join(config.UPLOAD_DIR, "40x40_upload.png"), "PNG")

            gray_img = ImageOps.grayscale(resized_img)
            enhanced_img = ImageEnhance.Contrast(gray_img).enhance(2.0)
            enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(0.1)
            enhanced_img.save(os.path.join(config.UPLOAD_DIR, "gray_40x40_upload.png"), "PNG")

            # Call video_generator functions with adjusted paths
            start_time = time.time()
            print("Generating frames...")
            video_generator.generate_frames()
            print("Generating video...")
            video_generator.generate_video(
                frames_dir=config.PROCESSED_FRAMES_DIR,
                fps=config.FRAME_RATE,
                output_video_path=config.OUTPUT_VIDEO,
                audio_path=config.AUDIO_FILE
            )
            print(f"Process complete in {time.time() - start_time:.2f} seconds.")

            # After processing is done, update the GUI
            self.processing_complete()

        except Exception as e:
            self.show_error_message(f"An unexpected error occurred: {e}")

    def show_progress_bar(self):
        self.clear_window()
        
        self.progress_label = ctk.CTkLabel(
            master=self, text="Generating video...", font=("Segoe UI", 16), anchor="center"
        )
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate", height=20, progress_color="#32CD32")
        self.cancelBtn = ctk.CTkButton(
            master=self, text="Cancel", border_width=1, border_color="#dfe6e9",
            fg_color="#6c5ce7", hover_color="#5f27cd", command=self.on_closing
        )
        self.progress_label.pack(pady=20)
        self.progress_bar.pack(pady=20)
        self.progress_bar.start()
        self.cancelBtn.pack(pady=20)

    def processing_complete(self):
        self.after(0, self._processing_complete)

    def _processing_complete(self):
        messagebox.showinfo("Info", "Processing complete.")
        self.clear_window()
        self.setup_ui()

    def show_error_message(self, message):
        self.after(0, lambda: messagebox.showerror("Error", message))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to cancel?"):
            try:
                # Terminate the executor if it's running
                if video_generator.executor_reference is not None:
                    video_generator.executor_reference.shutdown(wait=False, cancel_futures=True)
            except Exception as e:
                print(f"Error during shutdown: {e}")
            finally:
                self.destroy()
                sys.exit(0)

if __name__ == "__main__":
    app = BadAppleApp()
    app.mainloop()
