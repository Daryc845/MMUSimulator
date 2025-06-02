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
        self.physical_pages = 15
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
        pages_needed = (size_kb * 1024 + self.page_size - 1) // self.page_size
        if pages_needed > self.virtual_pages:
            return False, f"Proceso {pid} requiere {pages_needed} páginas, máximo {self.virtual_pages}"
        page_table = {}
        for i in range(pages_needed):
            page_table[i] = {
                'physical_frame': None,
                'status': PageStatus.INVALID,
                'referenced': False,
                'modified': False,
                'access_time': 0,
                'access_count': 0   # <-- NUEVO: contador de accesos por página
            }
        self.processes[pid] = {
            'size_kb': size_kb,
            'pages_needed': pages_needed,
            'page_table': page_table,
            'base_address': 0
        }
        return True, f"Proceso {pid} creado - Tamaño: {size_kb}KB, Páginas: {pages_needed}"

    def simulate_address_translation_stages(self, symbolic_address):
        stages = []
        stages.append(f"1. Dirección Simbólica: {symbolic_address}")
        relative_address = abs(hash(symbolic_address)) % (self.virtual_pages * self.page_size)
        stages.append(f"2. Dirección Relativa: 0x{relative_address:08X}")
        logical_address = relative_address
        stages.append(f"3. Dirección Lógica/Virtual: 0x{logical_address:08X}")
        if self.current_process:
            physical_address = self.translate_virtual_to_physical(logical_address)
            if physical_address is not None:
                stages.append(f"4. Dirección Física (MMU): 0x{physical_address:08X}")
                stages.append("✅ Traducción exitosa")
            else:
                stages.append("4. Dirección Física (MMU): ❌ Page Fault")
        else:
            stages.append("4. Dirección Física (MMU): ❌ No hay proceso activo")
        return stages, logical_address

    def translate_virtual_to_physical(self, virtual_address):
        if not self.current_process:
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
                physical_address = physical_frame * self.page_size + offset
                page_entry['access_time'] = self.access_count  # para LRU
                page_entry['referenced'] = True
                page_entry['access_count'] += 1  # <-- INCREMENTA AQUÍ
                key = (self.current_process, page_number)
                if key in self.lru_usage:
                    del self.lru_usage[key]
                self.lru_usage[key] = self.access_count
                return physical_address
            else:
                self.page_faults += 1
                self.recent_faults.append(current_time)
                if self.load_page_on_demand(page_number):
                    if page_table[page_number]['status'] == PageStatus.VALID:
                        physical_frame = page_table[page_number]['physical_frame']
                        physical_address = physical_frame * self.page_size + offset
                        return physical_address
        return None

    def load_page_on_demand(self, page_number):
        if not self.current_process:
            return False
        process_data = self.processes[self.current_process]
        page_table = process_data['page_table']
        free_frame = self.find_free_frame()
        if free_frame is None:
            free_frame = self.replace_page()
        if free_frame is not None:
            page_table[page_number]['physical_frame'] = free_frame
            page_table[page_number]['status'] = PageStatus.VALID
            page_table[page_number]['access_time'] = self.access_count
            page_table[page_number]['referenced'] = True
            page_table[page_number]['access_count'] = page_table[page_number].get('access_count', 0) + 1  # <-- Aquí
            self.physical_memory[free_frame] = (self.current_process, page_number)
            key = (self.current_process, page_number)
            self.fifo_queue.append(key)
            self.lru_usage[key] = self.access_count
            swap_key = f"{self.current_process}_{page_number}"
            if swap_key in self.swap_space:
                del self.swap_space[swap_key]
                self.swaps_in += 1
            return True
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
            return None
        victim_process, victim_page = self.fifo_queue.popleft()
        victim_frame = None
        for i, frame_content in enumerate(self.physical_memory):
            if frame_content == (victim_process, victim_page):
                victim_frame = i
                break
        if victim_frame is not None:
            self.move_page_to_swap(victim_process, victim_page, victim_frame)
            return victim_frame
        return None

    def replace_page_lru(self):
        while self.lru_usage:
            victim_key = min(self.lru_usage.keys(), key=lambda k: self.lru_usage[k])
            victim_process, victim_page = victim_key
            victim_frame = None
            for i, frame_content in enumerate(self.physical_memory):
                if frame_content == (victim_process, victim_page):
                    victim_frame = i
                    break
            # Elimina SIEMPRE la entrada de lru_usage
            del self.lru_usage[victim_key]
            if victim_frame is not None:
                self.move_page_to_swap(victim_process, victim_page, victim_frame)
                return victim_frame
            # Si no encontró el marco, intenta con el siguiente menos usado
        return None

    def move_page_to_swap(self, process_pid, page_number, frame_number):
        if process_pid in self.processes:
            page_table = self.processes[process_pid]['page_table']
            if page_number in page_table:
                page_table[page_number]['status'] = PageStatus.SWAPPED
                page_table[page_number]['physical_frame'] = None
        swap_key = f"{process_pid}_{page_number}"
        self.swap_space[swap_key] = f"Datos de página {page_number} del proceso {process_pid}"
        self.physical_memory[frame_number] = None
        self.swaps_out += 1

    def detect_thrashing(self):
        if len(self.recent_faults) < 5:
            return False, "Insuficientes datos"
        current_time = time.time()
        recent_faults_in_window = [f for f in self.recent_faults if current_time - f < 5.0]
        if len(recent_faults_in_window) >= 5:
            fault_rate = self.page_faults / max(self.access_count, 1)
            if fault_rate > 0.8:
                return True, f"¡HIPERPAGINACIÓN DETECTADA! Tasa de fallos: {fault_rate:.2%}"
        return False, "Sistema funcionando normalmente"

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

    def reset_memory_only(self):
        self.physical_memory = [None] * self.physical_pages
        self.swap_space.clear()
        self.fifo_queue.clear()
        self.lru_usage.clear()
        self.page_faults = 0
        self.page_hits = 0
        self.swaps_in = 0
        self.swaps_out = 0
        self.access_count = 0
        self.recent_faults.clear()
        # Resetear estado de páginas pero NO eliminar procesos
        for process in self.processes.values():
            for entry in process['page_table'].values():
                entry['physical_frame'] = None
                entry['status'] = PageStatus.INVALID
                entry['referenced'] = False
                entry['modified'] = False
                entry['access_time'] = 0
                entry['access_count'] = 0