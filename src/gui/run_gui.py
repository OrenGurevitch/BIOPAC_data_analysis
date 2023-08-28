import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # ttk (themed Tkinter) for a more modern look

class DataAnalysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("M2B3 BIOPAC Data Analysis")
        self.root.geometry("350x350")  # set initial window size
        
        # Better fonts
        large_font = ("Verdana", 12)
        medium_font = ("Verdana", 10)
        
        self.create_widgets(large_font, medium_font)
        
        self.data_file = ""
        self.sampling_rate = 0
        self.researcher_initials = ""
        
    def create_widgets(self, large_font, medium_font):
        tk.Label(self.root, text="Data File Path:", font=large_font).pack(pady=10)
        
        self.file_entry = tk.Entry(self.root, font=medium_font)
        self.file_entry.pack(pady=5)
        
        tk.Button(self.root, text="Browse", font=medium_font, command=self.open_file).pack(pady=5)

        tk.Label(self.root, text="Researcher Initials:", font=large_font).pack(pady=10)
        
        self.initials_entry = tk.Entry(self.root, font=medium_font)
        self.initials_entry.pack(pady=5)

        tk.Label(self.root, text="Sampling Rate:", font=large_font).pack(pady=10)
        
        self.rate_entry = tk.Entry(self.root, font=medium_font)
        self.rate_entry.pack(pady=5)

        tk.Button(self.root, text="Submit", font=medium_font, command=self.submit).pack(pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MAT files", "*.mat"), ("ACQ files", "*.acq")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def submit(self):
        self.data_file = self.file_entry.get()
        self.researcher_initials = self.initials_entry.get()
        self.sampling_rate = int(self.rate_entry.get())
        self.root.quit()

    def run(self):
        self.root.mainloop()
        return self.data_file, self.sampling_rate, self.researcher_initials
