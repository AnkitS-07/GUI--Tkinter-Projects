from tkinter import *
import math

def buttonpress(num):
    global equation_text
    equation_text = equation_text + str(num)
    equation_label.set(equation_text)

def equals():
    try:
        global equation_text
        total = str(eval(equation_text))
        equation_label.set(total)
        equation_text = total 
    except:
        equation_label.set("Error")
        equation_text = ""

def clear():
    global equation_text
    equation_label.set("")
    equation_text = ""

def delete():
    global equation_text
    equation_text = equation_text[:-1]
    equation_label.set(equation_text)

def square():
    global equation_text
    try:
        equation_text = str(eval(equation_text + "**2"))
        equation_label.set(equation_text)
    except:
        equation_label.set("Error")
        equation_text = ""

def sqrt():
    global equation_text
    try:
        equation_text = str(math.sqrt(float(equation_text)))
        equation_label.set(equation_text)
    except:
        equation_label.set("Error")
        equation_text = ""

def percent():
    global equation_text
    try:
        equation_text = str(eval(equation_text + "/100"))
        equation_label.set(equation_text)
    except:
        equation_label.set("Error")
        equation_text = ""

def keypress(event):
    if event.char.isdigit() or event.char in "+-*/.":
        buttonpress(event.char)
    elif event.keysym == "Return":
        equals()
    elif event.keysym == "BackSpace":
        delete()

window = Tk()
window.title("Calculator")
window.geometry("500x700")
window.config(bg="#282c34")

equation_text = ""
equation_label = StringVar()

label = Label(window, textvariable=equation_label, font=("Arial",20),
              bg="white", fg="black", width=24, height=2)
label.pack(pady=10)

frame = Frame(window, bg="#282c34")
frame.pack()

buttons = [
    ('7',2,0), ('8',2,1), ('9',2,2),
    ('4',1,0), ('5',1,1), ('6',1,2),
    ('1',0,0), ('2',0,1), ('3',0,2),
    ('0',3,1), ('.',3,0)
]

for (text, r, c) in buttons:
    Button(frame, text=text, height=4, width=9, font=35, bg="#61afef",
           command=lambda t=text: buttonpress(t)).grid(row=r, column=c, padx=2, pady=2)

ops = [
    ('+',0,3), ('-',1,3), ('x',2,3), ('/',3,3)
]

for (text, r, c) in ops:
    val = "*" if text == "x" else text
    Button(frame, text=text, height=4, width=9, font=35, bg="#98c379",
           command=lambda v=val: buttonpress(v)).grid(row=r, column=c, padx=2, pady=2)

Button(frame, text="=", height=4, width=9, font=35, bg="#e5c07b",
       command=equals).grid(row=3, column=2, padx=2, pady=2)

Button(frame, text="x²", height=4, width=9, font=35, bg="#c678dd",
       command=square).grid(row=4, column=0, padx=2, pady=2)

Button(frame, text="√", height=4, width=9, font=35, bg="#c678dd",
       command=sqrt).grid(row=4, column=1, padx=2, pady=2)

Button(frame, text="%", height=4, width=9, font=35, bg="#c678dd",
       command=percent).grid(row=4, column=2, padx=2, pady=2)

Button(frame, text="⌫", height=4, width=9, font=35, bg="#e06c75",
       command=delete).grid(row=4, column=3, padx=2, pady=2)

cl = Button(window, text="Clear", height=2, width=20, font=20, bg="#d19a66",
            command=clear)
cl.pack(pady=5)

window.bind("<Key>", keypress)

window.mainloop()