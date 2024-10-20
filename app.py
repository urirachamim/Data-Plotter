import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk,Label,Entry, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json
import tkinter as tk
import itertools

###############################################################################
# command to build exe -> pyinstaller --onefile --windowed --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=matplotlib.backends.backend_agg --hidden-import=matplotlib._pylab_helpers app.py
##############################################################################


# Global variables for dataframe and saved selections
df = None
primary_selections = []
secondary_selections = []



# Function to load an Excel or CSV file
def load_file():
    filetypes = [("All files", "*.*")]
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

import matplotlib.pyplot as plt

def convert_time_to_seconds(time_str):
    # Split the time string into parts
    parts = time_str.split(':')
    if len(parts) == 4:  # HH:MM:SS:MS format
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        milliseconds = int(parts[3])
    elif len(parts) == 3:  # HH:MM:SS format, assuming no milliseconds
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        milliseconds = 0
    else:
        raise ValueError(f"Unexpected time format: {time_str}")
    
    # Calculate total seconds
    total_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000)
    return total_seconds

# Function to plot selected parameters from both ListBoxes
def plot_selected_parameters():
    if df is not None:
        # Example time log, replace with your actual data
        time_log = df['Time']  # Assuming 'Time' is the column in your DataFrame

        # Convert time log to seconds using the defined function
        x_data = [convert_time_to_seconds(time_str) for time_str in time_log]
        
        # Determine if the log length is in seconds or minutes
        log_length_in_seconds = x_data[-1]  # Last entry to determine log length
        is_minute = log_length_in_seconds > 60  # Assuming log length > 60 seconds means it's in minutes

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx() if secondary_selections else None
        
        # Set tick parameters for primary axis
        ax1.tick_params(axis='both', which='major', labelsize=14)  # Font size for primary y-axis ticks
        ax1.tick_params(axis='x', labelsize=14)  # Font size for x-axis ticks

        if ax2:
            ax2.tick_params(axis='both', which='major', labelsize=14)  # Font size for secondary y-axis ticks

        chart_title = chart_title_entry.get() if chart_title_entry.get() else "Default Title"  # Fallback to default
        
        # Plot primary parameters
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
                ax1.plot(x_data, data, label=label)  # Use x_data for the x-axis

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
                    ax2.plot(x_data, data, linestyle='--', label=label)  # Use x_data for the x-axis

            # Add grid to both y-axes
            ax1.grid(True)
            #ax2.grid(True)  # Add grid for the secondary y-axis

            ax1.set_title(chart_title, fontsize=16)
            ax1.set_xlabel(f'Time [{"Sec" if is_minute else "Sec"}]', fontsize=14)  # Set xlabel font size
            ax1.legend(loc='center right', bbox_to_anchor=(-0.04, 0.7), prop={'size': 9})
            ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 9})
            
        else:
            ax1.grid(True)  # Add grid for the single y-axis plot
            ax1.set_title('Plot', fontsize=16)
            ax1.set_xlabel(f'Time [{"Sec" if is_minute else "Sec"}]', fontsize=14)  # Set xlabel font size
            ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 9})

        plt.subplots_adjust(left=0.15, bottom=0.1, right=0.75, top=0.9, wspace=0.2, hspace=0.2)
        plt.show()
        
    else:
        messagebox.showerror("Error", "No excel file loaded.")


