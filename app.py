import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Listbox, MULTIPLE, font, filedialog, messagebox
import json

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

# Function to plot selected parameters from the listbox (direct plot option)
def plot_selected_parameters():
    selected = listbox.curselection()
    if selected and df is not None:
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
    else:
        messagebox.showerror("Error", "No parameters selected or no file loaded.")

# Function to plot parameters from multiple configurations as separate charts (subplot for each configuration)
def plot_from_configurations():
    filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if filepaths and df is not None:
        fig, axs = plt.subplots(len(filepaths), 1, figsize=(8, len(filepaths) * 5), constrained_layout=True)

        # If only one configuration is loaded, ensure axs is treated as an iterable
        if len(filepaths) == 1:
            axs = [axs]

        for idx, filepath in enumerate(filepaths):
            with open(filepath, 'r') as file:
                config = json.load(file)
                parameters = config.get('parameters', [])
                
                # Plot all selected parameters in one chart (subplot)
                for param in parameters:
                    if param in df.columns:
                        col = df[param]
                        max_value = col.max()
                        min_value = col.min()
                        avg_value = col.mean()

                        axs[idx].plot(df[param], label=f'{param} (Max: {max_value:.2f}, Min: {min_value:.2f}, Avg: {avg_value:.2f})')

                # Set the chart title to the configuration file name
                axs[idx].set_title(f'Configuration: {os.path.basename(filepath)}')

                # Set labels for each subplot
                axs[idx].set_xlabel('Index')
                axs[idx].set_ylabel('Values')

                # Add legend to each subplot
                axs[idx].legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})

        # Show the entire figure with all subplots
        plt.show()
    else:
        messagebox.showerror("Error", "No configuration files selected or no data file loaded.")

# Create the Tkinter window
root = Tk()
root.title('Data Plotter')

# Set the window size
root.geometry('800x600')


# Create a font object with bold style
bold_font = font.Font(weight='bold')

# Add Load File Button with bold text
load_button = Button(root, text="Load File", command=load_file, width=20, height=2, font=bold_font )
load_button.pack(pady=10)

# Add Listbox with specific width and height
listbox = Listbox(root, selectmode=MULTIPLE, width=50, height=15)
listbox.pack(expand=True, fill='both', pady=10)

# Add Save Configuration Button
save_button = Button(root, text="Save Configuration", command=save_configuration, width=20, height=2, font=bold_font)
save_button.pack(pady=10)



# Add Plot from Listbox Button with bold text (for direct plotting)
plot_button = Button(root, text="Plot Selected", command=plot_selected_parameters, width=20, height=2, font=bold_font)
plot_button.pack(pady=10)

# Add Plot from Configurations Button with bold text (for multi-chart plotting)
plot_config_button = Button(root, text="Plot from Configurations", command=plot_from_configurations, width=20, height=2, font=bold_font)
plot_config_button.pack(pady=10)

# Run the application
root.mainloop()
