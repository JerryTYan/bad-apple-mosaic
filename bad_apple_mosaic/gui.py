# gui.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageEnhance
import os
import video_generator
import time
import config  # Import the config module

class BadAppleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bad Appleify")
        self.config(padx=50, pady=50)
        self.iconbitmap(config.ICON_FILE)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize attributes
        self.selected_img_path = None
        self.selected_img_extension = None

        # Setup the user interface
        self.setup_ui()

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

        # Select Image Button
        selectImageBtn = ctk.CTkButton(
            master=self, text="Select Image", border_width=1, border_color="#dfe6e9",
            fg_color="#6c5ce7", hover_color="#5f27cd", command=self.selectFileHandler
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
            fg_color="#6c5ce7", hover_color="#5f27cd", command=self.uploadFileHandler
        )
        uploadBtn.grid(row=4, column=0, columnspan=3, pady=10)

    def selectFileHandler(self):
        """
        Opens a file dialog to select an image, displays the selected image in the GUI,
        and saves the file path for further processing.
        """
        file_path = filedialog.askopenfilename(
            initialdir="/", title="Select An Image",
            filetypes=[
                ('All image files', "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff *.tif *.ppm *.pgm *.pbm *.ico *.dds *.pcx *.psd *.tga"),
                ('PNG files', '*.png'),
                ('JPEG files', '*.jpg *.jpeg'),
                # ... other file types ...
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
            self.imgLbl.image = ctkImg  # Keep a reference to prevent garbage collection

            self.selected_img_path, self.selected_img_extension = os.path.splitext(file_path)

    def uploadFileHandler(self):
        """
        Uploads the selected file, saves it in multiple formats, and triggers video generation.
        """
        if not self.selected_img_path:
            messagebox.showerror("Error", "No valid file was selected.")
            return

        save_dir = config.UPLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)

        try:
            save_file_name = "upload.png"
            save_path = os.path.join(save_dir, save_file_name)

            img = Image.open(self.selected_img_path + self.selected_img_extension).convert('RGB')
            img.save(save_path, "PNG")

            resized_img = img.resize((40, 40))
            resized_img.save(os.path.join(save_dir, "40x40_upload.png"), "PNG")

            gray_img = ImageOps.grayscale(resized_img)
            enhanced_img = ImageEnhance.Contrast(gray_img).enhance(2.0)
            enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(0.1)
            enhanced_img.save(os.path.join(save_dir, "gray_40x40_upload.png"), "PNG")

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

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    app = BadAppleApp()
    app.mainloop()
