import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json
import tkinter as tk
import itertools
import matplotlib.pyplot as plt

# Global variables for dataframe and saved selections
df = None
primary_selections = []
secondary_selections = []

# Function to load an Excel or CSV file
def load_file():
    filetypes = [("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
    filepath = filedialog.askopenfilename(filetypes=filetypes)
    if filepath:
        global df
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        update_listboxes()

# Function to update listboxes with column names
def update_listboxes():
    global df
    if df is not None:
        primary_listbox.delete(0, 'end')
        secondary_listbox.delete(0, 'end')
        for col in df.columns:
            primary_listbox.insert('end', col)
            secondary_listbox.insert('end', col)

# Function to save selected parameters from the primary ListBox
def save_primary_selection():
    global primary_selections
    primary_selections = [primary_listbox.get(i) for i in primary_listbox.curselection()]
    #messagebox.showinfo("Info", "parameters saved.")

# Function to save selected parameters from the secondary ListBox
def save_secondary_selection():
    global secondary_selections
    secondary_selections = [secondary_listbox.get(i) for i in secondary_listbox.curselection()]
    #messagebox.showinfo("Info", "parameters saved.")
def Clear_selection():
    global primary_selections
    global secondary_selections
    primary_selections = [primary_listbox.select_clear(i) for i in primary_listbox.curselection()]
    secondary_selections = [secondary_listbox.select_clear(i) for i in secondary_listbox.curselection()]
# Function to save the configuration to a file
def save_configuration():
    config = {
        'primary_parameters': primary_selections,
        'secondary_parameters': secondary_selections,
        'show_max': show_max_var.get(),
        'show_min': show_min_var.get(),
        'show_avg': show_avg_var.get()
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        messagebox.showinfo("Info", "saved.")
   # else:
        #messagebox.showerror("Error", "Configuration not saved.")

# Function to plot selected parameters from both ListBoxes
def plot_selected_parameters():
    if df is not None:
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx() if secondary_selections else None

        for param in primary_selections:
            if param in df.columns:
                data = df[param]
                label = param
                if show_max_var.get():
                    label += f'\nMax: {data.max():.2f}'
                if show_min_var.get():
                    label += f'\nMin: {data.min():.2f}'
                if show_avg_var.get():
                    label += f'\nAvg: {data.mean():.2f}'
                ax1.plot(data, label=label)

        if ax2:
            for param in secondary_selections:
                if param in df.columns:
                    data = df[param]
                    label = param
                    if show_max_var.get():
                        label += f'\nMax: {data.max():.2f}'
                    if show_min_var.get():
                        label += f'\nMin: {data.min():.2f}'
                    if show_avg_var.get():
                        label += f'\nAvg: {data.mean():.2f}'
                    ax2.plot(data, linestyle='--', label=label)

            ax1.set_title('Parameters Plot')
            ax1.legend(loc='center right', bbox_to_anchor=(-0.04, 0.7), prop={'size': 8})
            ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 8})
        else:
            ax1.set_title('Selected Parameters Plot')
            ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 8})

        plt.subplots_adjust(left=0.15, bottom=0.1, right=0.75, top=0.9, wspace=0.2, hspace=0.2)
        plt.show()
    else:
        messagebox.showerror("Error", "No excel file loaded.")



