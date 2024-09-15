import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json

# Function to load an Excel file
def load_excel_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx""*.csv")])
    if filepath:
        global df
        df = pd.read_excel(filepath)
        listbox.delete(0, 'end')
        for col in df.columns:
            listbox.insert('end', col)

# Function to save the selected parameters as a configuration to a file on user's computer
def save_configuration():
    selected = listbox.curselection()
    if selected:
        # Ask the user where to save the configuration
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            config = {
                'parameters': [listbox.get(i) for i in selected]
            }
            with open(filepath, 'w') as file:
                json.dump(config, file)
            messagebox.showinfo("Success", f"Configuration saved at {filepath}")
        else:
            messagebox.showerror("Error", "No file selected for saving configuration.")
    else:
        messagebox.showerror("Error", "No parameters selected to save in the configuration.")

# Function to load multiple saved configurations from files on user's computer
def load_configuration():
    filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if filepaths:
        all_parameters = set()  # Use a set to avoid duplicates
        for filepath in filepaths:
            with open(filepath, 'r') as file:
                config = json.load(file)
                all_parameters.update(config.get('parameters', []))  # Add parameters from each file

        listbox.selection_clear(0, 'end')  # Clear any previous selections
        for param in all_parameters:
            try:
                index = listbox.get(0, 'end').index(param)
                listbox.select_set(index)
            except ValueError:
                continue

        messagebox.showinfo("Success", f"Loaded configurations from {len(filepaths)} files.")
    else:
        messagebox.showerror("Error", "No configuration files selected.")

# Function to plot selected parameters
def plot_selected_parameters():
    selected = listbox.curselection()
    if selected:
        plt.figure()
        ax = plt.gca()
        for i in selected:
            col = listbox.get(i)
            max_value = df[col].max()
            min_value = df[col].min()
            avg_value = df[col].mean()
            
            # Plot the parameter with default values in the legend
            ax.plot(df[col], label=f'{col}\nMax: {max_value:.2f}, Min: {min_value:.2f}, Avg: {avg_value:.2f}')
        
        # Set the legend on the right side of the plot with default font size 8
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})

        # Set the default layout for the plot
        plt.subplots_adjust(left=0.102, bottom=0.124, right=0.752, top=0.922, wspace=0.2, hspace=0.2)

        ax.set_xlabel('Index')
        ax.set_ylabel('Values')
        ax.set_title('Selected Parameters Plot')
        plt.show()

# Create the Tkinter window
root = Tk()
root.title('Data Plotter')

# Set the window size
root.geometry('800x600')


# Create a font object with bold style
bold_font = font.Font(weight='bold')

# Add Load Excel Button with bold text
load_button = Button(root, text="Load Excel File", command=load_excel_file, width=20, height=2, font=bold_font)
load_button.pack(pady=10)

# Add Listbox with specific width and height
listbox = Listbox(root, selectmode=MULTIPLE, width=50, height=15)
listbox.pack(expand=True, fill='both', pady=10)

# Add Save Configuration Button
save_button = Button(root, text="Save Configuration", command=save_configuration, width=20, height=2, font=bold_font)
save_button.pack(pady=10)

# Add Load Configuration Button
load_button = Button(root, text="Load Configuration", command=load_configuration, width=20, height=2, font=bold_font)
load_button.pack(pady=10)

# Add Plot Button with bold text
plot_button = Button(root, text="Generate", command=plot_selected_parameters, width=20, height=2, font=bold_font)
plot_button.pack(pady=10)

# Run the application
root.mainloop()
