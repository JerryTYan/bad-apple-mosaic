import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps, ImageEnhance
import shutil
import os
import sys
import video_generator
import time
import config
import threading
import multiprocessing
import re

class BadAppleApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bad Appleify")
        self.iconbitmap(config.ICON_FILE)
        self.config(padx=50, pady=50)
        self.eval("tk::PlaceWindow . center")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Set a fixed window size
        self.geometry("600x600")
        self.resizable(False, False)

        # Initialize attributes
        self.selected_img_path = None
        self.selected_img_extension = None

        # User-selected options
        self.input_resolution = config.DEFAULT_INPUT_RESOLUTION
        self.output_framerate = config.DEFAULT_FRAMERATE
        self.output_resolution = config.DEFAULT_OUTPUT_RESOLUTION

        # Keep a reference to the processing thread
        self.processing_thread = None

        # Initialize frames dictionary
        self.frames = {}
        self.current_frame = None

        # Show initial frame
        self.show_frame(InitialFrame)

        # Set the protocol handler for window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def show_frame(self, frame_class):
        """Bring the specified frame to the front and handle frame transitions."""
        # Create the frame if it doesn't exist
        if frame_class not in self.frames:
            frame = frame_class(parent=self, controller=self)
            self.frames[frame_class] = frame
        else:
            frame = self.frames[frame_class]

        # Hide the current frame if it exists
        if self.current_frame and self.current_frame != frame:
            if hasattr(self.current_frame, 'on_hide_frame'):
                self.current_frame.on_hide_frame()
            self.current_frame.place_forget()

        # Place the new frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Call on_show_frame if it exists
        if hasattr(frame, 'on_show_frame'):
            frame.on_show_frame()

        # Update the current frame reference
        self.current_frame = frame

    def select_file_handler(self):
        """
        Handle the file selection and update the UI accordingly.
        """
        file_path = filedialog.askopenfilename(
            initialdir="/", title="Select An Image",
            filetypes=[
                ("All files", "*.png *.jpg *.jpeg *.png *.webp *.bmp *.gif *.tiff *.tif *.ppm *.pgm *.pbm *.ico *.dds *.pcx *.psd *.tga"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("WEBP files", "*.webp"),
                ("BMP files", "*.bmp"),
                ("GIF files", "*.gif"),
                ("TIFF files", "*.tiff *.tif"),
                ("PPM files", "*.ppm *.pgm *.pbm"),
                ("ICO files", "*.ico"),
                ("DDS files", "*.dds"),
                ("PCX files", "*.pcx"),
                ("PSD files", "*.psd"),
                ("TGA files", "*.tga"),
            ]
        )

        if file_path:
            max_length = 40
            displayed_file_path = ("..." + file_path[-(max_length - 3):]) if len(file_path) > max_length else file_path
            initial_frame = self.frames[InitialFrame]
            initial_frame.fileNameLbl.configure(text=displayed_file_path)

            img = Image.open(file_path).convert("RGB")
            img.thumbnail((200, 200))

            ctkImg = ctk.CTkImage(light_image=img, size=(200, 200))
            initial_frame.imgLbl.configure(image=ctkImg)
            initial_frame.imgLbl.image = ctkImg

            self.selected_img_path, self.selected_img_extension = os.path.splitext(file_path)

    def upload_file_handler(self):
        """
        Start the processing thread and show the progress frame.
        """
        if not self.selected_img_path:
            messagebox.showerror("Error", "No valid file was selected.")
            return

        save_dir = config.UPLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)

        # Show progress frame
        self.show_frame(ProgressFrame)

        # Start processing in a separate daemon thread
        self.processing_thread = threading.Thread(target=self.process_images_and_generate_video, daemon=True)
        self.processing_thread.start()

    def process_images_and_generate_video(self):
        try:
            save_file_name = "upload.png"
            save_path = os.path.join(config.UPLOAD_DIR, save_file_name)

            img = Image.open(self.selected_img_path + self.selected_img_extension).convert("RGB")
            img.save(save_path, "PNG")

            resized_img = img.resize((40, 40))
            resized_img.save(os.path.join(config.UPLOAD_DIR, "40x40_upload.png"), "PNG")

            gray_img = ImageOps.grayscale(resized_img)
            enhanced_img = ImageEnhance.Contrast(gray_img).enhance(2.0)
            enhanced_img = ImageEnhance.Brightness(enhanced_img).enhance(0.1)
            enhanced_img.save(os.path.join(config.UPLOAD_DIR, "gray_40x40_upload.png"), "PNG")

            # Construct pixel data file path based on user selections
            pixel_data_filename = f"pixel_data@{self.input_resolution}{self.output_framerate}.pkl"
            pixel_data_path = os.path.join(config.PIXEL_DATA_DIR, pixel_data_filename)
            if not os.path.exists(pixel_data_path):
                raise FileNotFoundError(f"Pixel data file '{pixel_data_filename}' not found.")

            # Call video_generator functions
            start_time = time.time()
            video_generator.generate_frames(
                pixel_data_path=pixel_data_path,
                output_resolution=config.OUTPUT_RESOLUTION_DIMENSIONS[self.output_resolution]
            )
            video_generator.generate_video(
                frames_dir=config.PROCESSED_FRAMES_DIR,
                fps=config.FRAME_RATE_OPTIONS[self.output_framerate],
                output_video_path=os.path.join(config.OUTPUT_VIDEO_DIR, "good_apple.mp4"),
                audio_path=config.AUDIO_FILE
            )

            # After processing is done, update the GUI
            self.processing_complete()

        except Exception as e:
            self.show_error_message(f"An unexpected error occurred: {e}")

    def processing_complete(self):
        self.after(0, self._processing_complete)

    def _processing_complete(self):
        # Stop the progress bar
        progress_frame = self.frames[ProgressFrame]
        progress_frame.progress_bar.stop()
        # Show the save frame
        self.show_frame(SaveFrame)

    def save_as_handler(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Video As",
            initialfile="good_apple.mp4"
        )

        if save_path:
            try:
                shutil.copyfile(os.path.join(config.OUTPUT_VIDEO_DIR, "good_apple.mp4"), save_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the video: {e}")
            finally:
                # Return to the initial frame
                self.show_frame(InitialFrame)
        else:
            # User canceled the save dialog
            pass

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

class InitialFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Configure grid layout
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        self.grid_rowconfigure((0, 2, 3, 4, 5, 6, 7), weight=1, uniform="row")
        self.grid_rowconfigure(1, weight=3)

        # Title Label
        titleLbl = ctk.CTkLabel(
            master=self, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center"
        )
        titleLbl.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Display Image
        image_path = config.IMAGE_FILE
        img = Image.open(image_path)
        ctkImg = ctk.CTkImage(light_image=img, size=(200, 200))
        self.imgLbl = ctk.CTkLabel(master=self, image=ctkImg, anchor="center", text="")
        self.imgLbl.grid(row=1, column=0, columnspan=3, pady=5)
        self.imgLbl.image = ctkImg

        # Select Image Button
        selectImageBtn = ctk.CTkButton(
            master=self, text="Select Image", border_width=1, command=self.controller.select_file_handler
        )
        selectImageBtn.grid(row=2, column=0, pady=5, sticky="ew")

        # File Name Label
        self.fileNameLbl = ctk.CTkLabel(
            master=self, text="No file selected", fg_color="#37474F", anchor="w", corner_radius=5
        )
        self.fileNameLbl.grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")

        # Input Resolution Option Menu
        input_resolution_label = ctk.CTkLabel(master=self, text="Input Resolution:", anchor="w")
        input_resolution_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.input_resolution_var = ctk.StringVar(value=self.controller.input_resolution)
        input_resolution_options = ["72p"]
        input_resolution_menu = ctk.CTkOptionMenu(
            master=self,
            values=input_resolution_options,
            variable=self.input_resolution_var,
            command=self.update_input_resolution
        )
        input_resolution_menu.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Output Frame Rate Option Menu
        output_framerate_label = ctk.CTkLabel(master=self, text="Output Frame Rate:", anchor="w")
        output_framerate_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.output_framerate_var = ctk.StringVar(value=self.controller.output_framerate)
        output_framerate_options = ["30fps", "60fps"]
        output_framerate_menu = ctk.CTkOptionMenu(
            master=self,
            values=output_framerate_options,
            variable=self.output_framerate_var,
            command=self.update_output_framerate
        )
        output_framerate_menu.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Output Resolution Option Menu
        output_resolution_label = ctk.CTkLabel(master=self, text="Output Resolution:", anchor="w")
        output_resolution_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.output_resolution_var = ctk.StringVar(value=self.controller.output_resolution)
        output_resolution_options = ["4K"]
        output_resolution_menu = ctk.CTkOptionMenu(
            master=self,
            values=output_resolution_options,
            variable=self.output_resolution_var,
            command=self.update_output_resolution
        )
        output_resolution_menu.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Image Requirements Label
        imgReqLbl = ctk.CTkLabel(
            master=self, text="*Your file must be an image file.", anchor="center"
        )
        imgReqLbl.grid(row=6, column=0, columnspan=3, pady=5, sticky="ew")

        # Upload Button
        uploadBtn = ctk.CTkButton(
            master=self, text="Upload", border_width=1, command=self.controller.upload_file_handler
        )
        uploadBtn.grid(row=7, column=0, columnspan=3, pady=10)

    def update_input_resolution(self, value):
        self.controller.input_resolution = value

    def update_output_framerate(self, value):
        self.controller.output_framerate = value

    def update_output_resolution(self, value):
        self.controller.output_resolution = value

class ProgressFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Progress Label
        self.progress_label = ctk.CTkLabel(
            master=self, text="Generating video...", font=("Segoe UI", 20, "bold"), anchor="center"
        )
        self.progress_label.grid(row=0, column=0, padx=20, pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate", height=20)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Warning Label
        warning_text = (
            "⚠️ *Warning: This process may take several minutes and is CPU-intensive.\n"
            "Please ensure your computer is plugged in and avoid running other heavy applications."
        )
        warningLbl = ctk.CTkLabel(master=self, text=warning_text, anchor="center")
        warningLbl.grid(row=2, column=0, pady=10, sticky="ew")

        # Cancel Button
        self.cancelBtn = ctk.CTkButton(
            master=self, text="Cancel", border_width=1, command=self.controller.on_closing
        )
        self.cancelBtn.grid(row=3, column=0, padx=20, pady=10)

    def on_show_frame(self):
        """Method called when the frame is shown."""
        self.progress_bar.start()

    def on_hide_frame(self):
        """Method called when the frame is hidden."""
        self.progress_bar.stop()

class SaveFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Save As Labels
        save_as_label_main = ctk.CTkLabel(
            master=self, text="Video Generation Complete", font=("Segoe UI", 20, "bold"), anchor="center"
        )
        save_as_label_main.grid(row=0, column=0, padx=10, pady=(10, 0))

        save_as_label_sec = ctk.CTkLabel(
            master=self, text="Save Your Video!", font=("Segoe UI", 16), anchor="center"
        )
        save_as_label_sec.grid(row=1, column=0, padx=10, pady=(0, 10))

        # Display Video Preview Image
        try:
            image_path = config.VIDEO_PREVIEW_FILE
            img = Image.open(image_path)
            ctkImg = ctk.CTkImage(light_image=img, size=(360, 240))
            self.previewImgLbl = ctk.CTkLabel(master=self, image=ctkImg, anchor="center", text="")
            self.previewImgLbl.grid(row=2, column=0, padx=10, pady=10)
            self.previewImgLbl.image = ctkImg 
        except Exception as e:
            pass

        # Save As Button
        save_as_button = ctk.CTkButton(
            master=self, text="Save As", border_width=1, command=self.controller.save_as_handler
        )
        save_as_button.grid(row=3, column=0, padx=10, pady=10)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = BadAppleApp()
    app.mainloop()
