import customtkinter as ctk

app = ctk.CTk()
app.title("Bad Appleify")
app.geometry("400x200")

app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure((0,1), weight=1)

chooseImageBtn = ctk.CTkButton(master=app, text="Choose Image")
chooseImageBtn.grid(row=0, column=0, padx=20, pady=20)

uploadBtn = ctk.CTkButton(master=app, text="Upload")
uploadBtn.grid(row=1, column=0, padx=20, pady=20)

app.mainloop()