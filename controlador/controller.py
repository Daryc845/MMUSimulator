# File: /Direction_Traduction_MMU/Direction_Traduction_MMU/controlador/controller.py

import random
import time
from modelo.memory import MemorySimulator, ReplacementAlgorithm, PageStatus

__all__ = ["Controller", "ReplacementAlgorithm", "PageStatus"]

class Controller:
    def __init__(self):
        self.simulator = MemorySimulator()

    def create_process(self, pid, size_kb):
        return self.simulator.create_process(pid, size_kb)

    def set_active_process(self, pid):
        if pid in self.simulator.processes:
            self.simulator.current_process = pid

    def change_algorithm(self, algorithm):
        if algorithm == "FIFO":
            self.simulator.replacement_algorithm = ReplacementAlgorithm.FIFO
        elif algorithm == "LRU":
            self.simulator.replacement_algorithm = ReplacementAlgorithm.LRU

    def random_access(self):
        if not self.simulator.current_process:
            return None
        process_data = self.simulator.processes[self.simulator.current_process]
        max_address = process_data['pages_needed'] * self.simulator.page_size - 1
        random_address = random.randint(0, max_address)
        self.simulate_memory_access(random_address)
        return random_address

    def simulate_memory_access(self, address):
        if not self.simulator.current_process:
            return
        physical_address = self.simulator.translate_virtual_to_physical(address)
        if physical_address is not None:
            if random.random() < 0.3:
                page_num = address // self.simulator.page_size
                self.simulator.processes[self.simulator.current_process]['page_table'][page_num]['modified'] = True

    def intensive_load(self, update_callback=None):
        if not self.simulator.current_process:
            return
        for _ in range(50):
            self.random_access()
            time.sleep(0.05)
            if update_callback:
                update_callback()
    
    def translate_virtual_to_physical(self, virtual_address):
        """Función principal de la MMU para traducir direcciones"""
        if not self.simulator.current_process:
            return None

        # Extraer número de página y offset
        page_number = virtual_address // self.simulator.page_size
        offset = virtual_address % self.simulator.page_size

        process_data = self.simulator.processes[self.simulator.current_process]
        page_table = process_data['page_table']

        # Verificar si la página existe en el espacio virtual del proceso
        if page_number >= process_data['pages_needed']:
            return None

        # Verificar si la página está en memoria física
        if page_number in page_table:
            page_entry = page_table[page_number]

            if page_entry['status'] == PageStatus.VALID:
                # Page Hit
                physical_frame = page_entry['physical_frame']
                physical_address = physical_frame * self.simulator.page_size + offset
                return physical_address
            else:
                # Page Fault: podrías manejarlo aquí si lo deseas
                return None

        return None

    def reset_system(self):
        self.simulator.reset_system()

    def get_statistics(self):
        return self.simulator.get_statistics()

    def detect_thrashing(self):
        return self.simulator.detect_thrashing()

    def get_processes(self):
        return self.simulator.processes

    def get_current_process(self):
        return self.simulator.current_process

    def set_current_process(self, pid):
        self.simulator.current_process = pid

    def get_page_size(self):
        return self.simulator.page_size

    def simulate_address_translation_stages(self, symbolic_address):
        return self.simulator.simulate_address_translation_stages(symbolic_address)

    def get_physical_memory(self):
        return self.simulator.physical_memory

    def get_swap_space(self):
        return self.simulator.swap_space

    def get_page_table(self, pid):
        return self.simulator.processes[pid]['page_table']

    def get_replacement_algorithm(self):
        return self.simulator.replacement_algorithm