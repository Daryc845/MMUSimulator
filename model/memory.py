from enum import Enum
from collections import deque, OrderedDict
import time

class PageStatus(Enum):
    VALID = "Válida"
    INVALID = "Inválida"
    SWAPPED = "En Swap"

class ReplacementAlgorithm(Enum):
    FIFO = "FIFO"
    LRU = "LRU"

class MemorySimulator:
    def __init__(self):
        self.page_size = 4096
        self.physical_pages = 16 # Número de marcos físicos disponibles
        self.virtual_pages = 64  # Número máximo de páginas virtuales por proceso
        self.physical_memory = [None] * self.physical_pages # Representa los marcos físicos
        self.processes = {} # Diccionario de procesos: PID -> {size_kb, pages_needed, page_table, base_address}
        self.current_process = None
        
        # Estadísticas
        self.page_faults = 0
        self.page_hits = 0
        self.swaps_in = 0
        self.swaps_out = 0
        self.access_count = 0
        
        # Algoritmos de reemplazo
        self.replacement_algorithm = ReplacementAlgorithm.FIFO
        self.fifo_queue = deque() # Cola para FIFO: (pid, page_num)
        self.lru_usage = OrderedDict() # OrderedDict para LRU: (pid, page_num) -> last_access_time
        
        self.swap_space = {} # Espacio de intercambio: (pid_page_num_key) -> data
        self.recent_faults = deque(maxlen=10) # Para detección de thrashing

    def create_process(self, pid, size_kb):
        pages_needed = (size_kb * 1024 + self.page_size - 1) // self.page_size
        
        if pid in self.processes:
            return False, f"El PID '{pid}' ya existe."

        if pages_needed > self.virtual_pages:
            return False, f"Proceso {pid} requiere {pages_needed} páginas, máximo {self.virtual_pages} permitido."
        
        if pages_needed == 0: # Ensure at least one page if size_kb > 0, though GUI enforces size_kb > 0
             return False, f"Proceso {pid} con tamaño {size_kb}KB resulta en 0 páginas, lo cual no es práctico."


        page_table = {}
        for i in range(pages_needed):
            page_table[i] = {
                'physical_frame': None,
                'status': PageStatus.INVALID,
                'referenced': False,
                'modified': False,
                'access_time': 0
            }
        
        self.processes[pid] = {
            'size_kb': size_kb,
            'pages_needed': pages_needed,
            'page_table': page_table,
            'base_address': 0
        }
        
        if not self.current_process:
            self.current_process = pid

        return True, f"Proceso {pid} creado - Tamaño: {size_kb}KB, Páginas: {pages_needed}"

    def simulate_address_translation_stages(self, symbolic_address):
        stages = []
        stages.append(f"1. Dirección Simbólica: {symbolic_address}")

        logical_address_raw = abs(hash(symbolic_address)) % (self.virtual_pages * self.page_size)
        
        current_pid = self.current_process

        if not current_pid or current_pid not in self.processes:
            stages.append(f"2. Dirección Relativa (Simulada desde simbólica): 0x{logical_address_raw:08X}")
            stages.append(f"3. Dirección Lógica/Virtual (Potencial): 0x{logical_address_raw:08X}")
            stages.append("4. Dirección Física (MMU): ❌ Error: No hay proceso activo o el proceso no existe.")
            return stages, None 

        process_data = self.processes[current_pid]
        
        if process_data['pages_needed'] == 0:
            # This case should ideally not be hit if create_process ensures pages_needed > 0
            logical_address = 0 
            stages.append(f"2. Dirección Relativa (Simulada): 0x{logical_address:08X}")
            stages.append(f"3. Dirección Lógica/Virtual: 0x{logical_address:08X}")
            stages.append(f"4. Dirección Física (MMU): ❌ Error: Proceso {current_pid} no tiene páginas asignadas.")
            return stages, logical_address
        
        logical_address = logical_address_raw % (process_data['pages_needed'] * self.page_size)

        stages.append(f"2. Dirección Relativa (Simulada): 0x{logical_address:08X}")
        stages.append(f"3. Dirección Lógica/Virtual: 0x{logical_address:08X}")

        page_number = logical_address // self.page_size
        
        if page_number >= process_data['pages_needed']:
            stages.append(f"4. Dirección Física (MMU): ❌ Error de Segmentación: Dirección lógica 0x{logical_address:08X} (página {page_number}) está fuera de los límites del proceso {current_pid} (tiene {process_data['pages_needed']} páginas).")
            return stages, logical_address

        page_table = process_data['page_table']
        initial_page_status = page_table[page_number]['status']
        
        physical_address = self.translate_virtual_to_physical(logical_address)

        if physical_address is not None:
            stages.append(f"4. Dirección Física (MMU): 0x{physical_address:08X}")
            current_page_entry = page_table[page_number] 
            if initial_page_status == PageStatus.VALID: # It was a hit
                stages.append("✅ Traducción exitosa (Page Hit). La página ya estaba en memoria.")
            else: # It was a fault (INVALID or SWAPPED) but now it's VALID
                stages.append(f"✅ Traducción exitosa (Page Fault resuelto). Página {page_number} cargada/traída de swap al marco {current_page_entry['physical_frame']}.")
        else:
            # physical_address is None. Translation failed.
            stages.append(f"4. Dirección Física (MMU): ❌ Page Fault Irresoluble. No se pudo cargar la página {page_number} del proceso {current_pid} en memoria física.")
            
        return stages, logical_address

    def translate_virtual_to_physical(self, virtual_address):
        if not self.current_process or self.current_process not in self.processes:
            print(f"DEBUG: No hay proceso activo o el proceso '{self.current_process}' no existe.")
            return None

        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        process_data = self.processes[self.current_process]
        page_table = process_data['page_table']

        if page_number >= process_data['pages_needed']:
            print(f"DEBUG: Acceso fuera de los límites del proceso {self.current_process}. Página {page_number} >= Páginas requeridas {process_data['pages_needed']}")
            # Increment fault counter for segmentation fault type errors if desired
            # self.page_faults += 1 
            return None 

        self.access_count += 1
        current_time = time.time() 

        if page_number in page_table:
            page_entry = page_table[page_number]

            if page_entry['status'] == PageStatus.VALID:
                self.page_hits += 1
                physical_frame = page_entry['physical_frame']
                
                page_entry['access_time'] = self.access_count 
                page_entry['referenced'] = True
                
                key = (self.current_process, page_number)
                if key in self.lru_usage: 
                    del self.lru_usage[key]
                self.lru_usage[key] = self.access_count 

                # print(f"DEBUG: Page Hit para P{self.current_process}, Página {page_number} en Marco {physical_frame}")
                return physical_frame * self.page_size + offset
            else:
                self.page_faults += 1
                self.recent_faults.append(current_time) 
                # print(f"DEBUG: Page Fault para P{self.current_process}, Página {page_number}. Intentando cargar...")

                if self.load_page_on_demand(page_number):
                    if page_table[page_number]['status'] == PageStatus.VALID:
                        physical_frame = page_table[page_number]['physical_frame']
                        # print(f"DEBUG: Carga exitosa. P{self.current_process}, Página {page_number} cargada en Marco {physical_frame}")
                        return physical_frame * self.page_size + offset
                    else:
                        print(f"DEBUG: load_page_on_demand retornó True, pero la página no es VÁLIDA. Estado: {page_table[page_number]['status']}. Posible error interno.")
                else:
                    print(f"DEBUG: Fallo al cargar la página {page_number} bajo demanda (load_page_on_demand retornó False).")
        else:
            print(f"DEBUG: Página {page_number} no encontrada en la tabla de páginas del proceso {self.current_process}.")
            # This case should ideally be caught by page_number >= process_data['pages_needed']
            # or indicate an incomplete page_table initialization.
            # self.page_faults += 1 
            
        return None

    def load_page_on_demand(self, page_number):
        if not self.current_process:
            return False
        
        process_data = self.processes[self.current_process]
        page_table = process_data['page_table']

        free_frame = self.find_free_frame()

        if free_frame is None:
            # print(f"DEBUG: No hay marcos libres. Aplicando algoritmo de reemplazo: {self.replacement_algorithm.value}")
            free_frame = self.replace_page()

        if free_frame is not None:
            swap_key = f"{self.current_process}_{page_number}"
            if swap_key in self.swap_space:
                del self.swap_space[swap_key]
                self.swaps_in += 1
                # print(f"DEBUG: Swap In para P{self.current_process}, Página {page_number}")
            
            page_table[page_number]['physical_frame'] = free_frame
            page_table[page_number]['status'] = PageStatus.VALID
            page_table[page_number]['access_time'] = self.access_count 
            page_table[page_number]['referenced'] = True 

            self.physical_memory[free_frame] = (self.current_process, page_number) 
            
            key = (self.current_process, page_number)
            if self.replacement_algorithm == ReplacementAlgorithm.FIFO:
                if key not in self.fifo_queue: 
                    self.fifo_queue.append(key)
            elif self.replacement_algorithm == ReplacementAlgorithm.LRU:
                if key in self.lru_usage: 
                    del self.lru_usage[key]
                self.lru_usage[key] = self.access_count 

            return True
        # print(f"DEBUG: Fallo grave: No se pudo encontrar/reemplazar un marco para la página {page_number}.")
        return False

    def find_free_frame(self):
        for i, frame in enumerate(self.physical_memory):
            if frame is None:
                return i
        return None

    def replace_page(self):
        if self.replacement_algorithm == ReplacementAlgorithm.FIFO:
            return self.replace_page_fifo()
        elif self.replacement_algorithm == ReplacementAlgorithm.LRU:
            return self.replace_page_lru()
        return None 

    def replace_page_fifo(self):
        if not self.fifo_queue:
            # print("DEBUG: FIFO queue está vacía, no hay página para reemplazar.")
            return None 
        
        victim_process_pid, victim_page_num = self.fifo_queue.popleft() # Get the victim
        
        # Find the frame this victim page occupies
        victim_frame = None
        for i, frame_content in enumerate(self.physical_memory):
            if frame_content == (victim_process_pid, victim_page_num):
                victim_frame = i
                break
        
        if victim_frame is not None:
            # Ensure the process and page still exist, especially if reset_system was called or process deleted.
            if victim_process_pid in self.processes and \
               victim_page_num in self.processes[victim_process_pid]['page_table']:
                self.move_page_to_swap(victim_process_pid, victim_page_num, victim_frame)
                # print(f"DEBUG: FIFO: Reemplazando P{victim_process_pid}, Página {victim_page_num} del Marco {victim_frame}")
            else:
                # Process or page no longer exists, but frame was occupied by it. Just free the frame.
                self.physical_memory[victim_frame] = None
                # print(f"DEBUG: FIFO: Contenido del marco {victim_frame} ({victim_process_pid}, {victim_page_num}) ya no es válido o proceso no existe. Marco liberado.")
            return victim_frame
        else:
            # print(f"DEBUG: FIFO: La página a reemplazar ({victim_process_pid}, {victim_page_num}) de la cola no se encontró en la memoria física. Puede ser una inconsistencia o la página ya fue swappeada/eliminada.")
            # Try to pop next if queue not empty, or indicate failure
            if self.fifo_queue: # If there are other items, maybe try the next one (could lead to loop if all are inconsistent)
                 # For simplicity, we just fail this attempt. A more robust system might retry or clean the queue.
                 pass
            return None 

    def replace_page_lru(self):
        if not self.lru_usage:
            # print("DEBUG: LRU usage está vacío, no hay página para reemplazar.")
            return None
        
        try:
            # victim_key = min(self.lru_usage, key=self.lru_usage.get) # Simpler way to get key with min value
            victim_key = min(self.lru_usage.keys(), key=lambda k: self.lru_usage[k])

        except ValueError: # lru_usage might be empty if concurrently modified (should not happen in single thread)
             # print("DEBUG: LRU: lru_usage se vació inesperadamente.")
             return None

        victim_process_pid, victim_page_num = victim_key
        
        victim_frame = None
        for i, frame_content in enumerate(self.physical_memory):
            if frame_content == (victim_process_pid, victim_page_num):
                victim_frame = i
                break
        
        if victim_frame is not None:
            # Remove from LRU tracking *before* moving to swap to avoid re-adding if access happens during swap
            del self.lru_usage[victim_key]

            if victim_process_pid in self.processes and \
               victim_page_num in self.processes[victim_process_pid]['page_table']:
                self.move_page_to_swap(victim_process_pid, victim_page_num, victim_frame)
                # print(f"DEBUG: LRU: Reemplazando P{victim_process_pid}, Página {victim_page_num} del Marco {victim_frame}")
            else:
                self.physical_memory[victim_frame] = None
                # print(f"DEBUG: LRU: Contenido del marco {victim_frame} ({victim_process_pid}, {victim_page_num}) ya no es válido o proceso no existe. Marco liberado.")
            return victim_frame
        else:
            # print(f"DEBUG: LRU: La página a reemplazar ({victim_process_pid}, {victim_page_num}) de lru_usage no se encontró en la memoria física. Eliminando de LRU y fallando reemplazo.")
            if victim_key in self.lru_usage: # If somehow it's still there
                del self.lru_usage[victim_key]
            return None

    def move_page_to_swap(self, process_pid, page_number, frame_number):
        if process_pid in self.processes:
            page_table = self.processes[process_pid]['page_table']
            if page_number in page_table:
                # Check if page is modified
                # if page_table[page_number]['modified']:
                #    print(f"DEBUG: Página {page_number} (Proc {process_pid}) está modificada. Escribiendo a swap...")
                #    page_table[page_number]['modified'] = False # Reset dirty bit after writing to swap

                page_table[page_number]['status'] = PageStatus.SWAPPED
                page_table[page_number]['physical_frame'] = None 
                page_table[page_number]['referenced'] = False # Typically reset when swapped out
        
        swap_key = f"{process_pid}_{page_number}"
        self.swap_space[swap_key] = f"Datos de página {page_number} del proceso {process_pid}" 
        self.physical_memory[frame_number] = None 
        self.swaps_out += 1
        # print(f"DEBUG: Movida P{process_pid}, Página {page_number} del Marco {frame_number} a Swap.")

    def detect_thrashing(self):
        if len(self.recent_faults) < 5: 
            return False, "Insuficientes datos de fallos recientes para detectar hiperpaginación."
        
        current_time = time.time()
        recent_faults_in_window = [f for f in self.recent_faults if current_time - f < 5.0]
        
        # Define thrashing if more than, say, 3 faults in the last 5 seconds AND overall fault rate is high
        if len(recent_faults_in_window) >= 3: 
            # Fault rate calculation should be based on accesses in that window, or overall as a proxy
            fault_rate = self.page_faults / max(self.access_count, 1) # Overall fault rate
            # Threshold for "high" fault rate, e.g., 50%
            if fault_rate > 0.5: # Adjusted threshold
                return True, f"¡HIPERPAGINACIÓN DETECTADA! Tasa de fallos: {fault_rate:.2%}. {len(recent_faults_in_window)} fallos en los últimos 5s."
        
        fault_rate_display = self.page_faults / max(self.access_count, 1)
        return False, f"Sistema funcionando normalmente. Tasa de fallos: {fault_rate_display:.2%} (no se detecta hiperpaginación)."


    def get_statistics(self):
        stats = {
            'access_count': self.access_count,
            'page_hits': self.page_hits,
            'page_faults': self.page_faults,
            'swaps_in': self.swaps_in,
            'swaps_out': self.swaps_out,
            'pages_in_swap': len(self.swap_space),
            'algorithm': self.replacement_algorithm.value
        }
        if self.access_count > 0:
            stats['hit_rate'] = (self.page_hits / self.access_count) * 100
            stats['fault_rate'] = (self.page_faults / self.access_count) * 100
        else:
            stats['hit_rate'] = 0
            stats['fault_rate'] = 0
        return stats

    def reset_system(self):
        self.physical_memory = [None] * self.physical_pages
        self.processes = {}
        self.current_process = None
        self.page_faults = 0
        self.page_hits = 0
        self.swaps_in = 0
        self.swaps_out = 0
        self.access_count = 0
        self.fifo_queue.clear()
        self.lru_usage.clear()
        self.swap_space.clear()
        self.recent_faults.clear()

    def get_processes(self):
        return self.processes

    def get_current_process(self):
        return self.current_process

    def get_page_size(self):
        return self.page_size

    def get_physical_memory(self):
        return self.physical_memory
        
    def get_page_table(self, pid):
        return self.processes.get(pid, {}).get('page_table', {})

    def get_swap_space(self):
        return self.swap_space
        
    def get_physical_pages(self): 
        return self.physical_pages