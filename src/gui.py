import tkinter as tk
from visualization.visualize import main as visualize

def on_submit(processed_dataframes, sampling_rate, excel_path, events):
    HRV_val = HRV_checkbox.get()
    excel_table_val = excel_table_checkbox.get()
    ecg_val = ecg_checkbox.get()
    # Add additional options here...
    visualize(processed_dataframes, sampling_rate, excel_path, events, HRV_val, excel_table_val, ecg_val)
    root.quit()

def show_gui(processed_dataframes, sampling_rate, excel_path, events):
    global HRV_checkbox, excel_table_checkbox, ecg_checkbox, root
    root = tk.Tk()
    HRV_checkbox = tk.BooleanVar()
    excel_table_checkbox = tk.BooleanVar()
    ecg_checkbox = tk.BooleanVar()
    # Add additional checkboxes here...

    tk.Checkbutton(root, text="HRV", variable=HRV_checkbox).pack()
    tk.Checkbutton(root, text="Excel Table", variable=excel_table_checkbox).pack()
    tk.Checkbutton(root, text="ECG", variable=ecg_checkbox).pack()
    # Add additional checkbox widgets here...

    tk.Button(root, text="Submit", command=lambda: on_submit(processed_dataframes, sampling_rate, excel_path, events)).pack()
    root.mainloop()