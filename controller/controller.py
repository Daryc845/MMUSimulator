import random
import time
from model.memory import MemorySimulator, ReplacementAlgorithm, PageStatus

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
        """
        This method exists in the controller but the GUI's random_access button
        calls the GUI's own random_access method, which then calls
        controller.simulate_memory_access. This is fine.
        If this controller method were to be used directly, it would perform one random access.
        """
        if not self.simulator.current_process:
            return None # Or raise an error, or return a status
        
        process_data = self.simulator.processes.get(self.simulator.current_process)
        if not process_data: # Should not happen if current_process is valid
            return None

        if process_data['pages_needed'] == 0:
            random_address = 0
        else:
            max_address = process_data['pages_needed'] * self.simulator.page_size - 1
            random_address = random.randint(0, max_address)
        
        self.simulate_memory_access(random_address) # Calls the method below
        return random_address

    def simulate_memory_access(self, address):
        """
        This is the core method called by the GUI's simulation actions.
        It translates the virtual address and may mark a page as modified.
        """
        if not self.simulator.current_process:
            return

        physical_address = self.simulator.translate_virtual_to_physical(address)
        
        # If translation was successful (page is in memory)
        if physical_address is not None:
            # Simulate a chance to modify the page (write operation)
            if random.random() < 0.3: # 30% chance
                page_num = address // self.simulator.page_size
                current_pid = self.simulator.current_process # Should be valid here
                
                # Check if process still exists and page is in its table
                # (defensive, as translate_virtual_to_physical implies validity)
                if current_pid in self.simulator.processes:
                    process_page_table = self.simulator.processes[current_pid]['page_table']
                    if page_num in process_page_table:
                        process_page_table[page_num]['modified'] = True


    def intensive_load(self, update_callback=None):
        """
        This method in the controller can perform an intensive load.
        The GUI also has an intensive_load which calls its own random_access in a loop.
        Using the GUI's version is fine as it handles UI updates.
        """
        if not self.simulator.current_process:
            return

        num_accesses = 50 # Or make this configurable
        for i in range(num_accesses):
            
            process_data = self.simulator.processes.get(self.simulator.current_process)
            if not process_data or process_data['pages_needed'] == 0:
                continue # or break

            max_address = process_data['pages_needed'] * self.simulator.page_size - 1
            random_address = random.randint(0, max_address)
            self.simulate_memory_access(random_address) # Simulate the access

            time.sleep(0.05) # Pause between accesses
            if update_callback: # If a GUI callback is provided (e.g., to update UI)
                update_callback()

    def reset_system(self):
        self.simulator.reset_system()

    def get_statistics(self):
        return self.simulator.get_statistics()

    def detect_thrashing(self):
        return self.simulator.detect_thrashing()

    def get_processes(self):
        return self.simulator.processes # Exposes the dictionary directly

    def get_current_process(self):
        return self.simulator.current_process

    def set_current_process(self, pid): # Added for completeness, GUI uses it
        self.simulator.current_process = pid


    def get_page_size(self):
        return self.simulator.page_size

    def simulate_address_translation_stages(self, symbolic_address):
        # This method is crucial for the translation tab in the GUI
        return self.simulator.simulate_address_translation_stages(symbolic_address)

    def get_physical_memory(self):
        return self.simulator.physical_memory # Exposes the list directly

    def get_swap_space(self):
        return self.simulator.swap_space # Exposes the dictionary directly

    def get_page_table(self, pid):
        # GUI calls this, ensure it handles pid not found gracefully if necessary,
        # though GUI logic should usually provide a valid pid.
        process = self.simulator.processes.get(pid)
        if process:
            return process.get('page_table', {})
        return {} # Return empty dict if pid not found

    def get_replacement_algorithm(self):
        return self.simulator.replacement_algorithm
        
    def get_physical_pages(self): 
        return self.simulator.physical_pages
