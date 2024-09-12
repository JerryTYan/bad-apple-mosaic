import customtkinter as ctk
from tkinter import filedialog, PhotoImage
from PIL import Image
import os

def selectFileHandler():
    file_path = filedialog.askopenfilename(initialdir="/", title="Select An Image", filetypes=[('png files','*.png'),('jpg files','*.jpg'),('jpeg files','*.jpeg')])
    if file_path:
        fileNameLbl.configure(text=file_path)
        
        img = Image.open(file_path)
        img.thumbnail((200,200))
        
        ctkImg = ctk.CTkImage(light_image=img, size=(200,200))
        imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
        imgLbl.grid(row=1, column=0, columnspan=3, pady=10)
        
        global selected_img_path, selected_img_extension
        selected_img_path, selected_img_extension = os.path.splitext(file_path)
    
def uploadFileHandler():
    save_dir = "assets/uploads"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        save_file_name = f"upload{selected_img_extension}"
        save_path = os.path.join(save_dir, save_file_name)
        img = Image.open(selected_img_path + selected_img_extension)
        img.save(save_path)
    except NameError:
        print("No valid file was selected")
    except Exception as e:
        print(f"Error saving the image: {e}")

# customtkinter window for image upload
app = ctk.CTk()
app.title("Bad Appleify")
app.config(padx=50,pady=50)
app.iconbitmap("assets/badApple.ico")

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app.grid_columnconfigure((0,1,2), weight=1, uniform="col")
app.grid_rowconfigure((0,2,3,4), weight=1, uniform="row")
app.grid_rowconfigure(1, weight=3)

titleLbl = ctk.CTkLabel(master=app, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center")
titleLbl.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

ctkImg = ctk.CTkImage(light_image=Image.open("assets/badApple.png"), size=(200,200))
imgLbl = ctk.CTkLabel(master=app, image=ctkImg, anchor="center", text="")
imgLbl.grid(row=1, column=0, columnspan=3, pady=10)       

selectImageBtn = ctk.CTkButton(master=app, text="Select Image", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=selectFileHandler)
selectImageBtn.grid(row=2, column=0, pady=10, sticky="ew")
fileNameLbl = ctk.CTkLabel(master=app, text="No file selected", fg_color="#636e72", anchor="w", corner_radius=5)
fileNameLbl.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

imgReqLbl = ctk.CTkLabel(master=app, text="*Your file must be a .png, .jpg, or .jpeg.", anchor="center")
imgReqLbl.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

uploadBtn = ctk.CTkButton(master=app, text="Upload", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command=uploadFileHandler)
uploadBtn.grid(row=4, column=0, columnspan=3, pady=10)

app.mainloop()
