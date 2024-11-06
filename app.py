import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk,Label,Entry, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json
import tkinter as tk
import itertools
from tkinter import ttk
from io import BytesIO
from PIL import Image 
import win32clipboard
import subprocess





###############################################################################
# command to build exe -> pyinstaller --onefile --windowed --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=matplotlib.backends.backend_agg --hidden-import=matplotlib._pylab_helpers app.py
##############################################################################




# Global variables for dataframe and saved selections
df = None
primary_selections = []
secondary_selections = []
green_items = []
green_items2 = []



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
# Function to update listboxes with column names
def update_listboxes():
    global df
    if df is not None:
        primary_listbox.delete(0, 'end')
        secondary_listbox.delete(0, 'end')
        
        # Loop through columns and exclude "Time" if it exists
        for col in df.columns:
            if col != "Time":  # Exclude "Time" column
                primary_listbox.insert('end', col)
                secondary_listbox.insert('end', col)


# Function to save selected parameters from the primary ListBox
def save_primary_selection():
   
    global primary_selections, green_items2
    primary_selections = [primary_listbox.get(i) for i in primary_listbox.curselection()]
    green_items2.clear()  # Clear the list before adding new green items

    # Color the selected items green and store their indices
    for i in primary_listbox.curselection():
        primary_listbox.itemconfig(i, {'fg': 'green'})  # Color selected items green
        green_items2.append(i)  # Store the index of green-colored items


    

# Function to save selected parameters from the secondary ListBox
def save_secondary_selection():
    global secondary_selections, green_items
    secondary_selections = [secondary_listbox.get(i) for i in secondary_listbox.curselection()]
    green_items.clear()  # Clear the previous list of green-colored items

    for i in secondary_listbox.curselection():
        secondary_listbox.itemconfig(i, {'fg': 'green'})  # Set the selected item to green
        green_items.append(i)  # Clear the previous list of green-colored items

  

  
def Clear_selection1():
    
    global primary_selections, green_items2
    primary_selections = [primary_listbox.select_clear(i) for i in primary_listbox.curselection()]
   
    for i in green_items2:
        primary_listbox.itemconfig(i, {'fg': 'black'})
        
        green_items2.clear() 
        
       
        
def Clear_selection2():
    
    global secondary_selections,green_items
 
    secondary_selections = [secondary_listbox.select_clear(i) for i in secondary_listbox.curselection()]
    
    for i in green_items:
        secondary_listbox.itemconfig(i, {'fg': 'black'}) 
    green_items.clear()
    

def save_configuration():
    config = {
        'primary_parameters': primary_selections,
        'secondary_parameters': secondary_selections,
        'show_max': show_max_var.get(),
        'show_min': show_min_var.get(),
        'show_avg': show_avg_var.get(),
    }
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        messagebox.showinfo("Info", "saved.")
   # else:
        #messagebox.showerror("Error", "Configuration not saved.")



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

def plot_selected_parameters():
    if df is not None:
        time_log = df['Time']  # Assuming 'Time' is the column in your DataFrame
        x_data = [convert_time_to_seconds(time_str) for time_str in time_log]
        
        # Fetch start and end times from the entries
        start_time = float(start_time_entry.get()) if start_time_entry.get() else 0
        end_time = float(end_time_entry.get()) if end_time_entry.get() else x_data[-1]

        # Filter x_data and corresponding parameters within the specified range
        x_data_filtered = [x for x in x_data if start_time <= x <= end_time]
        start_index = x_data.index(x_data_filtered[0]) if x_data_filtered else 0
        end_index = x_data.index(x_data_filtered[-1]) + 1 if x_data_filtered else len(x_data)
        
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx() if secondary_selections else None
        
        # Set tick parameters for primary axis
        ax1.tick_params(axis='both', which='major', labelsize=16)
        ax1.tick_params(axis='x', labelsize=16)

        chart_title = chart_title_entry.get() if chart_title_entry.get() else "Title"

        # Plot primary parameters within the time range
        for param in primary_selections:
            if param in df.columns:
                data = df[param][start_index:end_index]  # Filter data within the range
                label = param
                if show_max_var.get():
                    label += f'\nMax: {data.max():.2f}'
                if show_min_var.get():
                    label += f'\nMin: {data.min():.2f}'
                if show_avg_var.get():
                    label += f'\nAvg: {data.mean():.2f}'
                ax1.plot(x_data_filtered, data, label=label)

        if ax2:
            for param in secondary_selections:
                if param in df.columns:
                    data = df[param][start_index:end_index]  # Filter data within the range
                    label = param
                    if show_max_var.get():
                        label += f'\nMax: {data.max():.2f}'
                    if show_min_var.get():
                        label += f'\nMin: {data.min():.2f}'
                    if show_avg_var.get():
                        label += f'\nAvg: {data.mean():.2f}'
                    ax2.plot(x_data_filtered, data, linestyle='--', label=label)

            ax1.grid(True)
            ax1.set_title(chart_title, fontsize=16)
            ax1.set_xlabel(f'Time [Sec]', fontsize=14)

            # Legend positioning
            handles1, labels1 = ax1.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels() if ax2 else ([], [])
            ax1.legend(handles=handles1, loc='upper center', bbox_to_anchor=(0.25, -0.2), ncol=1, prop={'size': 10})
            ax2.legend(handles=handles2, loc='upper center', bbox_to_anchor=(0.75, -0.2), ncol=1, prop={'size': 10})
            
        else:
            ax1.grid(True)
            ax1.set_title(chart_title, fontsize=16)
            ax1.set_xlabel(f'Time [Sec]', fontsize=14)
            ax1.legend(loc='upper center', bbox_to_anchor=(0.75, -0.2), ncol=1, prop={'size': 10})

        plt.subplots_adjust(left=0.15, bottom=0.3, right=0.85, top=0.9, wspace=0.2, hspace=0.2)
        plt.show()
        
    else:
        messagebox.show




