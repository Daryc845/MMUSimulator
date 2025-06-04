import random
import time
from model.memory import MemorySimulator, ReplacementAlgorithm, PageStatus

__all__ = ["Controller", "ReplacementAlgorithm", "PageStatus"]

class Controller:
    def __init__(self):
        """
        Inicializa el controlador y la instancia del simulador de memoria.
        """
        self.simulator = MemorySimulator()

    def create_process(self, pid, size_kb):
        """
        Crea un proceso en el simulador.
        Args:
            pid (str): Identificador del proceso.
            size_kb (int): Tamaño del proceso en KB.
        Returns:
            tuple: (bool, str) indicando éxito y mensaje.
        """
        return self.simulator.create_process(pid, size_kb)

    def set_active_process(self, pid):
        """
        Establece el proceso activo si existe.
        Args:
            pid (str): Identificador del proceso.
        """
        if pid in self.simulator.processes:
            self.simulator.current_process = pid

    def change_algorithm(self, algorithm):
        """
        Cambia el algoritmo de reemplazo de páginas.
        Args:
            algorithm (str): "FIFO" o "LRU".
        """
        if algorithm == "FIFO":
            self.simulator.replacement_algorithm = ReplacementAlgorithm.FIFO
            self.simulator.fifo_queue.clear()
            for i, frame_content in enumerate(self.simulator.physical_memory):
                if frame_content is not None:
                    pid, page_num = frame_content
                    key = (pid, page_num)
                    if key not in self.simulator.fifo_queue:
                        self.simulator.fifo_queue.append(key)
        elif algorithm == "LRU":
            self.simulator.replacement_algorithm = ReplacementAlgorithm.LRU

    def random_access(self):
        """
        Realiza un acceso aleatorio a una dirección virtual del proceso activo.
        Returns:
            int or None: Dirección virtual accedida, o None si no hay proceso activo.
        """
        if not self.simulator.current_process:
            return None
        
        process_data = self.simulator.processes.get(self.simulator.current_process)
        if not process_data:
            return None

        if process_data['pages_needed'] == 0:
            random_address = 0
        else:
            max_address = process_data['pages_needed'] * self.simulator.page_size - 1
            random_address = random.randint(0, max_address)
        
        self.simulate_memory_access(random_address)
        return random_address

    def simulate_memory_access(self, address):
        """
        Simula el acceso a una dirección virtual, gestionando page faults y posibles escrituras.
        Args:
            address (int): Dirección virtual a acceder.
        """
        if not self.simulator.current_process:
            return

        physical_address = self.simulator.translate_virtual_to_physical(address)
        if physical_address is not None:
            if random.random() < 0.3:
                page_num = address // self.simulator.page_size
                current_pid = self.simulator.current_process
                if current_pid in self.simulator.processes:
                    process_page_table = self.simulator.processes[current_pid]['page_table']
                    if page_num in process_page_table:
                        process_page_table[page_num]['modified'] = True

    def intensive_load(self, update_callback=None):
        """
        Realiza múltiples accesos aleatorios para simular carga intensiva.
        Args:
            update_callback (callable, optional): Función para actualizar la interfaz.
        """
        if not self.simulator.current_process:
            return

        num_accesses = 50
        for i in range(num_accesses):
            process_data = self.simulator.processes.get(self.simulator.current_process)
            if not process_data or process_data['pages_needed'] == 0:
                continue

            max_address = process_data['pages_needed'] * self.simulator.page_size - 1
            random_address = random.randint(0, max_address)
            self.simulate_memory_access(random_address)

            time.sleep(0.05)
            if update_callback:
                update_callback()

    def reset_system(self):
        """
        Reinicia el simulador, eliminando todos los procesos y estadísticas.
        """
        self.simulator.reset_system()

    def get_statistics(self):
        """
        Obtiene las estadísticas actuales del simulador.
        Returns:
            dict: Estadísticas del sistema.
        """
        return self.simulator.get_statistics()

    def detect_thrashing(self):
        """
        Detecta si hay hiperpaginación en el sistema.
        Returns:
            tuple: (bool, str) indicando si hay thrashing y mensaje descriptivo.
        """
        return self.simulator.detect_thrashing()

    def get_processes(self):
        """
        Obtiene el diccionario de procesos actuales.
        Returns:
            dict: Procesos activos.
        """
        return self.simulator.processes

    def get_current_process(self):
        """
        Obtiene el PID del proceso activo.
        Returns:
            str or None: PID del proceso activo.
        """
        return self.simulator.current_process

    def set_current_process(self, pid):
        """
        Establece el proceso activo.
        Args:
            pid (str): Identificador del proceso.
        """
        self.simulator.current_process = pid

    def get_page_size(self):
        """
        Obtiene el tamaño de página en bytes.
        Returns:
            int: Tamaño de página.
        """
        return self.simulator.page_size

    def simulate_address_translation_stages(self, symbolic_address):
        """
        Simula las etapas de traducción de una dirección simbólica.
        Args:
            symbolic_address (str): Dirección simbólica.
        Returns:
            tuple: (list de etapas, dirección lógica)
        """
        return self.simulator.simulate_address_translation_stages(symbolic_address)

    def get_physical_memory(self):
        """
        Obtiene la lista de marcos físicos.
        Returns:
            list: Estado de la memoria física.
        """
        return self.simulator.physical_memory

    def get_swap_space(self):
        """
        Obtiene el espacio de intercambio (swap).
        Returns:
            dict: Páginas en swap.
        """
        return self.simulator.swap_space

    def get_page_table(self, pid):
        """
        Obtiene la tabla de páginas de un proceso.
        Args:
            pid (str): Identificador del proceso.
        Returns:
            dict: Tabla de páginas del proceso.
        """
        process = self.simulator.processes.get(pid)
        if process:
            return process.get('page_table', {})
        return {}

    def get_replacement_algorithm(self):
        """
        Obtiene el algoritmo de reemplazo actual.
        Returns:
            ReplacementAlgorithm: Algoritmo de reemplazo.
        """
        return self.simulator.replacement_algorithm
        
    def get_physical_pages(self): 
        """
        Obtiene el número de marcos físicos.
        Returns:
            int: Número de marcos físicos.
        """
        return self.simulator.physical_pages