def plot_from_configurations():
    if df is not None:
        
        filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        if filepaths:
            num_configs = len(filepaths)
            fig, axs = plt.subplots(num_configs, 1, figsize=(8, num_configs * 5), constrained_layout=True)

            if num_configs == 1:
                axs = [axs]  # Ensure axs is always a list even for one subplot

            # Define color cycles for primary and secondary axes
            primary_colors = itertools.cycle(plt.cm.tab10.colors)  # Color cycle for primary axis
            secondary_colors = itertools.cycle(plt.cm.Set2.colors)  # Color cycle for secondary axis

            # Iterate through each configuration file
            for idx, filepath in enumerate(filepaths):
                ax = axs[idx]

                with open(filepath, 'r') as file:
                    config = json.load(file)
                    primary_params = config.get('primary_parameters', [])
                    secondary_params = config.get('secondary_parameters', [])
                    show_max = config.get('show_max', True)
                    show_min = config.get('show_min', True)
                    show_avg = config.get('show_avg', True)

                    primary_data = []
                    primary_labels = []
                    secondary_data = []
                    secondary_labels = []

                    # Process primary parameters
                    for param in primary_params:
                        if param in df.columns:
                            data = df[param]
                            label = param
                            if show_max:
                                label += f'\nMax: {data.max():.2f}'
                            if show_min:
                                label += f'\nMin: {data.min():.2f}'
                            if show_avg:
                                label += f'\nAvg: {data.mean():.2f}'
                            primary_labels.append(label)
                            primary_data.append(data)

                    # Process secondary parameters
                    for param in secondary_params:
                        if param in df.columns:
                            data = df[param]
                            label = param
                            if show_max:
                                label += f'\nMax: {data.max():.2f}'
                            if show_min:
                                label += f'\nMin: {data.min():.2f}'
                            if show_avg:
                                label += f'\nAvg: {data.mean():.2f}'
                            secondary_labels.append(label)
                            secondary_data.append(data)

                    # Plot the primary parameters on ax
                    if primary_data:
                        for data, label in zip(primary_data, primary_labels):
                            color = next(primary_colors)  # Get the next color for primary axis
                            ax.plot(data, label=label, color=color)
                    else:
                        messagebox.showerror("Error", f"No valid primary data found in {filepath}")

                    # Create and plot on secondary axis if secondary parameters exist
                    if secondary_data:
                        ax2 = ax.twinx()  # Always create twin axis if secondary data exists
                        for data, label in zip(secondary_data, secondary_labels):
                            color = next(secondary_colors)  # Get the next color for secondary axis
                            ax2.plot(data, linestyle='--', label=label, color=color)

                        # Add legends for both axes
                        ax.legend(loc='center right', bbox_to_anchor=(-0.04, 0.7), prop={'size': 8})
                        ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 8})
                    else:
                        ax.legend(loc='center right', bbox_to_anchor=(-0.04, 0.7), prop={'size': 8})

                    # Set the title for each subplot
                    ax.set_title(f'{os.path.splitext(os.path.basename(filepath))[0]}', fontsize=10)

            # Adjust the layout to prevent overlap
            plt.tight_layout()
            plt.show()

        else:
            messagebox.showerror("Error", "No configuration files selected.")
    else:
        messagebox.showerror("Error", "No file loaded.")





# Create the Tkinter window
root = tk.Tk()
root.title('Data Plotter')

# Set the window size
root.geometry('400x800')

# Create a smaller font object
small_font = font.Font(size=10,weight="bold")

# Define the variables to track checkbox states
show_max_var = tk.BooleanVar(value=True)
show_min_var = tk.BooleanVar(value=True)
show_avg_var = tk.BooleanVar(value=True)

# Create checkboxes and link them to the variables
show_max_checkbox = tk.Checkbutton(root, text=" Max", variable=show_max_var, font=small_font)
show_min_checkbox = tk.Checkbutton(root, text=" Min", variable=show_min_var, font=small_font)
show_avg_checkbox = tk.Checkbutton(root, text=" Avg", variable=show_avg_var, font=small_font)

# Add buttons with smaller dimensions
load_button = Button(root, text="Load File",command=load_file, width=15, height=1, font=small_font, bg='lightblue')
load_button.pack(pady=5)

primary_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, bg='white')
primary_listbox.pack(expand=True, fill='both', pady=5)

#primary_label = tk.Label(root, text=" Axis 1 ", font=small_font)
#primary_label.pack()

save_primary_button = Button(root, text="Save Axis 1 ", command=save_primary_selection, width=20, height=1, font=small_font, bg='orange')
save_primary_button.pack(pady=5)

secondary_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=10, bg='white')
secondary_listbox.pack(expand=True, fill='both', pady=5)

#secondary_label = tk.Label(root, text=" Axis 2", font=small_font)
#secondary_label.pack()



save_secondary_button = Button(root, text="Save Axis 2", command=save_secondary_selection, width=20, height=1, font=small_font, bg='orange')
save_secondary_button.pack(pady=5 )

Clear_selection_button = Button(root,text="Clear saved axis", command=Clear_selection,width=20, height=1, font=small_font, bg='red')
Clear_selection_button.pack(pady=5)

plot_button = Button(root, text="Plot parameter", command=plot_selected_parameters, width=20, height=1, font=small_font, bg='lightblue')
plot_button.pack(pady=5)

save_config_button = Button(root, text="Save Configuration", command=save_configuration, width=20, height=1, font=small_font, bg='lightblue')
save_config_button.pack(pady=5)



plot_config_button = Button(root, text="Load saved plot", command=plot_from_configurations, width=20, height=1, font=small_font, bg='lightblue')
plot_config_button.pack(pady=5)

show_max_checkbox.pack()
show_min_checkbox.pack()
show_avg_checkbox.pack()

# Run the Tkinter event loop
root.mainloop()