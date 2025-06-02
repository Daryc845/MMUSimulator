import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from controlador.controller import Controller, ReplacementAlgorithm
import random
import time

class MMUSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador MMU y Gestión de Memoria Virtual")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

        # Usar el controlador
        self.controller = Controller()

        self.setup_styles()
        self.create_widgets()
        self.update_displays()

    def setup_styles(self):
        """Configurar estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
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
        """Crear todos los widgets de la interfaz"""
        # Título principal
        title_label = ttk.Label(self.root, 
                               text="🖥️ Simulador MMU y Gestión de Memoria Virtual",
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Frame principal con pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pestaña 1: Traducción de Direcciones
        self.create_address_translation_tab(notebook)
        
        # Pestaña 2: Gestión de Procesos
        self.create_process_management_tab(notebook)
        
        # Pestaña 3: Estado del Sistema
        self.create_load_simulation_tab(notebook)
        
        # Pestaña 4: Análisis y Estadísticas
        self.create_analysis_tab(notebook)
    
    def create_address_translation_tab(self, parent):
        """Crear pestaña de traducción de direcciones"""
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="🔄 Traducción de Direcciones")
        
        # Frame superior: entrada de datos
        input_frame = ttk.LabelFrame(frame, text="Entrada de Direcciones", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Dirección simbólica
        ttk.Label(input_frame, text="Dirección Simbólica:").grid(row=0, column=0, sticky='w', padx=5)
        self.symbolic_entry = ttk.Entry(input_frame, width=30)
        self.symbolic_entry.grid(row=0, column=1, padx=5)
        self.symbolic_entry.insert(0, "main_function_start")
        
        # Botón de traducción
        translate_btn = ttk.Button(input_frame, text="🔍 Traducir Dirección",
                                  command=self.translate_address)
        translate_btn.grid(row=0, column=2, padx=10)
        
        # Frame para mostrar etapas de traducción
        translation_frame = ttk.LabelFrame(frame, text="Etapas de Traducción", padding=10)
        translation_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.translation_text = scrolledtext.ScrolledText(translation_frame, 
                                                         height=15, 
                                                         font=('Courier', 10),
                                                         bg='#ecf0f1',
                                                         fg='#2c3e50')
        self.translation_text.pack(fill='both', expand=True)
    
    def create_process_management_tab(self, parent):
        """Crear pestaña de gestión de procesos"""
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="⚙️ Gestión de Procesos")
        
        # Frame superior: creación de procesos
        process_frame = ttk.LabelFrame(frame, text="Crear Proceso", padding=10)
        process_frame.pack(fill='x', padx=10, pady=5)
        
        # PID del proceso
        ttk.Label(process_frame, text="PID:").grid(row=0, column=0, sticky='w')
        self.pid_entry = ttk.Entry(process_frame, width=10)
        self.pid_entry.grid(row=0, column=1, padx=5)
        
        # Tamaño en KB
        ttk.Label(process_frame, text="Tamaño (KB):").grid(row=0, column=2, sticky='w', padx=(20,0))
        self.size_entry = ttk.Entry(process_frame, width=10)
        self.size_entry.grid(row=0, column=3, padx=5)
        
        # Botón crear proceso
        create_btn = ttk.Button(process_frame, text="➕ Crear Proceso",
                               command=self.create_process)
        create_btn.grid(row=0, column=4, padx=10)
        
        # Botón para generar 10 procesos
        ttk.Button(process_frame, text="⚙️ Generar 10 procesos", command=self.generate_10_processes).grid(row=0, column=5, padx=10)

        # Botón para reiniciar sistema
        ttk.Button(process_frame, text="🔄 Reiniciar Sistema", command=self.reset_system).grid(row=0, column=6, padx=10)
        
        # Frame para selección de proceso activo
        active_frame = ttk.LabelFrame(frame, text="Proceso Activo", padding=10)
        active_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(active_frame, text="Proceso Activo:").grid(row=0, column=0, sticky='w')
        self.active_process_var = tk.StringVar()
        self.active_process_combo = ttk.Combobox(active_frame, 
                                               textvariable=self.active_process_var,
                                               state='readonly')
        self.active_process_combo.grid(row=0, column=1, padx=5)
        self.active_process_combo.bind('<<ComboboxSelected>>', self.set_active_process)
        
        # Algoritmo de reemplazo
        ttk.Label(active_frame, text="Algoritmo:").grid(row=0, column=2, sticky='w', padx=(20,0))
        self.algorithm_var = tk.StringVar(value="FIFO")
        algorithm_combo = ttk.Combobox(active_frame, 
                                     textvariable=self.algorithm_var,
                                     values=["FIFO", "LRU"],
                                     state='readonly')
        algorithm_combo.grid(row=0, column=3, padx=5)
        algorithm_combo.bind('<<ComboboxSelected>>', self.change_algorithm)
        

        
        # --- NUEVO: Frame horizontal para tablas ---
        tables_frame = ttk.Frame(frame)
        tables_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Frame para mostrar procesos (izquierda)
        list_frame = ttk.LabelFrame(tables_frame, text="Lista de Procesos", padding=10)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 20), pady=5)

        self.process_tree = ttk.Treeview(list_frame, 
                                       columns=('PID', 'Tamaño', 'Páginas', 'Estado'),
                                       show='headings')

        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Tamaño', text='Tamaño (KB)')
        self.process_tree.heading('Páginas', text='Páginas')
        self.process_tree.heading('Estado', text='Estado')

        self.process_tree.column('PID', width=80)
        self.process_tree.column('Tamaño', width=100)
        self.process_tree.column('Páginas', width=80)
        self.process_tree.column('Estado', width=100)

        self.process_tree.pack(fill='both', expand=True)

        # Frame para tabla de páginas (derecha)
        page_table_frame = ttk.LabelFrame(tables_frame, text="Tabla de Páginas del Proceso Seleccionado", padding=10)
        page_table_frame.pack(side='left', fill='both', expand=True, padx=(0, 0), pady=5)

        self.proc_page_table_tree = ttk.Treeview(page_table_frame,
            columns=('Página', 'Marco', 'Estado', 'Ref', 'Mod'),
            show='headings')

        for col in ['Página', 'Marco', 'Estado', 'Ref', 'Mod']:
            self.proc_page_table_tree.heading(col, text=col)
            self.proc_page_table_tree.column(col, width=80)

        self.proc_page_table_tree.pack(fill='both', expand=True)
    
    def create_load_simulation_tab(self, parent):
        """Crear pestaña de simulación de carga"""
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="⚡ Simulación de carga")

        # Frame para simulación de accesos
        access_frame = ttk.LabelFrame(frame, text="Simulación de Accesos", padding=10)
        access_frame.pack(fill='x', padx=10, pady=5)
        
        # Botones de simulación
        ttk.Button(access_frame, text="🎯 Acceso Aleatorio",
                  command=self.random_access).pack(side='left', padx=5)
        
        ttk.Button(access_frame, text="🔥 Simular Carga Intensiva",
                  command=self.intensive_load).pack(side='left', padx=5)
        
        ttk.Button(access_frame, text="🔄 Reiniciar Sistema",
                  command=self.reset_system).pack(side='left', padx=5)

        # Frame izquierdo: Tabla de páginas de todos los procesos
        left_frame = ttk.LabelFrame(frame, text="Tabla de Páginas de Todos los Procesos", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(10,5), pady=10)

        self.all_pages_tree = ttk.Treeview(left_frame,
            columns=('PID', 'Página', 'Estado', 'Marco', 'Ref', 'Mod'),
            show='headings')
        for col in ['PID', 'Página', 'Estado', 'Marco', 'Ref', 'Mod']:
            self.all_pages_tree.heading(col, text=col)
            self.all_pages_tree.column(col, width=80)
        self.all_pages_tree.pack(fill='both', expand=True)

        # Frame central: Memoria SWAP
        center_frame = ttk.LabelFrame(frame, text="Memoria SWAP", padding=10)
        center_frame.pack(side='left', fill='both', expand=True, padx=(5,5), pady=10)

        self.swap_tree = ttk.Treeview(center_frame,
            columns=('PID', 'Página'),
            show='headings')
        self.swap_tree.heading('PID', text='PID')
        self.swap_tree.heading('Página', text='Página')
        self.swap_tree.column('PID', width=80)
        self.swap_tree.column('Página', width=80)
        self.swap_tree.pack(fill='both', expand=True)

        # Frame derecho: RAM (páginas en memoria física)
        right_frame = ttk.LabelFrame(frame, text="RAM (Páginas en Memoria Física)", padding=10)
        right_frame.pack(side='left', fill='both', expand=True, padx=(5,10), pady=10)

        self.ram_tree = ttk.Treeview(right_frame,
            columns=('Marco', 'PID', 'Página'),
            show='headings')
        self.ram_tree.heading('Marco', text='Marco')
        self.ram_tree.heading('PID', text='PID')
        self.ram_tree.heading('Página', text='Página')
        self.ram_tree.column('Marco', width=80)
        self.ram_tree.column('PID', width=80)
        self.ram_tree.column('Página', width=80)
        self.ram_tree.pack(fill='both', expand=True)
    
    def create_analysis_tab(self, parent):
        """Crear pestaña de análisis y estadísticas"""
        frame = ttk.Frame(parent, style='Custom.TFrame')
        parent.add(frame, text="📊 Análisis y Estadísticas")
        
        # Frame superior: Estadísticas
        stats_frame = ttk.LabelFrame(frame, text="Estadísticas del Sistema", padding=15)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        # Grid para estadísticas
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Etiquetas de estadísticas
        self.stats_labels = {}
        stats_items = [
            ('Accesos Totales:', 'access_count'),
            ('Page Hits:', 'page_hits'),
            ('Page Faults:', 'page_faults'),
            ('Tasa de Aciertos:', 'hit_rate'),
            ('Tasa de Fallos:', 'fault_rate'),
            ('Swaps In:', 'swaps_in'),
            ('Swaps Out:', 'swaps_out'),
            ('Páginas en Swap:', 'pages_in_swap'),
            ('Algoritmo:', 'algorithm')
        ]
        
        row = 0
        col = 0
        for label_text, key in stats_items:
            ttk.Label(stats_grid, text=label_text, font=('Arial', 10, 'bold')).grid(
                row=row, column=col*2, sticky='w', padx=5, pady=2)
            
            self.stats_labels[key] = ttk.Label(stats_grid, text="0", 
                                             font=('Arial', 10))
            self.stats_labels[key].grid(row=row, column=col*2+1, sticky='w', padx=5, pady=2)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Frame para análisis de rendimiento
        analysis_frame = ttk.LabelFrame(frame, text="Análisis de Rendimiento", padding=10)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botón para detectar thrashing
        thrashing_btn = ttk.Button(analysis_frame, text="🔍 Detectar Hiperpaginación",
                                 command=self.check_thrashing)
        thrashing_btn.pack(pady=5)
        
        # Área de texto para análisis
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame,
                                                     height=15,
                                                     font=('Courier', 10),
                                                     bg='#f8f9fa',
                                                     fg='#2c3e50')
        self.analysis_text.pack(fill='both', expand=True)
        
        # Insertar análisis inicial
        self.show_initial_analysis()
    
    def translate_address(self):
        """Traducir dirección simbólica"""
        symbolic_addr = self.symbolic_entry.get().strip()
        if not symbolic_addr:
            messagebox.showwarning("Advertencia", "Ingrese una dirección simbólica")
            return

        if not self.controller.get_current_process():
            messagebox.showwarning("Advertencia", "Seleccione un proceso activo")
            return

        # Realizar traducción
        stages, logical_addr = self.controller.simulate_address_translation_stages(symbolic_addr)
        
        # Mostrar resultados
        self.translation_text.delete(1.0, tk.END)
        self.translation_text.insert(tk.END, "🔄 PROCESO DE TRADUCCIÓN DE DIRECCIONES\n")
        self.translation_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for stage in stages:
            self.translation_text.insert(tk.END, stage + "\n")
        
        # Mostrar detalles de la MMU
        page_number = logical_addr // self.controller.get_page_size()
        offset = logical_addr % self.controller.get_page_size()
        
        self.translation_text.insert(tk.END, f"\n📋 DETALLES DE LA MMU:\n")
        self.translation_text.insert(tk.END, f"Número de página: {page_number}\n")
        self.translation_text.insert(tk.END, f"Offset: {offset}\n")
        self.translation_text.insert(tk.END, f"Tamaño de página: {self.controller.get_page_size()} bytes\n")
        
        # Actualizar displays
        self.update_displays()
    
    def create_process(self):
        """Crear un nuevo proceso"""
        try:
            pid = self.pid_entry.get().strip()
            size_kb = int(self.size_entry.get().strip())
            
            if not pid:
                messagebox.showwarning("Advertencia", "Ingrese un PID válido")
                return
            
            if size_kb <= 0:
                messagebox.showwarning("Advertencia", "El tamaño debe ser mayor a 0")
                return
            
            success, message = self.controller.create_process(pid, size_kb)
            
            if success:
                messagebox.showinfo("Éxito", message)
                self.pid_entry.delete(0, tk.END)
                self.size_entry.delete(0, tk.END)
                self.update_process_list()
                self.update_proc_page_table()
                self.update_system_status_tab()
            else:
                messagebox.showerror("Error", message)
                
        except ValueError:
            messagebox.showerror("Error", "Ingrese un tamaño numérico válido")
    
    def generate_10_processes(self):
        """Generar 10 procesos con PID ascendente y tamaño aleatorio"""
        existing_pids = set(int(pid) for pid in self.controller.get_processes().keys() if str(pid).isdigit())
        next_pid = 1
        created = 0
        while created < 10:
            while next_pid in existing_pids:
                next_pid += 1
            size_kb = random.randint(1, 256)
            pid_str = str(next_pid)
            success, _ = self.controller.create_process(pid_str, size_kb)
            if success:
                created += 1
                existing_pids.add(next_pid)
            next_pid += 1
        self.update_process_list()
        self.update_proc_page_table()
        self.update_system_status_tab()

    def set_active_process(self, event=None):
        """Establecer proceso activo"""
        selected = self.active_process_var.get()
        if selected and selected in self.controller.get_processes():
            self.controller.set_current_process(selected)
            self.update_displays()
            self.update_proc_page_table()

    def change_algorithm(self, event=None):
        """Cambiar algoritmo de reemplazo"""
        algorithm = self.algorithm_var.get()
        self.controller.change_algorithm(algorithm)
        self.update_displays()

    def random_access(self):
        """Simular acceso aleatorio a memoria"""
        if not self.controller.get_current_process():
            messagebox.showwarning("Advertencia", "Seleccione un proceso activo")
            return
        
        # Generar dirección aleatoria dentro del espacio del proceso
        process_data = self.controller.get_processes()[self.controller.get_current_process()]
        max_address = process_data['pages_needed'] * self.controller.get_page_size() - 1
        random_address = random.randint(0, max_address)
        
        # Simular acceso
        self.simulate_memory_access(random_address)
        
        # Actualizar displays
        self.update_displays()
        
        # Mostrar información
        page_num = random_address // self.controller.get_page_size()
        messagebox.showinfo("Acceso Aleatorio", 
                          f"Proceso: {self.controller.get_current_process()}\n"
                          f"Dirección: 0x{random_address:08X}\n"
                          f"Página: {page_num}")

    def simulate_memory_access(self, address):
        """Simular acceso a memoria"""
        if not self.controller.get_current_process():
            return
            
        # Traducir dirección
        physical_address = self.controller.translate_virtual_to_physical(address)
        
        # Simular operación de lectura/escritura
        if physical_address is not None:
            # Simular posible modificación (30% de probabilidad)
            if random.random() < 0.3:
                page_num = address // self.controller.get_page_size()
                self.controller.get_processes()[self.controller.get_current_process()]['page_table'][page_num]['modified'] = True

    def intensive_load(self):
        """Simular carga intensiva de memoria"""
        if not self.controller.get_current_process():
            messagebox.showwarning("Advertencia", "Seleccione un proceso activo")
            return
        
        # Realizar múltiples accesos aleatorios
        for _ in range(50):
            self.random_access()
            time.sleep(0.05)  # Pequeña pausa para visualización
            self.root.update()  # Actualizar GUI
        
        # Verificar thrashing
        thrashing, msg = self.controller.detect_thrashing()
        if thrashing:
            self.analysis_text.insert(tk.END, f"\n⚠️ {msg}\n")

    def reset_system(self):
        """Reiniciar el sistema de simulación"""
        self.controller.reset_system()
        self.update_displays()
        messagebox.showinfo("Sistema Reiniciado", "Todos los procesos y estadísticas han sido reiniciados")

    def update_process_list(self):
        """Actualizar la lista de procesos en la interfaz"""
        self.process_tree.delete(*self.process_tree.get_children())
        
        # Actualizar combo de proceso activo
        processes = list(self.controller.get_processes().keys())
        self.active_process_combo['values'] = processes
        
        if processes and not self.controller.get_current_process():
            self.controller.set_current_process(processes[0])
            self.active_process_var.set(processes[0])
        
        # Llenar treeview con procesos
        for pid, data in self.controller.get_processes().items():
            status = "Activo" if pid == self.controller.get_current_process() else "Inactivo"
            self.process_tree.insert('', 'end', 
                                  values=(pid, data['size_kb'], data['pages_needed'], status))
        
        self.update_proc_page_table()

    def update_stats_display(self):
        """Actualizar visualización de estadísticas"""
        stats = self.controller.get_statistics()
        
        for key, value in stats.items():
            if key in self.stats_labels:
                if key in ['hit_rate', 'fault_rate']:
                    self.stats_labels[key].config(text=f"{value:.2f}%")
                else:
                    self.stats_labels[key].config(text=str(value))

    def update_proc_page_table(self):
        """Actualizar tabla de páginas en la pestaña de gestión de procesos"""
        self.proc_page_table_tree.delete(*self.proc_page_table_tree.get_children())
        current_process = self.controller.get_current_process()
        if not current_process:
            return
        page_table = self.controller.get_page_table(current_process)
        for page_num, entry in page_table.items():
            frame = entry['physical_frame'] if entry['physical_frame'] is not None else "-"
            ref = "✓" if entry['referenced'] else "✗"
            mod = "✓" if entry['modified'] else "✗"
            self.proc_page_table_tree.insert('', 'end', 
                values=(page_num, frame, entry['status'].value, ref, mod))

    def update_system_status_tab(self):
        """Actualizar la pestaña de estado del sistema con todas las tablas"""
        # Tabla de páginas de todos los procesos
        self.all_pages_tree.delete(*self.all_pages_tree.get_children())
        for pid, pdata in self.controller.get_processes().items():
            for page_num, entry in pdata['page_table'].items():
                frame = entry['physical_frame'] if entry['physical_frame'] is not None else "-"
                ref = "✓" if entry['referenced'] else "✗"
                mod = "✓" if entry['modified'] else "✗"
                self.all_pages_tree.insert('', 'end',
                    values=(pid, page_num, entry['status'].value, frame, ref, mod))

        # Memoria SWAP
        self.swap_tree.delete(*self.swap_tree.get_children())
        for key in self.controller.get_swap_space().keys():
            pid, page = key.split('_')
            self.swap_tree.insert('', 'end', values=(pid, page))

        # RAM (páginas en memoria física)
        self.ram_tree.delete(*self.ram_tree.get_children())
        for marco, content in enumerate(self.controller.get_physical_memory()):
            if content is not None:
                pid, page = content
                self.ram_tree.insert('', 'end', values=(marco, pid, page))

    def check_thrashing(self):
        """Verificar condición de hiperpaginación"""
        thrashing, msg = self.controller.detect_thrashing()
        
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "📈 ANÁLISIS DE RENDIMIENTO\n")
        self.analysis_text.insert(tk.END, "=" * 50 + "\n\n")
        
        if thrashing:
            self.analysis_text.insert(tk.END, f"❌ {msg}\n\n")
            self.analysis_text.insert(tk.END, "Posibles soluciones:\n")
            self.analysis_text.insert(tk.END, "- Aumentar memoria física\n")
            self.analysis_text.insert(tk.END, "- Reducir número de procesos\n")
            self.analysis_text.insert(tk.END, "- Ajustar tamaño de páginas\n")
            self.analysis_text.insert(tk.END, "- Optimizar algoritmo de reemplazo\n")
        else:
            self.analysis_text.insert(tk.END, f"✅ {msg}\n\n")
        
        # Mostrar estadísticas de rendimiento
        stats = self.controller.get_statistics()
        self.analysis_text.insert(tk.END, f"Tasa de aciertos: {stats['hit_rate']:.2f}%\n")
        self.analysis_text.insert(tk.END, f"Tasa de fallos: {stats['fault_rate']:.2f}%\n")
        self.analysis_text.insert(tk.END, f"Swaps realizados: {stats['swaps_in'] + stats['swaps_out']}\n")

    def show_initial_analysis(self):
        """Mostrar análisis inicial"""
        self.analysis_text.insert(tk.END, "📈 ANÁLISIS INICIAL\n")
        self.analysis_text.insert(tk.END, "=" * 50 + "\n\n")
        self.analysis_text.insert(tk.END, "Este simulador muestra:\n")
        self.analysis_text.insert(tk.END, "- Traducción de direcciones por la MMU\n")
        self.analysis_text.insert(tk.END, "- Paginación sobre demanda\n")
        self.analysis_text.insert(tk.END, "- Algoritmos de reemplazo (FIFO/LRU)\n")
        self.analysis_text.insert(tk.END, "- Detección de hiperpaginación\n\n")
        self.analysis_text.insert(tk.END, "Instrucciones:\n")
        self.analysis_text.insert(tk.END, "1. Cree procesos\n")
        self.analysis_text.insert(tk.END, "2. Seleccione uno como activo\n")
        self.analysis_text.insert(tk.END, "3. Realice accesos a memoria\n")

    def update_displays(self):
        """Actualizar todas las visualizaciones"""
        self.update_process_list()
        self.update_proc_page_table()
        self.update_stats_display()
        self.update_system_status_tab()