def plot_from_configurations():
    if df is not None:  # Check if DataFrame is loaded
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

                    # Select x-axis parameter (default or from config)
                    x_param = config.get('x_axis', 'Time')
                    if x_param not in df.columns:
                        messagebox.showerror("Error", f"{x_param} not found in data.")
                        return
                    x_data = df[x_param].apply(convert_time_to_seconds)  # Ensure x_data is processed correctly

                    # Determine if the log length is in seconds or minutes
                    log_length_in_seconds = x_data.iloc[-1]  # Last entry to determine log length
                    is_minute = log_length_in_seconds > 60  # Assuming log length > 60 seconds means it's in minutes

                    # Process and store data for primary parameters
                    primary_data = []
                    primary_labels = []
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

                    # Plot the primary parameters on ax
                    if primary_data:
                        for data, label in zip(primary_data, primary_labels):
                            color = next(primary_colors)  # Get the next color for primary axis
                            ax.plot(x_data, data, label=label, color=color)  # Use x_data for x-axis
                    else:
                        messagebox.showerror("Error", f"No valid primary data found in {filepath}")

                    # Create and plot on secondary axis if secondary parameters exist
                    ax2 = None  # Initialize ax2
                    if secondary_params:
                        secondary_data = []
                        secondary_labels = []
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

                        ax2 = ax.twinx()  # Always create twin axis if secondary data exists
                        for data, label in zip(secondary_data, secondary_labels):
                            color = next(secondary_colors)  # Get the next color for secondary axis
                            ax2.plot(x_data, data, linestyle='--', label=label, color=color)  # Use x_data for x-axis

                        # Add grids and legends for both axes
                        ax.grid(True)
                        ax.legend(loc='center right', bbox_to_anchor=(-0.08, 0.7), prop={'size': 9})
                        ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.7), prop={'size': 9})

                        # Set y-labels fontsize
                        ax.set_ylabel('', fontsize=12)
                        ax2.set_ylabel('', fontsize=12)

                    else:
                        ax.grid(True)
                        ax.legend(loc='center right', bbox_to_anchor=(1.1, 0.7), prop={'size': 9})

                    # Set the title for each subplot
                    ax.set_title(f'{os.path.splitext(os.path.basename(filepath))[0]}', fontsize=14)

                    # Set tick parameters for both axes
                    ax.tick_params(axis='both', which='major', labelsize=14)  # Font size for primary y-axis ticks
                    ax.tick_params(axis='x', labelsize=14)  # Font size for x-axis ticks
                    if ax2:
                        ax2.tick_params(axis='both', which='major', labelsize=14)  # Font size for secondary y-axis ticks

                    # Set x-axis label
                    ax.set_xlabel(f'Time [{"Sec" if is_minute else "Sec"}]', fontsize=12)  # Set xlabel fontsize

            # Adjust the layout to prevent overlap
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "No JSON files selected.")
    else:
        messagebox.showerror("Error", "No data loaded.")








root = tk.Tk()
root.title('Data Plotter')

# Set the window size
root.geometry('400x800')



# Create a smaller font object
small_font = font.Font(size=10, weight="bold")

# Define the variables to track checkbox states
show_max_var = tk.BooleanVar(value=True)
show_min_var = tk.BooleanVar(value=True)
show_avg_var = tk.BooleanVar(value=True)

# Create checkboxes and link them to the variables
show_max_checkbox = tk.Checkbutton(root, text=" Max", variable=show_max_var, font=small_font)
show_min_checkbox = tk.Checkbutton(root, text=" Min", variable=show_min_var, font=small_font)
show_avg_checkbox = tk.Checkbutton(root, text=" Avg", variable=show_avg_var, font=small_font)

# Add buttons with smaller dimensions
load_button = Button(root, text="Load File", command=load_file, width=15, height=1, font=small_font, bg='lightblue')
load_button.pack(pady=5)

primary_frame = tk.Frame(root)
primary_frame.pack(pady=5)

# Primary Listbox and Save Button
primary_listbox = tk.Listbox(primary_frame, selectmode=tk.MULTIPLE, width=30, height=10, bg='white')
primary_listbox.pack(side=tk.RIGHT, expand=True, fill='both')

save_primary_button = Button(primary_frame, text="Save Axis 1", command=save_primary_selection, width=15, height=1, font=small_font, bg='orange')
save_primary_button.pack(side=tk.LEFT, padx=5)

# Secondary Listbox and Save Button
secondary_frame = tk.Frame(root)
secondary_frame.pack(pady=5)

# Secondary Listbox
secondary_listbox = tk.Listbox(secondary_frame, selectmode=tk.MULTIPLE, width=30, height=10, bg='white')
secondary_listbox.pack(side=tk.RIGHT, expand=True, fill='both')

save_secondary_button = Button(secondary_frame, text="Save Axis 2", command=save_secondary_selection, width=15, height=1, font=small_font, bg='orange')
save_secondary_button.pack(side=tk.LEFT, padx=5)

# Clear selection Button
clear_selection_button = Button(root, text="Clear saved axis", command=Clear_selection, width=20, height=1, font=small_font, bg='red')
clear_selection_button.pack(pady=5)

# Create and place the label and entry box for chart title
chart_title_label = Label(root, text="Enter Chart Title:")
chart_title_label.pack(pady=10)  # Adjust padding for spacing

chart_title_entry = Entry(root, width=40)  # Adjust the width as needed
chart_title_entry.pack(pady=5)

# Plot parameter Button
plot_button = Button(root, text="Create Chart", command=plot_selected_parameters, width=20, height=1, font=small_font, bg='lightgreen')
plot_button.pack(pady=5)

# Save Configuration Button
save_config_button = Button(root, text="Save Chart Config", command=save_configuration, width=20, height=1, font=small_font, bg='lightblue')
save_config_button.pack(pady=5)

# Load saved plot Button
plot_config_button = Button(root, text="Load Chart", command=plot_from_configurations, width=20, height=1, font=small_font, bg='lightblue')
plot_config_button.pack(pady=5)

# Place the checkboxes at the bottom
show_max_checkbox.pack()
show_min_checkbox.pack()
show_avg_checkbox.pack()

# Run the Tkinter event loop
root.mainloop()