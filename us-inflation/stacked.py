import pandas as pd
import os
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, FactorRange
from bokeh.layouts import gridplot
from bokeh.io import save
from bokeh.palettes import Category20

# Directory containing the CSV files
directory_path = "./Chicago"

# Specify the files to include
selected_files = [
    "Commodities_less_food.csv",
    "Energy.csv",
    "Nondurables.csv",
    "Services_less_medical_care_services.csv"
]

# Create a dictionary with file names (without '.csv') as keys and file paths as values
file_paths = {file[:-4]: os.path.join(directory_path, file) for file in selected_files}

# Initialize an empty DataFrame to hold all data
all_data = pd.DataFrame()

# Loop through the dictionary to read and transform each dataset
for category, path in file_paths.items():
    # Load dataset
    df = pd.read_csv(path)
    
    # Load data starting from 2019 for calculation, but visualization will be from 2020 onwards
    df = df[df['Year'].between(2019, 2024)]
    
    # Melt the DataFrame to long format, ignoring 'Annual', 'HALF1', and 'HALF2'
    df_long = df.melt(id_vars='Year', value_vars=df.columns[1:13], var_name='Month', value_name='Price Level')
    
    # Add a column for category before the groupby operation
    df_long['Category'] = category
    
    # Calculate Year-over-Year Inflation Rate
    df_long['Inflation Rate'] = df_long.groupby(['Category', 'Month'])['Price Level'].pct_change(fill_method=None) * 100
    
    # Append to the main DataFrame
    all_data = pd.concat([all_data, df_long], ignore_index=True)

# Load the 'All_items.csv' data separately
all_items_path = os.path.join(directory_path, "All_items.csv")
all_items_df = pd.read_csv(all_items_path)
all_items_df = all_items_df[all_items_df['Year'].between(2019, 2024)]
all_items_df_long = all_items_df.melt(id_vars='Year', value_vars=all_items_df.columns[1:13], var_name='Month', value_name='Price Level')
all_items_df_long['Category'] = 'All_items'
all_items_df_long['Inflation Rate'] = all_items_df_long.groupby(['Category', 'Month'])['Price Level'].pct_change(fill_method=None) * 100

# Filter data to include only 2020 to 2024 for visualization
all_data = all_data[all_data['Year'] >= 2020]
all_items_df_long = all_items_df_long[all_items_df_long['Year'] >= 2020]

# Convert 'Month' to categorical to control order in plots
months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
all_data['Month'] = pd.Categorical(all_data['Month'], categories=months_order, ordered=True)
all_items_df_long['Month'] = pd.Categorical(all_items_df_long['Month'], categories=months_order, ordered=True)

# Set output to HTML file
output_file("interactive_inflation_plots.html")

# Map each category to a color using Category20 palette
category_colors = {category: color for category, color in zip(file_paths.keys(), Category20[len(file_paths)])}

# Create a list to hold the plot objects
plot_list = []

# Generate a plot for each year
for year in all_data['Year'].unique():
    # Filter data for the current year
    year_data = all_data[all_data['Year'] == year]
    year_all_items_data = all_items_df_long[all_items_df_long['Year'] == year]
    
    # Pivot the data to create a stacked bar chart
    year_pivot = year_data.pivot_table(index='Month', columns='Category', values='Inflation Rate')
    year_all_items_pivot = year_all_items_data.pivot_table(index='Month', columns='Category', values='Inflation Rate')
    
    # Create the stacked bar chart
    p = figure(x_range=FactorRange(*months_order), title=f"Inflation Rates - {year}", width=800, height=400, tools="pan,wheel_zoom,box_zoom,reset")
    
    # Set the bar width to 0.8 for wider bars
    bar_width = 0.8
    
    # Plot each category as a stacked bar
    for i, category in enumerate(year_pivot.columns):
        category_display = category.replace('_', ' ')  # Replace underscores with spaces for display
        color = category_colors[category]
        source = ColumnDataSource(year_pivot)
        p.vbar(x='Month', top=category, source=source, width=bar_width, color=color, legend_label=category_display)
    
    # Add hover tooltips for each bar
    hover_tooltips = [('Month', '@Month')]
    for category in year_pivot.columns:
        category_display = category.replace('_', ' ')
        hover_tooltips.append((category_display, f'@{{{category}}}{{0.2f}}%'))
    
    # Merge the 'All_items' data with the main data for the hover tooltip
    year_pivot_with_all_items = pd.concat([year_pivot, year_all_items_pivot], axis=1)
    hover_tooltips.append(('All Items', '@{All_items}{0.2f}%'))
    
    # Create a ColumnDataSource for the merged data
    source_with_all_items = ColumnDataSource(year_pivot_with_all_items)
    
    hover = HoverTool(tooltips=hover_tooltips, mode='mouse', point_policy='follow_mouse')
    p.add_tools(hover)
    
    p.xaxis.major_label_orientation = 1.57  # Rotate labels
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    plot_list.append(p)

# Arrange plots vertically
grid = gridplot(plot_list, ncols=1)

# Show the plot
show(grid)

# Optionally, save the plot to an HTML file
save(grid)