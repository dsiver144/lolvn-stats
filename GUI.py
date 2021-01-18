from tkinter import *
from tkinter import filedialog

 
window = Tk()
 
window.title("Welcome to LikeGeeks app")
window.geometry('1280x720')
 
lbl = Label(window, text="Hello")
 
lbl.grid(column=0, row=0)
file = filedialog.askopenfilename()
print(file)

 
window.mainloop()