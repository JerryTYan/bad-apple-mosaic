import customtkinter as ctk
from tkinter import filedialog, PhotoImage
from PIL import Image
import os
import subprocess

def selectFileHandler():
    # Open file dialog to select an image
    file_path = filedialog.askopenfilename(initialdir="/", title="Select An Image", filetypes=[('png files','*.png'),('jpg files','*.jpg'),('jpeg files','*.jpeg')])
    
    if file_path:
        # Display selected file path in the label
        fileNameLbl.configure(text=file_path)
        
        # Open and create a thumbnail for display in the GUI
        img = Image.open(file_path)
        img.thumbnail((200,200))
        
        # Convert to customtkinter image format and display it
        ctkImg = ctk.CTkImage(light_image=img, size=(200,200))
        imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
        imgLbl.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Save the image path and extension globally for the upload function
        global selected_img_path, selected_img_extension
        selected_img_path, selected_img_extension = os.path.splitext(file_path)
    
def uploadFileHandler():
    # Create the upload directory if it doesn't exist
    save_dir = "assets/uploads"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        # Define the save path for the uploaded file
        save_file_name = f"upload{selected_img_extension}"
        save_path = os.path.join(save_dir, save_file_name)
        
        # Save the image in the specified directory
        img = Image.open(selected_img_path + selected_img_extension)
        img.save(save_path)
        resized_img = img.resize((40, 40))
        resized_img.save(os.path.join(save_dir, "40x40_" + save_file_name))
        
    except NameError:
        # Error handling in case no file was selected
        print("No valid file was selected")
    except Exception as e:
        # General error handling for any issue during file saving
        print(f"Error saving the image: {e}")
    
    # Execute video_generator.py script
    try:
        subprocess.run(["python", "video_generator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running video_generator.py: {e}")

# Setup the customtkinter app window
app = ctk.CTk()
app.title("Bad Appleify")
app.config(padx=50, pady=50)  # Add padding around the window
app.iconbitmap("assets/badApple.ico")  # Set window icon

# Configure appearance mode and color theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# Configure grid layout with flexible columns and rows for extendable UI
app.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
app.grid_rowconfigure((0, 2, 3, 4), weight=1, uniform="row")
app.grid_rowconfigure(1, weight=3)

# Add the title label to the window
titleLbl = ctk.CTkLabel(master=app, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center")
titleLbl.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

# Display default image before user selects a new one
ctkImg = ctk.CTkImage(light_image=Image.open("assets/badApple.png"), size=(200,200))
imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
imgLbl.grid(row=1, column=0, columnspan=3, pady=10)

# Add a button to select an image
selectImageBtn = ctk.CTkButton(master=app, text="Select Image", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=selectFileHandler)
selectImageBtn.grid(row=2, column=0, pady=10, sticky="ew")

# Label to display the selected file path
fileNameLbl = ctk.CTkLabel(master=app, text="No file selected", fg_color="#636e72", anchor="w", corner_radius=5)
fileNameLbl.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

# Instruction label for the image requirements
imgReqLbl = ctk.CTkLabel(master=app, text="*Your file must be a .png, .jpg, or .jpeg.", anchor="center")
imgReqLbl.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

# Add an upload button to save the selected image
uploadBtn = ctk.CTkButton(master=app, text="Upload", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=uploadFileHandler)
uploadBtn.grid(row=4, column=0, columnspan=3, pady=10)

# Run the application
app.mainloop()
