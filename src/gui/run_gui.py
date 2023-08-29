import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # ttk (themed Tkinter) for a more modern look
import random

class DataAnalysisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("M2B3 BIOPAC Data Analysis")
        self.root.geometry("400x680")  # set initial window size
        
        # Initialize attributes
        self.data_file = ""
        self.sampling_rate = 0
        self.researcher_initials = ""
        self.participant_name = ""
        self.participant_id = ""

        self.HRV = tk.BooleanVar(value=False)
        self.excel_table = tk.BooleanVar(value=False)
        self.ecg = tk.BooleanVar(value=False)
        self.rsp = tk.BooleanVar(value=False)
        self.eda = tk.BooleanVar(value=False)
        self.ppg = tk.BooleanVar(value=False)
        self.slider = tk.BooleanVar(value=False)
        self.rates_and_events = tk.BooleanVar(value=False)

        # Better fonts
        large_font = ("Verdana", 12)
        medium_font = ("Verdana", 10)
        
        # Create widgets
        self.create_widgets(large_font, medium_font)

    def create_widgets(self, large_font, medium_font):
        tk.Label(self.root, text="Data File Path:", font=large_font).pack(pady=10)
        
        self.file_entry = tk.Entry(self.root, font=medium_font)
        self.file_entry.pack(pady=5)
        
        tk.Button(self.root, text="Browse", font=medium_font, command=self.open_file).pack(pady=5)

        tk.Label(self.root, text="Sampling Rate:", font=large_font).pack(pady=10)
        
        self.rate_entry = tk.Entry(self.root, font=medium_font)
        self.rate_entry.pack(pady=5)

        tk.Label(self.root, text="Researcher Initials:", font=large_font).pack(pady=10)
        
        self.initials_entry = tk.Entry(self.root, font=medium_font)
        self.initials_entry.pack(pady=5)

        tk.Label(self.root, text="Participant Name:", font=large_font).pack(pady=10)
        
        self.name_entry = tk.Entry(self.root, font=medium_font)
        self.name_entry.pack(pady=5)
                
        tk.Checkbutton(self.root, text="HRV", variable=self.HRV).pack(pady=5)
        tk.Checkbutton(self.root, text="Excel Table", variable=self.excel_table).pack(pady=5)
        tk.Checkbutton(self.root, text="ECG", variable=self.ecg).pack(pady=5)
        tk.Checkbutton(self.root, text="RSP", variable=self.rsp).pack(pady=5)
        tk.Checkbutton(self.root, text="EDA", variable=self.eda).pack(pady=5)
        tk.Checkbutton(self.root, text="PPG", variable=self.ppg).pack(pady=5)
        tk.Checkbutton(self.root, text="Slider", variable=self.slider).pack(pady=5)
        tk.Checkbutton(self.root, text="Rates and Events", variable=self.rates_and_events).pack(pady=5)
        
        tk.Button(self.root, text="Submit", font=medium_font, command=self.validate_and_submit).pack(pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MAT files", "*.mat"), ("ACQ files", "*.acq")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def validate_and_submit(self):
        validation_pass = True

        self.data_file = self.file_entry.get()
        rate_str = self.rate_entry.get()
        self.researcher_initials = self.initials_entry.get()
        self.participant_name = self.name_entry.get()

        if not self.data_file:
            self.file_entry.config(bg='red')
            validation_pass = False
        else:
            self.file_entry.config(bg='white')

        if not rate_str:
            self.rate_entry.config(bg='red')
            validation_pass = False
        else:
            self.rate_entry.config(bg='white')
            try:
                self.sampling_rate = int(rate_str)
            except ValueError:
                messagebox.showerror("Error", "Sampling rate must be an integer")
                return
            
        if not self.researcher_initials:
            self.initials_entry.config(bg='red')
            validation_pass = False
        else:
            self.initials_entry.config(bg='white')

        if not self.participant_name:
            self.name_entry.config(bg='red')
            validation_pass = False
        else:
            self.name_entry.config(bg='white')

        if not validation_pass:
            messagebox.showwarning("Missing Info", "Please fill in the required fields highlighted in red")
        else:
            # This is where you could generate the participant ID
            self.participant_id = self.generate_participant_id(self.participant_name)
            self.root.quit()

    def submit(self):
        self.data_file = self.file_entry.get()
        self.sampling_rate = int(self.rate_entry.get())
        self.researcher_initials = self.initials_entry.get()
        self.participant_name = self.name_entry.get()
        
        # Generate the unique participant ID
        self.participant_id = self.generate_participant_id(self.participant_name)
        
        self.root.quit()

    def generate_participant_id(self, participant_name):
        # Create a unique participant ID based on the participant's name
        random_id = random.randint(1000, 9999)

        # Create a unique participant ID based on the participant's name and random ID
        participant_id = f"{participant_name[:2].upper()}{random_id}"
        
        return participant_id

    def run(self):
        self.root.mainloop()
        print("Participant name and ID:", self.participant_name, self.participant_id)
        return (
            self.data_file, 
            self.sampling_rate, 
            self.researcher_initials, 
            self.participant_name, 
            self.participant_id,
            self.HRV.get(), self.excel_table.get(), self.ecg.get(), self.rsp.get(), self.eda.get(), self.ppg.get(), self.slider.get(), self.rates_and_events.get()
        )

def main():
    gui_instance = DataAnalysisGUI()
    return gui_instance.run()
