import customtkinter as ctk
from tkinter import filedialog, PhotoImage, messagebox
from PIL import Image, ImageOps, ImageEnhance
import os
import video_generator
import time

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Select file handler
def selectFileHandler():
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
        displayed_file_path = ('...' + file_path[-(max_length-3):]) if len(file_path) > max_length else file_path
        fileNameLbl.configure(text=displayed_file_path)

        img = Image.open(file_path).convert('RGB')
        img.thumbnail((200,200))
        
        ctkImg = ctk.CTkImage(light_image=img, size=(200,200))
        imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
        imgLbl.grid(row=1, column=0, columnspan=3, pady=10)
        
        app.selected_img_path, app.selected_img_extension = os.path.splitext(file_path)

# Upload file handler
def uploadFileHandler():
    """
    Uploads the selected file, saves it in multiple formats, and triggers video generation.
    """
    if not hasattr(app, 'selected_img_path'):
        messagebox.showerror("Error", "No valid file was selected.")
        return
    
    # Define the paths relative to the script directory
    save_dir = os.path.join(script_dir, '..', 'assets', 'uploads')
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        save_file_name = "upload.png"
        save_path = os.path.join(save_dir, save_file_name)

        img = Image.open(app.selected_img_path + app.selected_img_extension).convert('RGB')
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
        frames_dir = os.path.join(script_dir, '..', 'assets', 'processed_frames')
        output_video_path = os.path.join(script_dir, '..', 'good_apple.mp4')
        audio_path = os.path.join(script_dir, '..', 'assets', 'bad_apple_enhanced.mp3')
        video_generator.generate_video(
            frames_dir, 
            30, 
            output_video_path, 
            audio_path
        )
        print(f"Process complete in {time.time() - start_time:.2f} seconds.")

    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Setup the app window
    app = ctk.CTk()
    app.title("Bad Appleify")
    app.config(padx=50, pady=50)
    icon_path = os.path.join(script_dir, '..', 'assets', 'badApple.ico')
    app.iconbitmap(icon_path)

    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
    app.grid_rowconfigure((0, 2, 3, 4), weight=1, uniform="row")
    app.grid_rowconfigure(1, weight=3)

    titleLbl = ctk.CTkLabel(master=app, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center")
    titleLbl.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

    image_path = os.path.join(script_dir, '..', 'assets', 'badApple.png')
    ctkImg = ctk.CTkImage(light_image=Image.open(image_path), size=(200,200))
    imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
    imgLbl.grid(row=1, column=0, columnspan=3, pady=10)

    selectImageBtn = ctk.CTkButton(master=app, text="Select Image", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=selectFileHandler)
    selectImageBtn.grid(row=2, column=0, pady=10, sticky="ew")

    fileNameLbl = ctk.CTkLabel(master=app, text="No file selected", fg_color="#636e72", anchor="w", corner_radius=5)
    fileNameLbl.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

    imgReqLbl = ctk.CTkLabel(master=app, text="*Your file must be an image file.", anchor="center")
    imgReqLbl.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

    uploadBtn = ctk.CTkButton(master=app, text="Upload", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=uploadFileHandler)
    uploadBtn.grid(row=4, column=0, columnspan=3, pady=10)
    app.mainloop()
