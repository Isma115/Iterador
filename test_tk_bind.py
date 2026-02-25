import tkinter as tk

root = tk.Tk()
canvas = tk.Canvas(root, width=200, height=200)
canvas.pack()

btn = tk.Button(canvas, text="Click Me")
btn.place(x=50, y=50)

def on_canvas(e):
    print("Canvas clicked")

def on_btn(e):
    print("Btn clicked")
    # return "break"

canvas.bind("<Button-1>", on_canvas)
btn.bind("<Button-1>", on_btn)

# We can simulate a click on the button
btn.event_generate("<Button-1>")

root.update()