def plot_from_configurations():
    if df is not None:  # Check if DataFrame is loaded
        # Get start and end times from user input (assuming these entries exist in your UI)
        try:
            start_time = float(start_time_entry.get())
        except ValueError:
            start_time = 0  # Default to 0 if input is invalid
        try:
            end_time = float(end_time_entry.get())
        except ValueError:
            end_time = df['Time'].apply(convert_time_to_seconds).max()  # Default to max time if input is invalid

        filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
        if filepaths:
            num_configs = len(filepaths)
            fig, axs = plt.subplots(num_configs, 1, figsize=(8, num_configs * 5), constrained_layout=True)

            if num_configs == 1:
                axs = [axs]  # Ensure axs is always a list even for one subplot

            # Define color cycles for primary and secondary axes
            primary_colors = itertools.cycle(plt.cm.tab10.colors)
            secondary_colors = itertools.cycle(plt.cm.Set2.colors)

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
                    x_data = df[x_param].apply(convert_time_to_seconds)

                    # Apply start and end time filters to x_data and corresponding parameter data
                    mask = (x_data >= start_time) & (x_data <= end_time)
                    x_data_filtered = x_data[mask]

                    # Filter and plot primary parameters
                    for param in primary_params:
                        if param in df.columns:
                            data = df[param][mask]  # Filter data using mask
                            label = param
                            if show_max:
                                label += f'\nMax: {data.max():.2f}'
                            if show_min:
                                label += f'\nMin: {data.min():.2f}'
                            if show_avg:
                                label += f'\nAvg: {data.mean():.2f}'
                            color = next(primary_colors)
                            ax.plot(x_data_filtered, data, label=label, color=color)

                    # Filter and plot secondary parameters if any
                    ax2 = None
                    if secondary_params:
                        ax2 = ax.twinx()
                        for param in secondary_params:
                            if param in df.columns:
                                data = df[param][mask]
                                label = param
                                if show_max:
                                    label += f'\nMax: {data.max():.2f}'
                                if show_min:
                                    label += f'\nMin: {data.min():.2f}'
                                if show_avg:
                                    label += f'\nAvg: {data.mean():.2f}'
                                color = next(secondary_colors)
                                ax2.plot(x_data_filtered, data, linestyle='--', label=label, color=color)

                    # Position legends as specified
                    handles1, labels1 = ax.get_legend_handles_labels()
                    handles2, labels2 = (ax2.get_legend_handles_labels() if ax2 else ([], []))
                    ax.legend(handles=handles1, loc='upper center', bbox_to_anchor=(0.25, -0.2), ncol=1, prop={'size': 8})
                    if ax2:
                        ax2.legend(handles=handles2, loc='upper center', bbox_to_anchor=(0.75, -0.2), ncol=1, prop={'size': 8})

                    ax.grid(True)
                    ax.set_ylabel('', fontsize=12)
                    if ax2:
                        ax2.set_ylabel('', fontsize=12)

                    # Set title and x-axis label
                    ax.set_title(f'{os.path.splitext(os.path.basename(filepath))[0]}', fontsize=14)
                    ax.set_xlabel(f'Time [Sec]', fontsize=12)

                    # Set tick parameters for both axes
                    ax.tick_params(axis='both', which='major', labelsize=16)
                    ax.tick_params(axis='x', labelsize=16)
                    if ax2:
                        ax2.tick_params(axis='both', which='major', labelsize=16)

            plt.subplots_adjust(left=0.15, bottom=0.3, right=0.85, top=0.9, hspace=0.3)
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
show_max_var = tk.BooleanVar(value=False)
show_min_var = tk.BooleanVar(value=False)
show_avg_var = tk.BooleanVar(value=False)

