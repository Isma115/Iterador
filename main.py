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
        self.content_container.grid_columnconfigure(1, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Left Pane container (Split into Tree and Search Results)
        self.left_pane = ctk.CTkFrame(self.content_container, width=300, corner_radius=10, fg_color="transparent")
        self.left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        self.left_pane.grid_propagate(False)
        self.left_pane.grid_rowconfigure(0, weight=1) # Explorer gets more space initially or equal
        self.left_pane.grid_rowconfigure(1, weight=1) # Search gets equal space
        
        # Explorer Section
        self.list_frame = ctk.CTkFrame(self.left_pane, corner_radius=10)
        self.list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        
        self.list_header = ctk.CTkLabel(self.list_frame, text="Explorador", font=("Arial", 14, "bold"))
        self.list_header.pack(pady=5)
        
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
        self.text_frame.grid(row=0, column=1, sticky="nsew")
        
        self.reader_header = ctk.CTkLabel(self.text_frame, text="Editor", font=("Arial", 14, "bold"))
        self.reader_header.pack(pady=10)
        
        self.content_text = ctk.CTkTextbox(self.text_frame, font=("Georgia", 16), wrap="word", padx=20, pady=20)
        self.content_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.save_changes_btn = ctk.CTkButton(self.text_frame, text="Guardar Cambios en Selección", 
                                              command=self.save_current_file,
                                              fg_color="#2ECC71", hover_color="#27AE60")
        self.save_changes_btn.pack(pady=10)
        
        # State
        self.current_selected_path = None
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

    def refresh_tree(self, search_query=None):
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
                
                if search_query:
                    search_lower = search_query.lower()
                    match_found = False
                    
                    if search_lower in item.lower():
                        match_found = True
                    elif not is_dir:
                        # Full text search inside the file gracefully
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if search_lower in content.lower():
                                    match_found = True
                        except:
                            pass
                            
                    if match_found and not is_dir:
                        self.add_search_result(full_path, item)
                        
                # Create tree item
                indent = "  " * level
                prefix = "📁 " if is_dir else "📄 "
                display_text = f"{indent}{prefix}{item}"
                
                color = "#34495E" if is_dir else "transparent"
                hover = "#2C3E50" if is_dir else "#333333"
                
                btn = ctk.CTkButton(self.tree_scrollable, text=display_text, 
                                    anchor="w", fg_color=color, hover_color=hover,
                                    text_color="white", font=("Arial", 12),
                                    command=lambda p=full_path, d=is_dir: self.on_tree_select(p, d))
                btn.pack(fill="x", pady=1)
                
                # Bind right click on individual item
                btn.bind("<Button-3>", lambda e, p=full_path, d=is_dir: self.show_context_menu_item(e, p, d))
                btn.bind("<Button-2>", lambda e, p=full_path, d=is_dir: self.show_context_menu_item(e, p, d)) # Mac
                
                self.tree_widgets.append(btn)
                
                # Recursively parse directories
                if is_dir and not search_query:
                    build_tree(full_path, level + 1)
                    
        # Start recursion
        build_tree(DOCS_DIR, 0)

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

    def on_search_result_select(self, index):
        self.current_selected_path = None
        
        if index < 0 or index >= len(self.current_results):
            return
            
        res = self.current_results[index]
        self.status_label.configure(text=f"Resultado Web cargado: {res.get('title', 'Sin título')}", text_color="white")
        self.reader_header.configure(text=f"Web: {res.get('source', 'Fuente')}")
        
        content = res.get('content', '')
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert(tk.END, content)

    def on_tree_select(self, path, is_dir):
        self.current_selected_path = path
        if is_dir:
            self.status_label.configure(text=f"Carpeta seleccionada: {os.path.basename(path)}", text_color="white")
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert(tk.END, "Seleccionaste una carpeta. Click derecho aquí en el panel o en un archivo para gestionar contenido.")
            self.reader_header.configure(text="Editor")
            return
            
        self.status_label.configure(text=f"Archivo cargado: {os.path.basename(path)}", text_color="white")
        self.reader_header.configure(text=f"Editando: {os.path.basename(path)}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert(tk.END, content)
        except Exception as e:
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert(tk.END, f"Error al leer el archivo: {e}")

    def save_current_file(self):
        content = self.content_text.get("1.0", "end-1c")
        
        if not self.current_selected_path:
            # We are likely viewing a web result, let the user save it
            dialog = ctk.CTkInputDialog(text=f"Guardar resultado web como (ej. articulo.md):", title="Guardar Documento Local")
            name = dialog.get_input()
            if not name:
                return
            if not '.' in name:
                name += '.md'
                
            path = os.path.join(DOCS_DIR, name)
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
                self.content_text.delete('1.0', tk.END)
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
        
        self.content_text.delete('1.0', tk.END)
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
                "results": self.current_results
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
            
            if self.current_results:
                self.append_results_to_ui(self.current_results)
                self.status_label.configure(text=f"Se cargaron los resultados de la última búsqueda: '{self.search_var.get()}'", text_color="#00ADB5")
        except Exception as e:
            print(f"Error loading search state: {e}")


if __name__ == "__main__":
    app = ctk.CTk()
    gui = DocumentManagerApp(app)
    app.mainloop()
