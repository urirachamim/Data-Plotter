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
            ax1.plot(data, label=f'{param} (Max: {data.max():.2f}, Min: {data.min():.2f}, Avg: {data.mean():.2f})')

        # Plot on secondary Y-axis
        if ax2:
            for data, param in zip(secondary_data, secondary_params):
                ax2.plot(data, linestyle='--', label=f'{param} (Max: {data.max():.2f}, Min: {data.min():.2f}, Avg: {data.mean():.2f})')

            # Set labels for secondary axis
            x_label = 'Index'
            y_label_primary = 'Primary Parameters'
            y_label_secondary = 'Secondary Parameters'

            ax1.set_xlabel(x_label)
            ax1.set_ylabel(y_label_primary)
            ax2.set_ylabel(y_label_secondary)
            ax1.set_title('Selected Parameters Plot')

            # Set legends
            ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
            ax2.legend(loc='center left', bbox_to_anchor=(1, 0.3), prop={'size': 8})
        else:
            # Set labels for primary axis only
            x_label = 'Index'
            y_label_primary = 'Primary Parameters'

            ax1.set_xlabel(x_label)
            ax1.set_ylabel(y_label_primary)
            ax1.set_title('Selected Parameters Plot')

            # Set legend
            ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})

        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.75, top=0.9, wspace=0.2, hspace=0.2)
        plt.show()

      
    else:
        messagebox.showerror("Error", "No parameters selected or no file loaded.")


def plot_from_configurations():
    filepaths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if filepaths and df is not None:
        num_configs = len(filepaths)
        fig, axs = plt.subplots(num_configs, 1, figsize=(8, num_configs * 5), constrained_layout=True)

        # If only one configuration is loaded, ensure axs is treated as an iterable
        if num_configs == 1:
            axs = [axs]

        for idx, filepath in enumerate(filepaths):
            ax = axs[idx]
            ax2 = ax.twinx() if any(df[param].max() > 1000 for param in json.load(open(filepath)).get('parameters', [])) else None

            with open(filepath, 'r') as file:
                config = json.load(file)
                parameters = config.get('parameters', [])
                
                # Retrieve axis labels from config, with defaults
                x_label = config.get('x_label', 'Index')
                y_label_primary = config.get('y_label_primary', 'Primary Parameters')
                y_label_secondary = config.get('y_label_secondary', 'Secondary Parameters')

                primary_data = []
                secondary_data = []
                primary_params = []
                secondary_params = []

                for param in parameters:
                    if param in df.columns:
                        data = df[param]
                        max_value = data.max()
                        min_value = data.min()
                        avg_value = data.mean()

                        # Separate data for primary and secondary Y-axes
                        if max_value > 1000:
                            secondary_data.append(data)
                            secondary_params.append(param)
                        else:
                            primary_data.append(data)
                            primary_params.append(param)

                # Plot on primary Y-axis
                for data, param in zip(primary_data, primary_params):
                    ax.plot(data, label=f'{param} (Max: {data.max():.2f}, Min: {data.min():.2f}, Avg: {data.mean():.2f})')

                # Plot on secondary Y-axis
                if secondary_data:
                    for data, param in zip(secondary_data, secondary_params):
                        ax2.plot(data, linestyle='--', label=f'{param} (Max: {data.max():.2f}, Min: {data.min():.2f}, Avg: {data.mean():.2f})')
                    # Set labels for secondary axis
                    ax2.set_ylabel(y_label_secondary)

                # Set labels for primary axis
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label_primary)
                ax.set_title(f'{os.path.splitext(os.path.basename(filepath))[0]}')

                # Set legends
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 8})
                if secondary_data:
                    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.3), prop={'size': 8})

        plt.show()
        
        # Open the edit labels window after plotting
        for idx, filepath in enumerate(filepaths):
            with open(filepath, 'r') as file:
                config = json.load(file)
                x_label = config.get('x_label', 'Index')
                y_label_primary = config.get('y_label_primary', 'Primary Parameters')
                y_label_secondary = config.get('y_label_secondary', 'Secondary Parameters')
                
               
              
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