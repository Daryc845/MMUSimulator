from vista.gui import MMUSimulatorGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = MMUSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()