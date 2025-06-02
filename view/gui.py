import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from controller.controller import Controller, ReplacementAlgorithm 
import random
import time

class MMUSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador MMU y Gestión de Memoria Virtual")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

        self.controller = Controller()

        self.setup_styles()
        self.create_widgets()
        
        self.root.after(100, self.update_displays) 
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       foreground='#ecf0f1',
                       background='#2c3e50')
        
        style.configure('Heading.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground='#3498db',
                       background='#34495e')
        
        style.configure('Custom.TFrame',
                       background='#34495e',
                       relief='raised',
                       borderwidth=2)
    
    def create_widgets(self):
        title_label = ttk.Label(self.root, 
                               text="🖥️ Simulador MMU y Gestión de Memoria Virtual",
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.create_address_translation_tab(notebook)
        self.create_process_management_tab(notebook)
        self.create_system_status_tab(notebook)
        self.create_analysis_tab(notebook)
    
    def create_address_translation_tab(self, parent):
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="🔄 Traducción de Direcciones")
        
        input_frame = ttk.LabelFrame(frame, text="Entrada de Direcciones", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="Dirección Simbólica:").grid(row=0, column=0, sticky='w', padx=5)
        self.symbolic_entry = ttk.Entry(input_frame, width=30)
        self.symbolic_entry.grid(row=0, column=1, padx=5)
        self.symbolic_entry.insert(0, "Ingrese dirección simbólica")
        
        translate_btn = ttk.Button(input_frame, text="🔍 Traducir Dirección",
                                  command=self.translate_address)
        translate_btn.grid(row=0, column=2, padx=10)
        
        translation_frame = ttk.LabelFrame(frame, text="Etapas de Traducción", padding=10)
        translation_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.translation_text = scrolledtext.ScrolledText(translation_frame, 
                                                         height=15, 
                                                         font=('Courier', 10),
                                                         bg='#ecf0f1',
                                                         fg='#2c3e50',
                                                         wrap=tk.WORD) # Added wrap
        self.translation_text.pack(fill='both', expand=True)
        self.translation_text.config(state=tk.DISABLED)
    
    def create_process_management_tab(self, parent):
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="⚙️ Gestión de Procesos")
        
        process_frame = ttk.LabelFrame(frame, text="Crear Proceso", padding=10)
        process_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(process_frame, text="PID:").grid(row=0, column=0, sticky='w')
        self.pid_entry = ttk.Entry(process_frame, width=10)
        self.pid_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(process_frame, text="Tamaño (KB):").grid(row=0, column=2, sticky='w', padx=(20,0))
        self.size_entry = ttk.Entry(process_frame, width=10)
        self.size_entry.grid(row=0, column=3, padx=5)
        
        create_btn = ttk.Button(process_frame, text="➕ Crear Proceso",
                               command=self.create_process)
        create_btn.grid(row=0, column=4, padx=10)
        
        list_frame = ttk.LabelFrame(frame, text="Lista de Procesos", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.process_tree = ttk.Treeview(list_frame, 
                                       columns=('PID', 'Tamaño', 'Páginas', 'Estado'),
                                       show='headings')
        
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Tamaño', text='Tamaño (KB)')
        self.process_tree.heading('Páginas', text='Páginas')
        self.process_tree.heading('Estado', text='Estado')
        
        self.process_tree.column('PID', width=80, anchor='center')
        self.process_tree.column('Tamaño', width=100, anchor='center')
        self.process_tree.column('Páginas', width=80, anchor='center')
        self.process_tree.column('Estado', width=100, anchor='center')
        
        self.process_tree.pack(fill='both', expand=True)
    
    def create_system_status_tab(self, parent):
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="⚡ Simulación de carga")

        active_frame = ttk.LabelFrame(frame, text="Proceso Activo", padding=10)
        active_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(active_frame, text="Proceso Activo:").grid(row=0, column=0, sticky='w')
        self.active_process_var2 = tk.StringVar()
        self.active_process_combo2 = ttk.Combobox(active_frame,
                                                  textvariable=self.active_process_var2,
                                                  state='readonly')
        self.active_process_combo2.grid(row=0, column=1, padx=5)
        self.active_process_combo2.bind('<<ComboboxSelected>>', self.set_active_process)

        ttk.Label(active_frame, text="Algoritmo:").grid(row=0, column=2, sticky='w', padx=(20, 0))
        self.algorithm_var2 = tk.StringVar(value="FIFO")
        algorithm_combo2 = ttk.Combobox(active_frame,
                                        textvariable=self.algorithm_var2,
                                        values=["FIFO", "LRU"],
                                        state='readonly')
        algorithm_combo2.grid(row=0, column=3, padx=5)
        algorithm_combo2.bind('<<ComboboxSelected>>', self.change_algorithm)

        access_frame = ttk.LabelFrame(frame, text="Simulación de Accesos", padding=10)
        access_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(access_frame, text="Acceso Aleatorio",
                   command=self.gui_random_access).pack(side='left', padx=5)
        ttk.Button(access_frame, text="Simular Carga Intensiva",
                   command=self.gui_intensive_load).pack(side='left', padx=5)
        ttk.Button(access_frame, text="Reiniciar Sistema",
                   command=self.reset_system).pack(side='left', padx=5)

        # NUEVO LAYOUT: Un solo PanedWindow horizontal con tres paneles
        main_pane = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill='both', expand=True, padx=10, pady=10)

        # 1. Tabla de páginas (izquierda)
        page_table_frame = ttk.LabelFrame(main_pane, text="Tabla de Páginas del Proceso Activo", padding=10)
        self.page_table_tree = ttk.Treeview(page_table_frame,
                                            columns=('Página', 'Marco', 'Estado', 'Acceso'),
                                            show='headings')
        for col in ['Página', 'Marco', 'Estado', 'Acceso']:
            self.page_table_tree.heading(col, text=col)
            self.page_table_tree.column(col, width=90, anchor='center')
        self.page_table_tree.column('Estado', width=90)
        self.page_table_tree.pack(fill='both', expand=True)
        main_pane.add(page_table_frame, weight=1)  # 30%

        # 2. Swap (centro)
        swap_frame = ttk.LabelFrame(main_pane, text="Espacio de Intercambio (Swap)", padding=10)
        self.swap_tree = ttk.Treeview(swap_frame, columns=('PID', 'Página', 'Accesos'), show='headings')
        self.swap_tree.heading('PID', text='PID')
        self.swap_tree.heading('Página', text='Página')
        self.swap_tree.heading('Accesos', text='Accesos')
        self.swap_tree.column('PID', width=80, anchor='center')
        self.swap_tree.column('Página', width=80, anchor='center')
        self.swap_tree.column('Accesos', width=80, anchor='center')
        self.swap_tree.pack(fill='both', expand=True)
        main_pane.add(swap_frame, weight=2)        # 20%

        # 3. Memoria física (derecha)
        memory_frame = ttk.LabelFrame(main_pane, text="Memoria Física", padding=10)
        self.memory_canvas = tk.Canvas(memory_frame, bg='white', highlightthickness=0)
        self.memory_canvas.pack(fill='both', expand=True)
        main_pane.add(memory_frame, weight=5)      # 50%
    
    def create_analysis_tab(self, parent):
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="📊 Análisis y Estadísticas")
        
        stats_frame = ttk.LabelFrame(frame, text="Estadísticas del Sistema", padding=15)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        self.stats_labels = {}
        stats_items = [
            ('Accesos Totales:', 'access_count'), ('Page Hits:', 'page_hits'), ('Page Faults:', 'page_faults'),
            ('Tasa de Aciertos:', 'hit_rate'), ('Tasa de Fallos:', 'fault_rate'), ('Swaps In:', 'swaps_in'),
            ('Swaps Out:', 'swaps_out'), ('Páginas en Swap:', 'pages_in_swap'), ('Algoritmo:', 'algorithm')
        ]
        
        row, col_limit = 0, 3
        for i, (label_text, key) in enumerate(stats_items):
            ttk.Label(stats_grid, text=label_text, font=('Arial', 10, 'bold')).grid(
                row=row, column=(i % col_limit)*2, sticky='w', padx=5, pady=3)
            
            self.stats_labels[key] = ttk.Label(stats_grid, text="0", font=('Arial', 10))
            self.stats_labels[key].grid(row=row, column=(i % col_limit)*2+1, sticky='e', padx=5, pady=3)
            if (i + 1) % col_limit == 0:
                row += 1
        
        analysis_frame = ttk.LabelFrame(frame, text="Análisis de Rendimiento", padding=10)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        thrashing_btn = ttk.Button(analysis_frame, text="Detectar Hiperpaginación",
                                 command=self.check_thrashing)
        thrashing_btn.pack(pady=5)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame,
                                                     height=10, # Adjusted height
                                                     font=('Courier', 10),
                                                     bg='#f8f9fa',
                                                     fg='#2c3e50',
                                                     wrap=tk.WORD)
        self.analysis_text.pack(fill='both', expand=True)
        self.analysis_text.config(state=tk.DISABLED)
        
        self.show_initial_analysis()
    
    def translate_address(self):
        symbolic_addr = self.symbolic_entry.get().strip()
        if not symbolic_addr:
            messagebox.showwarning("Advertencia", "Ingrese una dirección simbólica.")
            return

        if not self.controller.get_current_process():
            messagebox.showwarning("Advertencia", "Seleccione o cree un proceso activo.")
            return

        stages, logical_addr = self.controller.simulate_address_translation_stages(symbolic_addr)
        
        self.translation_text.config(state=tk.NORMAL)
        self.translation_text.delete(1.0, tk.END)
        self.translation_text.insert(tk.END, "🔄 PROCESO DE TRADUCCIÓN DE DIRECCIONES\n")
        self.translation_text.insert(tk.END, "=" * 60 + "\n\n") # Increased separator length
        
        for stage in stages:
            self.translation_text.insert(tk.END, stage + "\n")
        
        if logical_addr is not None:
            page_number = logical_addr // self.controller.get_page_size()
            offset = logical_addr % self.controller.get_page_size()
            
            self.translation_text.insert(tk.END, f"\n📋 DETALLES DE LA MMU (para Dirección Lógica 0x{logical_addr:08X}):\n")
            self.translation_text.insert(tk.END, f"  Número de página virtual: {page_number}\n")
            self.translation_text.insert(tk.END, f"  Desplazamiento (Offset): {offset} (0x{offset:03X})\n") # Hex offset
            self.translation_text.insert(tk.END, f"  Tamaño de página: {self.controller.get_page_size()} bytes\n")
        else:
            self.translation_text.insert(tk.END, "\nNo se pudieron calcular detalles de MMU (dirección lógica no determinada o error previo).\n")
            
        self.translation_text.config(state=tk.DISABLED)
        self.update_displays()
    
    def create_process(self):
        try:
            pid = self.pid_entry.get().strip()
            size_kb_str = self.size_entry.get().strip()
            
            if not pid:
                messagebox.showwarning("Advertencia", "Ingrese un PID válido.")
                return
            if not size_kb_str:
                messagebox.showwarning("Advertencia", "Ingrese un tamaño para el proceso.")
                return
            
            size_kb = int(size_kb_str)
            if size_kb <= 0:
                messagebox.showwarning("Advertencia", "El tamaño debe ser mayor a 0 KB.")
                return
            
            success, message = self.controller.create_process(pid, size_kb)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.pid_entry.delete(0, tk.END)
                self.size_entry.delete(0, tk.END)
                self.update_displays() # Full update
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Ingrese un tamaño numérico válido para KB.")
    
    def set_active_process(self, event=None):
        selected_pid = self.active_process_var2.get()
        if selected_pid:
            self.controller.set_current_process(selected_pid)
            self.active_process_var2.set(selected_pid)
            self.update_displays()

    def change_algorithm(self, event=None):
        algorithm = self.algorithm_var2.get()
        self.controller.change_algorithm(algorithm)
        self.algorithm_var2.set(algorithm)
        self.update_displays()

    def gui_random_access(self): # Renamed
        current_pid = self.controller.get_current_process()
        if not current_pid:
            messagebox.showwarning("Advertencia", "Seleccione un proceso activo.")
            return
        
        process_data = self.controller.get_processes().get(current_pid)
        if not process_data or process_data['pages_needed'] == 0:
            messagebox.showinfo("Información", f"El proceso {current_pid} no tiene páginas o no existe.")
            return

        max_address = process_data['pages_needed'] * self.controller.get_page_size() - 1
        random_address = random.randint(0, max_address)
        
        # Call the corrected simulate_memory_access
        self.simulate_gui_memory_access(random_address) # Calls the corrected GUI method
        
        page_num = random_address // self.controller.get_page_size()
        # Optional: Show less intrusive info, or log it, instead of messagebox for every random access
        # messagebox.showinfo("Acceso Aleatorio", 
        #                   f"Proceso: {current_pid}\n"
        #                   f"Dirección Virtual: 0x{random_address:08X}\n"
        #                   f"Accediendo a Página: {page_num}")
        # Update display for this specific access in the translation tab for feedback
        self.translation_text.config(state=tk.NORMAL)
        self.translation_text.insert(tk.END, f"\n---\n[Acceso Aleatorio] Proceso: {current_pid}, Dir Virtual: 0x{random_address:08X} (Página {page_num})\n")
        # Get translation stages for this random access to show feedback
        stages, _ = self.controller.simulate_address_translation_stages(f"random_access_to_0x{random_address:08X}")
        for stage in stages:
            self.translation_text.insert(tk.END, stage + "\n")
        self.translation_text.see(tk.END) # Scroll to end
        self.translation_text.config(state=tk.DISABLED)


    def simulate_gui_memory_access(self, address): # Renamed to avoid conflict with controller
        """GUI method to trigger memory access simulation via the controller."""
        current_pid = self.controller.get_current_process()
        if not current_pid:
            # This should be caught by the caller (e.g., gui_random_access)
            return
            
        # Delegate to controller's simulate_memory_access method
        # This call will handle translation, page faults, and updating modified bit
        self.controller.simulate_memory_access(address)
        
        # After access, update all relevant displays
        self.update_displays()

    def gui_intensive_load(self): # Renamed
        current_pid = self.controller.get_current_process()
        if not current_pid:
            messagebox.showwarning("Advertencia", "Seleccione un proceso activo.")
            return
        
        process_data = self.controller.get_processes().get(current_pid)
        if not process_data or process_data['pages_needed'] == 0:
            messagebox.showinfo("Información", f"El proceso {current_pid} no tiene páginas para carga intensiva.")
            return

        # Provide feedback in translation tab
        self.translation_text.config(state=tk.NORMAL)
        self.translation_text.delete(1.0, tk.END) # Clear previous
        self.translation_text.insert(tk.END, f"INICIANDO CARGA INTENSIVA PARA PROCESO {current_pid}\n")
        self.translation_text.insert(tk.END, "=" * 60 + "\n\n")
        self.translation_text.config(state=tk.DISABLED)

        num_accesses = 20 # Reduced for faster UI response, was 50
        for i in range(num_accesses):
            max_address = process_data['pages_needed'] * self.controller.get_page_size() - 1
            random_address = random.randint(0, max_address)
            
            # Call the corrected simulate_memory_access
            self.simulate_gui_memory_access(random_address) # This updates displays internally too

            # Update translation tab with info about this specific access
            page_num = random_address // self.controller.get_page_size()
            self.translation_text.config(state=tk.NORMAL)
            self.translation_text.insert(tk.END, f"Acceso {i+1}/{num_accesses}: Dir Virtual 0x{random_address:08X} (Página {page_num})\n")
            
            # Get short status of this access for the log
            # We can't directly get "hit" or "fault" message easily without re-translating
            # So we rely on statistics updating. For more detailed log here, would need more complex return from controller.
            # For now, just log the access. Detailed translation for individual addresses is via the "Traducir Dirección" button.

            self.translation_text.see(tk.END) # Scroll to end
            self.translation_text.config(state=tk.DISABLED)

            time.sleep(0.02) # Shorter sleep for faster simulation
            self.root.update_idletasks() 
        
        self.translation_text.config(state=tk.NORMAL)
        self.translation_text.insert(tk.END, "\nCARGA INTENSIVA COMPLETADA\n")
        self.translation_text.see(tk.END)
        self.translation_text.config(state=tk.DISABLED)

        self.check_thrashing() 
        self.update_displays() # Final comprehensive update


    def reset_system(self):
        if messagebox.askyesno("Confirmar Reinicio", "Esto eliminará todos los procesos y estadísticas. ¿Continuar?"):
            self.controller.reset_system()
            self.active_process_var.set("") # Clear active process display
            self.active_process_var2.set("") # Clear active process display in second combo
            self.translation_text.config(state=tk.NORMAL)
            self.translation_text.delete(1.0, tk.END)
            self.translation_text.config(state=tk.DISABLED)
            self.update_displays()
            self.show_initial_analysis()
            messagebox.showinfo("Sistema Reiniciado", "Todos los procesos y estadísticas han sido reiniciados.")

    def update_process_list(self):
        self.process_tree.delete(*self.process_tree.get_children())
        
        processes_dict = self.controller.get_processes()
        process_pids = list(processes_dict.keys())
        # Solo actualiza el combo de la pestaña de simulación de carga
        self.active_process_combo2['values'] = process_pids
        
        current_selection = self.active_process_var2.get()
        current_controller_pid = self.controller.get_current_process()

        if not process_pids:
            self.controller.set_current_process(None)
            self.active_process_var2.set("")
        elif current_selection and current_selection in process_pids:
            if current_controller_pid != current_selection:
                self.controller.set_current_process(current_selection)
            self.active_process_var2.set(current_selection)
        elif current_controller_pid and current_controller_pid in process_pids:
            self.active_process_var2.set(current_controller_pid)
        elif process_pids:
            self.controller.set_current_process(process_pids[0])
            self.active_process_var2.set(process_pids[0])
        else:
            self.controller.set_current_process(None)
            self.active_process_var2.set("")

        for pid, data in processes_dict.items():
            status = "Activo" if pid == self.controller.get_current_process() else "Inactivo"
            self.process_tree.insert('', 'end', 
                                  values=(pid, data['size_kb'], data['pages_needed'], status))

    def update_memory_display(self):
        self.memory_canvas.delete("all")
        self.root.update_idletasks()
        canvas_width = self.memory_canvas.winfo_width()
        canvas_height = self.memory_canvas.winfo_height()

        max_frames = 10
        physical_memory = self.controller.get_physical_memory()[:max_frames]
        physical_pages_count = len(physical_memory)

        if canvas_width <= 1 or canvas_height <= 1:
            self.memory_canvas.create_text(50, 20, text="Cargando memoria...", fill="gray", anchor="nw")
            return

        if physical_pages_count == 0:
            self.memory_canvas.create_text(canvas_width/2, canvas_height/2, text="No hay memoria física", fill="red")
            return

        frame_height = canvas_height / physical_pages_count

        if not hasattr(self, 'process_color_map'):
            self.process_color_map = {}

        base_colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#d35400', '#7f8c8d']

        for i in range(physical_pages_count):
            y1 = i * frame_height
            y2 = (i + 1) * frame_height

            content = physical_memory[i]
            text_fill = '#2c3e50'

            if content is None:
                frame_color = '#ecf0f1'
                text = f"Marco {i} | Libre"
            else:
                pid, page = content
                if pid not in self.process_color_map:
                    self.process_color_map[pid] = base_colors[len(self.process_color_map) % len(base_colors)]
                frame_color = self.process_color_map[pid]
                page_table = self.controller.get_page_table(pid)
                access_time = "-"
                if page in page_table:
                    access_time = page_table[page].get('access_time', '-')
                text = f"Marco {i} | PID: {pid} | Página: {page} | Acceso: {access_time}"
                text_fill = '#ffffff'

            self.memory_canvas.create_rectangle(5, y1, canvas_width-5, y2,
                                               fill=frame_color, outline='#7f8c8d', width=1)
            self.memory_canvas.create_text(canvas_width/2, y1 + frame_height/2,
                                          text=text, font=('Arial', 8 if frame_height > 30 else 7), fill=text_fill, justify=tk.CENTER)

    def update_page_table_display(self):
        self.page_table_tree.delete(*self.page_table_tree.get_children())
        current_pid = self.controller.get_current_process()
        if not current_pid:
            return
        
        page_table = self.controller.get_page_table(current_pid)
        if not page_table:
            return

        for page_num, entry in sorted(page_table.items()):
            frame = entry.get('physical_frame', '-') if entry.get('physical_frame') is not None else "-"
            status_val = entry.get('status')
            status_str = status_val.value if hasattr(status_val, 'value') else str(status_val)
            access_t = entry.get('access_time', '-')
            self.page_table_tree.insert('', 'end', 
                                      values=(page_num, frame, status_str, access_t))

    def update_swap_display(self):
        # Ahora actualiza la tabla en vez del texto
        if hasattr(self, 'swap_tree'):
            self.swap_tree.delete(*self.swap_tree.get_children())
            swap_space = self.controller.get_swap_space()
            for key in sorted(swap_space.keys()):
                # key es del tipo "pid_pagina"
                try:
                    pid, pagina = key.split('_')
                except ValueError:
                    pid, pagina = key, "?"
                # Buscar accesos en la tabla de páginas del proceso
                page_table = self.controller.get_page_table(pid)
                accesos = "-"
                if page_table and pagina.isdigit():
                    entry = page_table.get(int(pagina))
                    if entry:
                        accesos = entry.get('access_time', '-')
                self.swap_tree.insert('', 'end', values=(pid, pagina, accesos))
        else:
            # Fallback si swap_tree no existe (por ejemplo, en otras pestañas)
            pass

    def update_stats_display(self):
        stats = self.controller.get_statistics()
        for key, value in stats.items():
            if key in self.stats_labels:
                if key in ['hit_rate', 'fault_rate']:
                    self.stats_labels[key].config(text=f"{float(value):.2f}%")
                else:
                    self.stats_labels[key].config(text=str(value))

    def check_thrashing(self):
        thrashing, msg = self.controller.detect_thrashing()
        
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "📈 ANÁLISIS DE RENDIMIENTO (HIPERPAGINACIÓN)\n")
        self.analysis_text.insert(tk.END, "=" * 60 + "\n\n")
        
        self.analysis_text.insert(tk.END, f"{msg}\n\n")

        if thrashing:
            self.analysis_text.insert(tk.END, "🚨 ¡ALERTA DE HIPERPAGINACIÓN! El sistema está intercambiando páginas excesivamente.\n")
            self.analysis_text.insert(tk.END, "Sugerencias para mitigar:\n")
            self.analysis_text.insert(tk.END, "  - Reducir la cantidad de procesos activos concurrentemente.\n")
            self.analysis_text.insert(tk.END, "  - Incrementar la memoria física disponible (si es posible en un sistema real).\n")
            self.analysis_text.insert(tk.END, "  - Optimizar los algoritmos de acceso a datos de los procesos.\n")
            self.analysis_text.insert(tk.END, "  - Considerar un algoritmo de reemplazo de páginas más eficiente si aplica.\n")
        else:
            self.analysis_text.insert(tk.END, "✅ El sistema parece estar operando sin hiperpaginación en este momento.\n")
        
        stats = self.controller.get_statistics() # Get fresh stats
        self.analysis_text.insert(tk.END, "\nEstadísticas relevantes:\n")
        self.analysis_text.insert(tk.END, f"  Tasa de aciertos (Hit Rate): {stats.get('hit_rate', 0):.2f}%\n")
        self.analysis_text.insert(tk.END, f"  Tasa de fallos (Fault Rate): {stats.get('fault_rate', 0):.2f}%\n")
        self.analysis_text.insert(tk.END, f"  Total Swaps (In+Out): {stats.get('swaps_in', 0) + stats.get('swaps_out', 0)}\n")
        self.analysis_text.config(state=tk.DISABLED)

    def show_initial_analysis(self):
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "📊 ANÁLISIS INICIAL DEL SIMULADOR\n")
        self.analysis_text.insert(tk.END, "=" * 60 + "\n\n")
        self.analysis_text.insert(tk.END, "Este simulador permite explorar conceptos clave de la gestión de memoria:\n\n")
        self.analysis_text.insert(tk.END, "🔹 Traducción de Direcciones:\n")
        self.analysis_text.insert(tk.END, "   Observe cómo las direcciones simbólicas se transforman en físicas a través de la MMU y tablas de páginas.\n\n")
        self.analysis_text.insert(tk.END, "🔹 Paginación por Demanda:\n")
        self.analysis_text.insert(tk.END, "   Las páginas se cargan en memoria física solo cuando son necesarias (accedidas).\n\n")
        self.analysis_text.insert(tk.END, "🔹 Algoritmos de Reemplazo (FIFO/LRU):\n")
        self.analysis_text.insert(tk.END, "   Cuando la memoria está llena, se elige una página víctima para enviar a swap.\n\n")
        self.analysis_text.insert(tk.END, "🔹 Detección de Hiperpaginación (Thrashing):\n")
        self.analysis_text.insert(tk.END, "   Identifique cuándo el sistema gasta demasiado tiempo en paginación, afectando el rendimiento.\n\n")
        self.analysis_text.insert(tk.END, " Pasos Sugeridos:\n")
        self.analysis_text.insert(tk.END, "  1. Cree uno o más procesos en la pestaña 'Gestión de Procesos'.\n")
        self.analysis_text.insert(tk.END, "  2. Seleccione un proceso como activo.\n")
        self.analysis_text.insert(tk.END, "  3. Vaya a 'Traducción de Direcciones' e ingrese direcciones simbólicas (ej: 'var_X', 'data_array[10]').\n")
        self.analysis_text.insert(tk.END, "  4. Use 'Acceso Aleatorio' y 'Carga Intensiva' para observar el comportamiento del sistema.\n")
        self.analysis_text.insert(tk.END, "  5. Monitoree el 'Estado del Sistema' y las 'Estadísticas'.\n")
        self.analysis_text.insert(tk.END, "  6. Pulse 'Detectar Hiperpaginación' después de una carga intensiva.\n")
        self.analysis_text.config(state=tk.DISABLED)

    def update_displays(self):
        self.update_process_list() # Order matters: update process list first to ensure current_process is set
        self.update_memory_display()
        self.update_page_table_display()
        self.update_swap_display()
        self.update_stats_display()
        # self.check_thrashing() # Optionally update thrashing status continuously, or only on demand