# Create checkboxes and link them to the variables
show_max_checkbox = tk.Checkbutton(root, text=" Max", variable=show_max_var, font=small_font)
show_min_checkbox = tk.Checkbutton(root, text=" Min", variable=show_min_var, font=small_font)
show_avg_checkbox = tk.Checkbutton(root, text=" Avg", variable=show_avg_var, font=small_font)



# Add buttons with smaller dimensions
load_button = Button(root, text="Load Log", command=load_file, width=15, height=1, font=small_font, bg='lightblue')
load_button.pack(pady=5)

primary_frame = tk.Frame(root)
primary_frame.pack(pady=5)

# Primary Listbox and Save Button
primary_listbox = tk.Listbox(primary_frame, selectmode=tk.MULTIPLE, width=30, height=10, bg='white')
primary_listbox.pack(side=tk.RIGHT, expand=True, fill='both')


# Save Button for Axis 1
save_primary_button = Button(primary_frame, text="Save Axis 1", command=save_primary_selection, width=15, height=1, font=small_font, bg='lightblue')
save_primary_button.pack(side=tk.TOP, pady=5)  # Stack vertically (top) with padding

# Clear selection Button for Axis 1
clear_selection_button1 = Button(primary_frame, text="Clear Axis 1", command=Clear_selection1, width=15, height=1, font=small_font, bg='red')
clear_selection_button1.pack(side=tk.TOP, pady=5)  # Stack below save button with padding


# Secondary Listbox and Save Button
secondary_frame = tk.Frame(root)
secondary_frame.pack(pady=5)

# Secondary Listbox
secondary_listbox = tk.Listbox(secondary_frame, selectmode=tk.MULTIPLE, width=30, height=10, bg='white')
secondary_listbox.pack(side=tk.RIGHT, expand=True, fill='both')

# Save Button for Axis 2
save_secondary_button = Button(secondary_frame, text="Save Axis 2", command=save_secondary_selection, width=15, height=1, font=small_font, bg='lightblue')
save_secondary_button.pack(side=tk.TOP, pady=5)  # Pack with padding along the Y-axis (vertical)

# Clear selection Button for Axis 2
clear_selection_button = Button(secondary_frame, text="Clear Axis 2", command=Clear_selection2, width=15, height=1, font=small_font, bg='red')
clear_selection_button.pack(side=tk.TOP, pady=5)  # Pack below the save button with padding


# Create and place the label and entry box for chart title
chart_title_label = Label(root, text="------------------------------------------------------------------\n" "\nEnter Chart Title:")
chart_title_label.pack(pady=10)  # Adjust padding for spacing

chart_title_entry = Entry(root, width=40)  # Adjust the width as needed
chart_title_entry.pack(pady=5)

Timeframe_lable = Label(root, text=" Chart Time Frame [sec]")
Timeframe_lable.pack(pady=10)

start_time_label = tk.Label(root, text="Start Time")
start_time_label.pack()
start_time_entry = tk.Entry(root)
start_time_entry.pack()

end_time_label = tk.Label(root, text="End Time")
end_time_label.pack()
end_time_entry = tk.Entry(root)
end_time_entry.pack()



# Plot parameter Button
plot_button = Button(root, text="Create Chart", command=plot_selected_parameters, width=20, height=1, font=small_font, bg='lightgreen')
plot_button.pack(pady=5)

# Save Configuration Button
save_config_button = Button(root, text="Save Chart Config", command=save_configuration, width=20, height=1, font=small_font, bg='lightblue')
save_config_button.pack(pady=5)

# Load saved plot Button
plot_config_button = Button(root, text="Load Chart Config", command=plot_from_configurations, width=20, height=1, font=small_font, bg='lightblue')
plot_config_button.pack(pady=5)






# Place the checkboxes at the bottom
show_max_checkbox.pack()
show_min_checkbox.pack()
show_avg_checkbox.pack()

# Run the Tkinter event loop
root.mainloop()