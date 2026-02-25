import customtkinter as ctk

app = ctk.CTk()
scroll = ctk.CTkScrollableFrame(app)
scroll.pack()

btn = ctk.CTkButton(scroll, text="Folder")
btn.pack()

def on_root(e): print("ROOT")
def on_btn(e): print("BTN")

scroll._parent_canvas.bind("<Button-1>", on_root)
btn.bind("<Button-1>", on_btn)

# Can't easily simulate so I'll just check bindings
print("Ready")
app.after(1000, lambda: btn._canvas.event_generate("<Button-1>"))
app.after(2000, app.destroy)
app.mainloop()
