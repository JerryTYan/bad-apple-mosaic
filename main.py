import customtkinter as ctk

app = ctk.CTk()
app.title("Bad Appleify")
app.config(padx=50,pady=50)

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app.grid_columnconfigure((0,1,2), weight=1, uniform="col")
app.grid_rowconfigure((0,1,2,3), weight=1, uniform="row")

titleLbl = ctk.CTkLabel(master=app, text="Bad Appleify Any Image!", font=("Segoe UI", 20, "bold"), anchor="center")
titleLbl.grid(row=0, column=1, pady=20, sticky="ew")

selectImageBtn = ctk.CTkButton(master=app, text="Select Image", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command="selectFileHandler")
selectImageBtn.grid(row=1, column=0, pady=20, sticky="ew")
fileNameLbl = ctk.CTkLabel(master=app, text="No file selected", fg_color="#636e72", anchor="w", corner_radius=5)
fileNameLbl.grid(row=1, column=1, columnspan=2, pady=20, sticky="ew")

uploadBtn = ctk.CTkButton(master=app, text="Upload", border_width=1, border_color="#dfe6e9", fg_color="#6c5ce7", hover_color="#5f27cd", command="uploadFileHandler")
uploadBtn.grid(row=3, column=1, pady=20, sticky="ew")

app.mainloop()
