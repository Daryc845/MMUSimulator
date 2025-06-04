from view.gui import MMUSimulatorGUI
import tkinter as tk

def main():
    """
    Punto de entrada principal de la aplicación.
    Inicializa la ventana raíz de Tkinter, crea la interfaz gráfica del simulador MMU y ejecuta el bucle principal de la GUI.
    """
    root = tk.Tk()
    app = MMUSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()