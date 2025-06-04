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
        """
        Inicializa el simulador de memoria, estructuras de datos y estadísticas.
        """
        self.page_size = 4096
        self.physical_pages = 10
        self.virtual_pages = 64
        self.physical_memory = [None] * self.physical_pages
        self.processes = {}
        self.current_process = None
        self.page_faults = 0
        self.page_hits = 0
        self.swaps_in = 0
        self.swaps_out = 0
        self.access_count = 0
        self.replacement_algorithm = ReplacementAlgorithm.FIFO
        self.fifo_queue = deque()
        self.lru_usage = OrderedDict()
        self.swap_space = {}
        self.recent_faults = deque(maxlen=10)

    def create_process(self, pid, size_kb):
        """
        Crea un nuevo proceso con su tabla de páginas.
        Args:
            pid (str): Identificador del proceso.
            size_kb (int): Tamaño del proceso en KB.
        Returns:
            tuple: (bool, str) indicando éxito y mensaje.
        """
        pages_needed = (size_kb * 1024 + self.page_size - 1) // self.page_size
        if pid in self.processes:
            return False, f"El PID '{pid}' ya existe."
        if pages_needed > self.virtual_pages:
            return False, f"Proceso {pid} requiere {pages_needed} páginas, máximo {self.virtual_pages} permitido."
        if pages_needed == 0:
            return False, f"Proceso {pid} con tamaño {size_kb}KB resulta en 0 páginas, lo cual no es práctico."
        page_table = {}
        for i in range(pages_needed):
            page_table[i] = {
                'physical_frame': None,
                'status': PageStatus.INVALID,
                'referenced': False,
                'modified': False,
                'access_time': 0,
                'access_count': 0
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
        """
        Simula las etapas de traducción de una dirección simbólica.
        Args:
            symbolic_address (str): Dirección simbólica.
        Returns:
            tuple: (list de etapas, dirección lógica)
        """
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
            if initial_page_status == PageStatus.VALID:
                stages.append("✅ Traducción exitosa (Page Hit). La página ya estaba en memoria.")
            else:
                stages.append(f"✅ Traducción exitosa (Page Fault resuelto). Página {page_number} cargada/traída de swap al marco {current_page_entry['physical_frame']}.")
        else:
            stages.append(f"4. Dirección Física (MMU): ❌ Page Fault Irresoluble. No se pudo cargar la página {page_number} del proceso {current_pid} en memoria física.")
        return stages, logical_address

    def translate_virtual_to_physical(self, virtual_address):
        """
        Traduce una dirección virtual a física para el proceso activo.
        Args:
            virtual_address (int): Dirección virtual a traducir.
        Returns:
            int or None: Dirección física resultante o None si falla.
        """
        if not self.current_process or self.current_process not in self.processes:
            return None
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        process_data = self.processes[self.current_process]
        page_table = process_data['page_table']
        if page_number >= process_data['pages_needed']:
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
                page_entry['access_count'] += 1
                key = (self.current_process, page_number)
                if key in self.lru_usage:
                    del self.lru_usage[key]
                self.lru_usage[key] = self.access_count
                return physical_frame * self.page_size + offset
            else:
                self.page_faults += 1
                self.recent_faults.append(current_time)
                if self.load_page_on_demand(page_number):
                    if page_table[page_number]['status'] == PageStatus.VALID:
                        physical_frame = page_table[page_number]['physical_frame']
                        return physical_frame * self.page_size + offset
                return None
        return None

    def load_page_on_demand(self, page_number):
        """
        Carga una página en memoria física bajo demanda, usando reemplazo si es necesario.
        Args:
            page_number (int): Número de página a cargar.
        Returns:
            bool: True si la página fue cargada, False si no fue posible.
        """
        if not self.current_process:
            return False
        process_data = self.processes[self.current_process]
        page_table = process_data['page_table']
        free_frame = self.find_free_frame()
        if free_frame is None:
            free_frame = self.replace_page()
        if free_frame is not None:
            swap_key = f"{self.current_process}_{page_number}"
            if swap_key in self.swap_space:
                del self.swap_space[swap_key]
                self.swaps_in += 1
            page_table[page_number]['physical_frame'] = free_frame
            page_table[page_number]['status'] = PageStatus.VALID
            page_table[page_number]['access_time'] = self.access_count
            page_table[page_number]['referenced'] = True
            page_table[page_number]['access_count'] += 1
            self.physical_memory[free_frame] = (self.current_process, page_number)
            key = (self.current_process, page_number)
            if key not in self.fifo_queue:
                self.fifo_queue.append(key)
            if self.replacement_algorithm == ReplacementAlgorithm.LRU:
                if key in self.lru_usage:
                    del self.lru_usage[key]
                self.lru_usage[key] = self.access_count
            return True
        return False

    def find_free_frame(self):
        """
        Busca un marco libre en la memoria física.
        Returns:
            int or None: Índice del marco libre o None si no hay.
        """
        for i, frame in enumerate(self.physical_memory):
            if frame is None:
                return i
        return None

    def replace_page(self):
        """
        Ejecuta el algoritmo de reemplazo de página configurado.
        Returns:
            int or None: Índice del marco liberado o None si falla.
        """
        if self.replacement_algorithm == ReplacementAlgorithm.FIFO:
            return self.replace_page_fifo()
        elif self.replacement_algorithm == ReplacementAlgorithm.LRU:
            return self.replace_page_lru()
        return None

    def replace_page_fifo(self):
        """
        Reemplaza una página usando el algoritmo FIFO.
        Returns:
            int or None: Índice del marco liberado o None si falla.
        """
        if not self.fifo_queue:
            return None
        victim_process_pid, victim_page_num = self.fifo_queue.popleft()
        victim_frame = None
        for i, frame_content in enumerate(self.physical_memory):
            if frame_content == (victim_process_pid, victim_page_num):
                victim_frame = i
                break
        if victim_frame is not None:
            if victim_process_pid in self.processes and victim_page_num in self.processes[victim_process_pid]['page_table']:
                self.move_page_to_swap(victim_process_pid, victim_page_num, victim_frame)
            else:
                self.physical_memory[victim_frame] = None
            return victim_frame
        else:
            if self.fifo_queue:
                pass
            return None

    def replace_page_lru(self):
        """
        Reemplaza una página usando el algoritmo LRU (menos accesada).
        Returns:
            int or None: Índice del marco liberado o None si falla.
        """
        candidates = []
        for i, frame_content in enumerate(self.physical_memory):
            if frame_content is not None:
                pid, page_num = frame_content
                page_table = self.processes[pid]['page_table']
                access_count = page_table[page_num].get('access_count', 0)
                candidates.append((access_count, i, pid, page_num))
        if not candidates:
            return None
        candidates.sort()
        _, victim_frame, victim_pid, victim_page_num = candidates[0]
        if victim_pid in self.processes and victim_page_num in self.processes[victim_pid]['page_table']:
            self.move_page_to_swap(victim_pid, victim_page_num, victim_frame)
        else:
            self.physical_memory[victim_frame] = None
        return victim_frame

    def move_page_to_swap(self, process_pid, page_number, frame_number):
        """
        Mueve una página de un proceso a swap y libera el marco físico.
        Args:
            process_pid (str): PID del proceso.
            page_number (int): Número de página.
            frame_number (int): Índice del marco físico.
        """
        if process_pid in self.processes:
            page_table = self.processes[process_pid]['page_table']
            if page_number in page_table:
                page_table[page_number]['status'] = PageStatus.SWAPPED
                page_table[page_number]['physical_frame'] = None
                page_table[page_number]['referenced'] = False
        swap_key = f"{process_pid}_{page_number}"
        self.swap_space[swap_key] = f"Datos de página {page_number} del proceso {process_pid}"
        self.physical_memory[frame_number] = None
        self.swaps_out += 1
        key = (process_pid, page_number)
        if key in self.fifo_queue:
            self.fifo_queue.remove(key)

    def detect_thrashing(self):
        """
        Detecta si hay hiperpaginación (thrashing) en el sistema.
        Returns:
            tuple: (bool, str) indicando si hay thrashing y mensaje descriptivo.
        """
        if len(self.recent_faults) < 5:
            return False, "Insuficientes datos de fallos recientes para detectar hiperpaginación."
        current_time = time.time()
        recent_faults_in_window = [f for f in self.recent_faults if current_time - f < 5.0]
        if len(recent_faults_in_window) >= 3:
            fault_rate = self.page_faults / max(self.access_count, 1)
            if fault_rate > 0.5:
                return True, f"¡HIPERPAGINACIÓN DETECTADA! Tasa de fallos: {fault_rate:.2%}. {len(recent_faults_in_window)} fallos en los últimos 5s."
        fault_rate_display = self.page_faults / max(self.access_count, 1)
        return False, f"Sistema funcionando normalmente. Tasa de fallos: {fault_rate_display:.2%} (no se detecta hiperpaginación)."

    def get_statistics(self):
        """
        Obtiene estadísticas actuales del simulador.
        Returns:
            dict: Estadísticas del sistema.
        """
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
        """
        Reinicia el simulador, eliminando procesos, memoria y estadísticas.
        """
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
        """
        Obtiene el diccionario de procesos actuales.
        Returns:
            dict: Procesos activos.
        """
        return self.processes

    def get_current_process(self):
        """
        Obtiene el PID del proceso activo.
        Returns:
            str or None: PID del proceso activo.
        """
        return self.current_process

    def get_page_size(self):
        """
        Obtiene el tamaño de página en bytes.
        Returns:
            int: Tamaño de página.
        """
        return self.page_size

    def get_physical_memory(self):
        """
        Obtiene la lista de marcos físicos.
        Returns:
            list: Estado de la memoria física.
        """
        return self.physical_memory

    def get_page_table(self, pid):
        """
        Obtiene la tabla de páginas de un proceso.
        Args:
            pid (str): Identificador del proceso.
        Returns:
            dict: Tabla de páginas del proceso.
        """
        return self.processes.get(pid, {}).get('page_table', {})

    def get_swap_space(self):
        """
        Obtiene el espacio de intercambio (swap).
        Returns:
            dict: Páginas en swap.
        """
        return self.swap_space

    def get_physical_pages(self):
        """
        Obtiene el número de marcos físicos.
        Returns:
            int: Número de marcos físicos.
        """
        return self.physical_pages