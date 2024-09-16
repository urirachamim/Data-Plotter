import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json
import tkinter as tk

# Global variable for dataframe
df = None

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
        
        listbox.delete(0, 'end')
        for col in df.columns:
            listbox.insert('end', col)

# Function to save the selected parameters as a configuration to a file on user's computer
def save_configuration():
    selected = listbox.curselection()
    if selected:
        config = {
            'parameters': [],
            'show_max': show_max_var.get(),
            'show_min': show_min_var.get(),
            'show_avg': show_avg_var.get()
        }
        
        for i in selected:
            param = listbox.get(i)
            if param in df.columns:
                config['parameters'].append(param)

        # Save the configuration to a JSON file
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)
    else:
        messagebox.showerror("Error", "No parameters selected.")

# Function to plot selected parameters from the ListBox
def plot_selected_parameters():
    selected = listbox.curselection()
    if selected and df is not None:
        fig, ax1 = plt.subplots()

        # Determine if secondary axis is needed
        needs_secondary_axis = False
        primary_data = []
        secondary_data = []
        primary_params = []
        secondary_params = []

        # Collect data for plotting
        for i in selected:
            col = listbox.get(i)
            if col in df.columns:
                data = df[col]
                max_value = data.max()
                min_value = data.min()
                avg_value = data.mean()

                # Check if data needs secondary axis
                if max_value > 1000:
                    secondary_data.append(data)
                    secondary_params.append(col)
                    needs_secondary_axis = True
                else:
                    primary_data.append(data)
                    primary_params.append(col)

        # Create secondary axis only if needed
        if needs_secondary_axis:
            ax2 = ax1.twinx()
        else:
            ax2 = None

        # Plot on primary Y-axis
        for data, param in zip(primary_data, primary_params):
            label = param
            if show_max_var.get():
                label += f'\nMax: {data.max():.2f}'
            if show_min_var.get():
                label += f'\nMin: {data.min():.2f}'
            if show_avg_var.get():
                label += f'\nAvg: {data.mean():.2f}'
            ax1.plot(data, label=label)

        # Plot on secondary Y-axis
        if ax2:
            for data, param in zip(secondary_data, secondary_params):
                label = param
                if show_max_var.get():
                    label += f'\nMax: {data.max():.2f}'
                if show_min_var.get():
                    label += f'\nMin: {data.min():.2f}'
                if show_avg_var.get():
                    label += f'\nAvg: {data.mean():.2f}'
                ax2.plot(data, linestyle='--', label=label)

            # Set labels for secondary axis
            ax1.set_title('Selected Parameters Plot')
            ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.5), prop={'size': 8})
            ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.3), prop={'size': 8})
        else:
            ax1.set_title('Selected Parameters Plot')
            ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})

        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75, top=0.9, wspace=0.2, hspace=0.2)
        plt.show()
    else:
        messagebox.showerror("Error", "No parameters selected or no file loaded.")

# Function to plot parameters from configurations
def plot_from_configurations():
    filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if filepaths and df is not None:
        num_configs = len(filepaths)
        fig, axs = plt.subplots(num_configs, 1, figsize=(8, num_configs * 5), constrained_layout=True)

        if num_configs == 1:
            axs = [axs]

        for idx, filepath in enumerate(filepaths):
            ax = axs[idx]
            ax2 = ax.twinx() if any(df[param].max() > 1000 for param in json.load(open(filepath)).get('parameters', [])) else None

            with open(filepath, 'r') as file:
                ax.set_title(f'{os.path.splitext(os.path.basename(filepath))[0]}')
                config = json.load(file)
                parameters = config.get('parameters', [])
                
                show_max = config.get('show_max', True)
                show_min = config.get('show_min', True)
                show_avg = config.get('show_avg', True)
                

                primary_data = []
                secondary_data = []
                primary_params = []
                secondary_params = []
                

                for param in parameters:
                    if param in df.columns:
                        data = df[param]
                        

                        if data.max() > 1000:
                            secondary_data.append(data)
                            secondary_params.append(param)
                        else:
                            primary_data.append(data)
                            primary_params.append(param)
                            

                # Plot on primary Y-axis
                for data, param in zip(primary_data, primary_params):
                    
                    label = param
                    if show_max:
                        label += f'\nMax: {data.max():.2f}'
                    if show_min:
                        label += f'\nMin: {data.min():.2f}'
                    if show_avg:
                        label += f'\nAvg: {data.mean():.2f}'
                        
                    ax.plot(data, label=label)
                    

                # Plot on secondary Y-axis
                if secondary_data:
                    
                    for data, param in zip(secondary_data, secondary_params):
                        label = param
                        if show_max:
                            label += f'\nMax: {data.max():.2f}'
                        if show_min:
                            label += f'\nMin: {data.min():.2f}'
                        if show_avg:
                            label += f'\nAvg: {data.mean():.2f}'
                        ax2.plot(data, linestyle='--', label=label)

                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
                if ax2:
                    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.3), prop={'size': 8})

        plt.show()
    else:
        messagebox.showerror("Error", "No configuration files selected or no file loaded.")

# Create the Tkinter window
root = Tk()
root.title('Data Plotter')

# Set the window size
root.geometry('300x800')


# Define the variables to track checkbox states
show_max_var = tk.BooleanVar(value=True)
show_min_var = tk.BooleanVar(value=True)
show_avg_var = tk.BooleanVar(value=True)

# Create checkboxes and link them to the variables
show_max_checkbox = tk.Checkbutton(root, text="Show Max", variable=show_max_var)
show_min_checkbox = tk.Checkbutton(root, text="Show Min", variable=show_min_var)
show_avg_checkbox = tk.Checkbutton(root, text="Show Avg", variable=show_avg_var)



# Create a font object with bold style
bold_font = font.Font(weight='bold')

# Add Load File Button with bold text
load_button = Button(root, text="Load File", command=load_file, width=20, height=2, font=bold_font,bg='lightblue')
load_button.pack(pady=10)

# Add Listbox with specific width and height
listbox = Listbox(root, selectmode=MULTIPLE, width=50, height=15)
listbox.pack(expand=True, fill='both', pady=10)

# Add Plot from Listbox Button with bold text (for direct plotting)
plot_button = Button(root, text="Plot ", command=plot_selected_parameters, width=20, height=2, font=bold_font,bg='lightblue')
plot_button.pack(pady=4)

# Add Save Configuration Button
save_button = Button(root, text="Save Configuration", command=save_configuration, width=20, height=2, font=bold_font,bg='lightblue')
save_button.pack(pady=4)

# Add Plot from Configurations Button with bold text (for multi-chart plotting)
plot_config_button = Button(root, text="Plot Configurations", command=plot_from_configurations, width=20, height=2, font=bold_font,bg='lightblue')
plot_config_button.pack(pady=4)

# Pack or grid the checkboxes (depending on your layout)
show_max_checkbox.pack(side='left', padx=5)
show_min_checkbox.pack(side='left', padx=5)
show_avg_checkbox.pack(side='left', padx=5)

# Run the application
root.mainloop()
