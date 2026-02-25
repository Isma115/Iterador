import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os
import shutil
import trafilatura
import threading
import json
from search_engine import TrustedSearcher

# Set basic theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DOCS_DIR = "Documentos"
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

CONDENSED_SEPARATOR = "═══════════ CONDENSADO ═══════════"

class DocumentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Documentos")
        
        # Maximize window (Mac compatible)
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+0+0")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        
        # Header Area
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.header_label = ctk.CTkLabel(self.header_frame, text="Gestor de Documentos", 
                                     font=("Helvetica", 24, "bold"), text_color="#00ADB5")
        self.header_label.pack(pady=5)
        
        # Action Bar Area
        self.action_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.action_frame.pack(fill='x', pady=10, padx=50)
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.action_frame, textvariable=self.search_var, 
                                     font=("Helvetica", 16), placeholder_text="Buscar en documentos (texto o título)...",
                                     height=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", self.start_search)
        
        self.search_button = ctk.CTkButton(self.action_frame, text="BUSCAR", command=self.start_search,
                                       font=("Helvetica", 12, "bold"), fg_color="#00ADB5", hover_color="#007d82",
                                       height=40)
        self.search_button.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(self.root, text="Listo.", font=("Helvetica", 12), text_color="gray")
        self.status_label.grid(row=1, column=0, pady=(0, 5))

        # Main Content Area
        self.content_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_container.grid_columnconfigure(2, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Left Pane container (Split into Tree and Search Results)
        self.left_pane_visible = True
        self.left_pane = ctk.CTkFrame(self.content_container, width=300, corner_radius=10, fg_color="transparent")
        self.left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 0))
        
        # Toggle button for left pane
        self.toggle_btn = ctk.CTkButton(self.content_container, text="◀", width=16, height=50,
                                        fg_color="#2C2C2C", hover_color="#3C3C3C",
                                        text_color="#888888", font=("Arial", 14),
                                        corner_radius=4, command=self.toggle_left_pane)
        self.toggle_btn.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=100)
        self.left_pane.grid_propagate(False)
        self.left_pane.grid_rowconfigure(0, weight=1) # Explorer gets more space initially or equal
        self.left_pane.grid_rowconfigure(1, weight=1) # Search gets equal space
        
        # Explorer Section
        self.list_frame = ctk.CTkFrame(self.left_pane, corner_radius=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.list_header_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        self.list_header_frame.pack(fill="x", pady=5)
        
        self.list_header = ctk.CTkLabel(self.list_header_frame, text="Explorador", font=("Arial", 14, "bold"))
        self.list_header.pack(side="left", padx=(10, 0))
        
        self.header_btns_frame = ctk.CTkFrame(self.list_header_frame, fg_color="transparent")
        self.header_btns_frame.pack(side="right", padx=5)
        
        self.new_file_btn = ctk.CTkButton(self.header_btns_frame, text="+", width=30, height=25, 
                                          fg_color="#00ADB5", hover_color="#007d82",
                                          font=("Arial", 14, "bold"), command=self.create_new_file_at_selection)
        self.new_file_btn.pack(side="left", padx=2)
        
        self.new_folder_btn = ctk.CTkButton(self.header_btns_frame, text="📁+", width=40, height=25, 
                                            fg_color="#00ADB5", hover_color="#007d82",
                                            font=("Arial", 12, "bold"), command=self.create_new_folder_at_selection)
        self.new_folder_btn.pack(side="left", padx=2)
        
        self.tree_scrollable = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.tree_scrollable.pack(fill="both", expand=True, padx=5, pady=5)

        # Search Results Section
        self.search_results_frame = ctk.CTkFrame(self.left_pane, corner_radius=10)
        self.search_results_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        
        self.search_header = ctk.CTkLabel(self.search_results_frame, text="Búsqueda", font=("Arial", 14, "bold"))
        self.search_header.pack(pady=5)
        
        self.search_scrollable = ctk.CTkScrollableFrame(self.search_results_frame, fg_color="transparent")
        self.search_scrollable.pack(fill="both", expand=True, padx=5, pady=5)
        self.search_widgets = []
        
        # Right Pane: Content Editor
        self.text_frame = ctk.CTkFrame(self.content_container, corner_radius=10)
        self.text_frame.grid(row=0, column=2, sticky="nsew")
        
        self.reader_header = ctk.CTkLabel(self.text_frame, text="Editor", font=("Arial", 14, "bold"))
        self.reader_header.pack(pady=(10, 5))
        
        # Editor controls (View mode, Font, Fullscreen)
        self.editor_controls_frame = ctk.CTkFrame(self.text_frame, fg_color="transparent")
        self.editor_controls_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # View mode selector
        self.view_mode_var = tk.StringVar(value="Ambos")
        self.view_mode_selector = ctk.CTkSegmentedButton(
            self.editor_controls_frame, values=["Bruto", "Condensado", "Ambos"],
            variable=self.view_mode_var, command=self.on_view_mode_change,
            font=("Arial", 12, "bold"), selected_color="#00ADB5",
            selected_hover_color="#007d82"
        )
        self.view_mode_selector.pack(side="left", padx=(0, 5))
        
        # Font style selector
        self.font_var = tk.StringVar(value="Georgia")
        self.font_selector = ctk.CTkOptionMenu(
            self.editor_controls_frame, values=["Georgia", "Arial", "Courier", "Helvetica", "Times", "Verdana"],
            variable=self.font_var, command=self.on_font_change,
            font=("Arial", 12), fg_color="#34495E", button_color="#2C3E50", button_hover_color="#00ADB5",
            width=110
        )
        self.font_selector.pack(side="left", padx=(0, 5))
        
        # Font size selector
        self.font_size_var = tk.StringVar(value="16")
        self.font_size_selector = ctk.CTkOptionMenu(
            self.editor_controls_frame, values=["10", "12", "14", "16", "18", "20", "24", "28", "32"],
            variable=self.font_size_var, command=self.on_font_change,
            font=("Arial", 12), fg_color="#34495E", button_color="#2C3E50", button_hover_color="#00ADB5",
            width=70
        )
        self.font_size_selector.pack(side="left", padx=(0, 5))
        
        # Fullscreen toggle button
        self.is_fullscreen_editor = False
        self.fullscreen_btn = ctk.CTkButton(
            self.editor_controls_frame, text="⛶", width=35, height=28,
            fg_color="#34495E", hover_color="#00ADB5",
            font=("Arial", 16), corner_radius=6, command=self.toggle_fullscreen_editor
        )
        self.fullscreen_btn.pack(side="left", padx=(0, 0))
        
        # Container for both text panes
        self.dual_pane_container = ctk.CTkFrame(self.text_frame, fg_color="transparent")
        self.dual_pane_container.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        self.dual_pane_container.grid_rowconfigure(0, weight=1)
        self.dual_pane_container.grid_columnconfigure(0, weight=1)
        self.dual_pane_container.grid_columnconfigure(1, weight=1)
        
        # Raw text pane
        self.raw_frame = ctk.CTkFrame(self.dual_pane_container, corner_radius=8)
        self.raw_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        self.raw_header = ctk.CTkLabel(self.raw_frame, text="📄 Información en Bruto",
                                       font=("Arial", 12, "bold"), text_color="#E67E22")
        self.raw_header.pack(pady=(5, 2))
        self.raw_text = ctk.CTkTextbox(self.raw_frame, font=("Georgia", 16), wrap="word", padx=20, pady=20)
        self.raw_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Condensed text pane
        self.condensed_frame = ctk.CTkFrame(self.dual_pane_container, corner_radius=8)
        self.condensed_frame.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
        self.condensed_header = ctk.CTkLabel(self.condensed_frame, text="📝 Información Condensada",
                                              font=("Arial", 12, "bold"), text_color="#2ECC71")
        self.condensed_header.pack(pady=(5, 2))
        self.condensed_text = ctk.CTkTextbox(self.condensed_frame, font=("Georgia", 16), wrap="word", padx=20, pady=20)
        self.condensed_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        self.save_changes_btn = ctk.CTkButton(self.text_frame, text="Guardar Cambios en Selección", 
                                              command=self.save_current_file,
                                              fg_color="#2ECC71", hover_color="#27AE60")
        self.save_changes_btn.pack(pady=5)
        
        # Apply initial view mode
        self.on_view_mode_change("Ambos")
        
        # State
        self.current_selected_path = None
        self.expanded_folders = {DOCS_DIR}
        self.tree_widgets = []
        self.searcher = TrustedSearcher()
        self.current_results = []
        self.state_file = "last_search.json"
        
        # Context Menu for Right Click
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Nuevo Documento", command=self.create_new_file_context)
        self.context_menu.add_command(label="Nueva Carpeta", command=self.create_new_folder_context)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Extraer Texto (HTML a Markdown)", command=self.convert_html_to_md_context)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Eliminar", command=self.delete_context)
        
        self.context_menu_target_path = DOCS_DIR
        self.context_menu_target_is_dir = True

        # Bind right-click on the scrollable frame background to create files in the root
        self.tree_scrollable._parent_canvas.bind("<Button-3>", lambda e: self.show_context_menu_root(e))
        self.tree_scrollable._parent_canvas.bind("<Button-2>", lambda e: self.show_context_menu_root(e)) # Mac Equivalent

        # Load tree
        self.refresh_tree()
        self.load_last_search_state()
        
    def show_context_menu_root(self, event):
        if self.current_selected_path and os.path.isdir(self.current_selected_path):
            self.context_menu_target_path = self.current_selected_path
            self.context_menu_target_is_dir = True
        else:
            self.context_menu_target_path = DOCS_DIR
            self.context_menu_target_is_dir = True
        self.show_context_menu(event)

    def show_context_menu_item(self, event, path, is_dir):
        self.context_menu_target_path = path
        self.context_menu_target_is_dir = is_dir
        self.show_context_menu(event)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def refresh_tree(self):
        for widget in self.tree_widgets:
            widget.destroy()
        self.tree_widgets.clear()
        
        def build_tree(current_path, level=0):
            try:
                items = sorted(os.listdir(current_path))
            except PermissionError:
                return
            
            for item in items:
                if item.startswith('.'):
                    continue
                full_path = os.path.join(current_path, item)
                is_dir = os.path.isdir(full_path)
                
                # Create tree item
                indent = "  " * level
                if is_dir:
                    is_expanded = full_path in self.expanded_folders
                    prefix = "▼ 📁 " if is_expanded else "▶ 📁 "
                else:
                    prefix = "  📄 "
                
                display_text = f"{indent}{prefix}{item}"
                
                # Highlight if selected
                is_selected = (full_path == self.current_selected_path)
                color = "#00ADB5" if is_selected else ("#34495E" if is_dir else "transparent")
                hover = "#007d82" if is_selected else ("#2C3E50" if is_dir else "#333333")
                
                btn = ctk.CTkButton(self.tree_scrollable, text=display_text, 
                                    anchor="w", fg_color=color, hover_color=hover,
                                    text_color="white", font=("Arial", 12),
                                    command=lambda p=full_path, d=is_dir: self.on_tree_click(p, d))
                btn.pack(fill="x", pady=1)
                
                # Bind right click on individual item
                btn.bind("<Button-3>", lambda e, p=full_path, d=is_dir: self.show_context_menu_item(e, p, d))
                btn.bind("<Button-2>", lambda e, p=full_path, d=is_dir: self.show_context_menu_item(e, p, d)) # Mac
                
                self.tree_widgets.append(btn)
                
                # Recursively parse directories if expanded
                if is_dir and full_path in self.expanded_folders:
                    build_tree(full_path, level + 1)
                    
        # Start recursion
        build_tree(DOCS_DIR, 0)

    def on_tree_click(self, path, is_dir):
        if is_dir:
            if path in self.expanded_folders:
                self.expanded_folders.remove(path)
            else:
                self.expanded_folders.add(path)
            
        self.on_tree_select(path, is_dir)
        self.refresh_tree()

    def toggle_left_pane(self):
        """Toggle the left sidebar visibility."""
        if self.left_pane_visible:
            self.left_pane.grid_forget()
            self.toggle_btn.configure(text="▶")
            self.left_pane_visible = False
        else:
            self.left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 0))
            self.toggle_btn.configure(text="◀")
            self.left_pane_visible = True

    def clear_search_results(self):
        for widget in self.search_widgets:
            widget.destroy()
        self.search_widgets.clear()

    def add_search_result(self, res_obj, index):
        color = "transparent"
        hover = "#333333"
        
        title = res_obj.get('title', 'Sin título')[:40] + "..." if len(res_obj.get('title', '')) > 40 else res_obj.get('title', 'Sin título')
        source = res_obj.get('source', 'Fuente')
        display_text = f"[{source}]\n{title}"
        text_color = "orange" if res_obj.get('is_google_general') else "#00ADB5"
        
        btn = ctk.CTkButton(self.search_scrollable, text=display_text, 
                            anchor="w", fg_color=color, hover_color=hover,
                            text_color=text_color, font=("Arial", 12),
                            command=lambda idx=index: self.on_search_result_select(idx))
        btn.pack(fill="x", pady=2)
        
        self.search_widgets.append(btn)

    def on_view_mode_change(self, mode):
        """Switch between Bruto, Condensado, or Ambos view modes."""
        # Hide all first
        self.raw_frame.grid_forget()
        self.condensed_frame.grid_forget()
        
        # Reset column weights
        self.dual_pane_container.grid_columnconfigure(0, weight=0)
        self.dual_pane_container.grid_columnconfigure(1, weight=0)
        
        if mode == "Bruto":
            self.dual_pane_container.grid_columnconfigure(0, weight=1)
            self.raw_frame.grid(row=0, column=0, sticky="nsew", padx=0)
        elif mode == "Condensado":
            self.dual_pane_container.grid_columnconfigure(0, weight=1)
            self.condensed_frame.grid(row=0, column=0, sticky="nsew", padx=0)
        else:  # Ambos
            self.dual_pane_container.grid_columnconfigure(0, weight=1)
            self.dual_pane_container.grid_columnconfigure(1, weight=1)
            self.raw_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
            self.condensed_frame.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
            
        self.save_last_search_state()

    def on_font_change(self, _=None):
        """Change the font family and size of the text editors."""
        font_name = self.font_var.get()
        font_size = int(self.font_size_var.get())
        self.raw_text.configure(font=(font_name, font_size))
        self.condensed_text.configure(font=(font_name, font_size))
        
        self.save_last_search_state()

    def toggle_fullscreen_editor(self):
        """Toggle between fullscreen editor and normal layout."""
        if self.is_fullscreen_editor:
            # Restore normal layout
            self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            self.status_label.grid(row=1, column=0, pady=(0, 5))
            if self.left_pane_visible:
                self.left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 0))
            self.toggle_btn.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=100)
            self.content_container.grid_configure(padx=20, pady=(0, 20))
            self.fullscreen_btn.configure(text="⛶")
            self.is_fullscreen_editor = False
        else:
            # Enter fullscreen: hide everything except the editor
            self.header_frame.grid_forget()
            self.status_label.grid_forget()
            self.left_pane.grid_forget()
            self.toggle_btn.grid_forget()
            self.content_container.grid_configure(padx=5, pady=5)
            self.fullscreen_btn.configure(text="✕")
            self.is_fullscreen_editor = True

    def _split_file_content(self, content):
        """Split file content into (raw, condensed) using the separator."""
        if CONDENSED_SEPARATOR in content:
            parts = content.split(CONDENSED_SEPARATOR, 1)
            return parts[0].rstrip('\n'), parts[1].lstrip('\n')
        return content, ""
    
    def _join_file_content(self, raw, condensed):
        """Join raw and condensed content with the separator."""
        if condensed.strip():
            return raw.rstrip('\n') + '\n' + CONDENSED_SEPARATOR + '\n' + condensed.lstrip('\n')
        return raw

    def on_search_result_select(self, index):
        self.current_selected_path = None
        
        if index < 0 or index >= len(self.current_results):
            return
            
        res = self.current_results[index]
        self.status_label.configure(text=f"Resultado Web cargado: {res.get('title', 'Sin título')}", text_color="white")
        self.reader_header.configure(text=f"Web: {res.get('source', 'Fuente')}")
        
        content = res.get('content', '')
        self.raw_text.delete('1.0', tk.END)
        self.raw_text.insert(tk.END, content)
        self.condensed_text.delete('1.0', tk.END)

    def on_tree_select(self, path, is_dir):
        self.current_selected_path = path
        if is_dir:
            self.status_label.configure(text=f"Carpeta seleccionada: {os.path.basename(path)}", text_color="white")
            self.raw_text.delete('1.0', tk.END)
            self.raw_text.insert(tk.END, "Seleccionaste una carpeta. Click derecho aquí en el panel o en un archivo para gestionar contenido.")
            self.condensed_text.delete('1.0', tk.END)
            self.reader_header.configure(text="Editor")
            return
            
        self.status_label.configure(text=f"Archivo cargado: {os.path.basename(path)}", text_color="white")
        self.reader_header.configure(text=f"Editando: {os.path.basename(path)}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            raw_content, condensed_content = self._split_file_content(content)
            self.raw_text.delete('1.0', tk.END)
            self.raw_text.insert(tk.END, raw_content)
            self.condensed_text.delete('1.0', tk.END)
            self.condensed_text.insert(tk.END, condensed_content)
        except Exception as e:
            self.raw_text.delete('1.0', tk.END)
            self.raw_text.insert(tk.END, f"Error al leer el archivo: {e}")
            self.condensed_text.delete('1.0', tk.END)

    def save_current_file(self):
        raw_content = self.raw_text.get("1.0", "end-1c")
        condensed_content = self.condensed_text.get("1.0", "end-1c")
        content = self._join_file_content(raw_content, condensed_content)
        
        if not self.current_selected_path:
            # Determine where to save: current selected folder or root
            default_dir = self.current_selected_path if self.current_selected_path and os.path.isdir(self.current_selected_path) else DOCS_DIR
            
            dialog = ctk.CTkInputDialog(text=f"Guardar resultado web en {os.path.basename(default_dir)} como (ej. articulo.md):", title="Guardar Documento Local")
            name = dialog.get_input()
            if not name:
                return
            if not '.' in name:
                name += '.md'
                
            path = os.path.join(default_dir, name)
            self.current_selected_path = path
            
        elif os.path.isdir(self.current_selected_path):
            self.status_label.configure(text="Selecciona o crea un archivo válido para guardar.", text_color="orange")
            return
            
        try:
            with open(self.current_selected_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.refresh_tree()
            self.status_label.configure(text="Archivo guardado correctamente.", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error al guardar: {e}", text_color="red")

    def create_new_file_at_selection(self):
        # Target: selected folder OR the parent folder of selected file
        if self.current_selected_path:
            if os.path.isdir(self.current_selected_path):
                target = self.current_selected_path
            else:
                target = os.path.dirname(self.current_selected_path)
        else:
            target = DOCS_DIR
            
        self.context_menu_target_path = target
        self.context_menu_target_is_dir = True
        self.create_new_file_context()

    def create_new_folder_at_selection(self):
        if self.current_selected_path:
            if os.path.isdir(self.current_selected_path):
                target = self.current_selected_path
            else:
                target = os.path.dirname(self.current_selected_path)
        else:
            target = DOCS_DIR
            
        self.context_menu_target_path = target
        self.context_menu_target_is_dir = True
        self.create_new_folder_context()

    def create_new_file_context(self):
        parent = self.context_menu_target_path if self.context_menu_target_is_dir else os.path.dirname(self.context_menu_target_path)
        
        dialog = ctk.CTkInputDialog(text=f"Nombre del nuevo documento en {os.path.basename(parent)} (ej. notas.txt):", title="Nuevo Documento")
        name = dialog.get_input()
        if not name:
            return
        if not '.' in name:
            name += '.txt'
            
        path = os.path.join(parent, name)
        
        if os.path.exists(path):
            self.status_label.configure(text="El archivo ya existe.", text_color="red")
            return
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("")
            self.expanded_folders.add(parent)
            self.refresh_tree()
            self.on_tree_select(path, False)
            self.status_label.configure(text=f"Documento creado: {name}", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error al crear: {e}", text_color="red")

    def create_new_folder_context(self):
        parent = self.context_menu_target_path if self.context_menu_target_is_dir else os.path.dirname(self.context_menu_target_path)
        
        dialog = ctk.CTkInputDialog(text=f"Nombre de la nueva carpeta en {os.path.basename(parent)}:", title="Nueva Carpeta")
        name = dialog.get_input()
        if not name:
            return
            
        path = os.path.join(parent, name)
        
        if os.path.exists(path):
            self.status_label.configure(text="La carpeta ya existe.", text_color="red")
            return
            
        try:
            os.makedirs(path)
            self.expanded_folders.add(parent)
            self.expanded_folders.add(path)
            self.refresh_tree()
            self.status_label.configure(text=f"Carpeta creada: {name}", text_color="#00FF00")
            self.on_tree_select(path, True)
        except Exception as e:
            self.status_label.configure(text=f"Error al crear: {e}", text_color="red")

    def convert_html_to_md_context(self):
        path = self.context_menu_target_path
        if not path or self.context_menu_target_is_dir or not path.lower().endswith(('.html', '.htm')):
            self.status_label.configure(text="Selecciona un archivo .html para convertir.", text_color="orange")
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            md_text = trafilatura.extract(html_content, output_format='markdown')
            
            if not md_text:
                self.status_label.configure(text="No se pudo extraer texto relevante del HTML.", text_color="red")
                return
                
            new_name = os.path.splitext(os.path.basename(path))[0] + ".md"
            new_path = os.path.join(os.path.dirname(path), new_name)
            
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(md_text)
                
            self.refresh_tree()
            self.on_tree_select(new_path, False)
            self.status_label.configure(text=f"HTML convertido a MD con éxito: {new_name}", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error al transformar HTML: {e}", text_color="red")

    def delete_context(self):
        path_to_delete = self.context_menu_target_path
        
        if path_to_delete == DOCS_DIR or not path_to_delete:
            self.status_label.configure(text="No puedes eliminar la carpeta raíz.", text_color="orange")
            return
            
        name = os.path.basename(path_to_delete)
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar '{name}'?")
        if not confirm:
            return
            
        try:
            if os.path.isdir(path_to_delete):
                shutil.rmtree(path_to_delete)
            else:
                os.remove(path_to_delete)
                
            if self.current_selected_path == path_to_delete:
                self.raw_text.delete('1.0', tk.END)
                self.condensed_text.delete('1.0', tk.END)
                self.reader_header.configure(text="Editor")
                self.current_selected_path = None
                
            self.refresh_tree()
            self.status_label.configure(text=f"Eliminado: {name}", text_color="#00FF00")
        except Exception as e:
            self.status_label.configure(text=f"Error al eliminar: {e}", text_color="red")

    def start_search(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            return
            
        self.status_label.configure(text=f"Buscando en internet '{query}'... (está tardando unos segundos)", text_color="#00ADB5")
        
        self.clear_search_results()
        self.current_results = []
        self.save_last_search_state() # Save empty state immediately so old ones are erased
        
        self.raw_text.delete('1.0', tk.END)
        self.condensed_text.delete('1.0', tk.END)
        self.search_button.configure(state="disabled")
        
        threading.Thread(target=self.perform_search, args=(query,), daemon=True).start()

    def perform_search(self, query):
        try:
            total_found = 0
            for chunk_results in self.searcher.search_generator(query, max_results=20):
                if not chunk_results:
                    continue
                
                is_general = any(r.get('is_google_general') for r in chunk_results)
                msg = f"Encontrados {len(chunk_results)} enlaces. Extrayendo..." if not is_general else f"Búsqueda general... ({len(chunk_results)})"
                self.root.after(0, lambda m=msg: self.status_label.configure(text=m, text_color="#00ADB5"))
                
                detailed_batch = self.searcher.fetch_full_content(chunk_results)
                
                if detailed_batch:
                    self.current_results.extend(detailed_batch)
                    total_found += len(detailed_batch)
                    self.root.after(0, lambda batch=detailed_batch: self.append_results_to_ui(batch))
            
            final_msg = f"Búsqueda finalizada. Total: {total_found} resultados legibles."
            color = "#00FF00" if total_found > 0 else "orange"
            self.root.after(0, lambda: self.status_label.configure(text=final_msg, text_color=color))
            self.root.after(0, self.save_last_search_state)

        except Exception as e:
            self.root.after(0, lambda err=e: self.status_label.configure(text=f"Error: {str(err)}", text_color="red"))
        finally:
             self.root.after(0, lambda: self.search_button.configure(state="normal"))

    def append_results_to_ui(self, new_results):
        start_index = len(self.current_results) - len(new_results)
        for i, res in enumerate(new_results):
            actual_index = start_index + i
            self.add_search_result(res, actual_index)
            
        if self.current_results and len(self.search_widgets) == len(new_results):
            self.on_search_result_select(0)

    def save_last_search_state(self):
        try:
            state = {
                "query": self.search_var.get(),
                "results": self.current_results,
                "view_mode": self.view_mode_var.get(),
                "font_family": self.font_var.get(),
                "font_size": self.font_size_var.get()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving search state: {e}")

    def load_last_search_state(self):
        if not os.path.exists(self.state_file):
            return
            
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            self.search_var.set(state.get("query", ""))
            self.current_results = state.get("results", [])
            
            # Load preferences
            view_mode = state.get("view_mode", "Ambos")
            self.view_mode_var.set(view_mode)
            self.on_view_mode_change(view_mode)
            
            font_family = state.get("font_family", "Georgia")
            self.font_var.set(font_family)
            font_size = state.get("font_size", "16")
            self.font_size_var.set(font_size)
            self.on_font_change()
            
            if self.current_results:
                self.append_results_to_ui(self.current_results)
                self.status_label.configure(text=f"Se cargaron los resultados de la última búsqueda y preferencias.", text_color="#00ADB5")
        except Exception as e:
            print(f"Error loading search state: {e}")


if __name__ == "__main__":
    app = ctk.CTk()
    gui = DocumentManagerApp(app)
    app.mainloop()
