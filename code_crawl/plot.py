import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, Label, DatetimeTickFormatter, YearsTicker
from bokeh.palettes import Category20, viridis
import numpy as np
from bokeh.transform import factor_cmap
from bokeh.models import CategoricalColorMapper


# Read the CSV file into a pandas DataFrame
df = pd.read_csv('merged_libraries.csv')

# Convert relevant columns and prepare data
df['Date_First_Used'] = pd.to_datetime(df['Date_First_Used'], errors='coerce')
df['Total_Files'] = pd.to_numeric(df['Total_Files'], errors='coerce')
df['Label'] = df['Label'].astype(str)
df['Scaled_Total_Files'] = 0.15 * df['Total_Files']

# Create the ColumnDataSource
source = ColumnDataSource(df)

# Set up the figure
p = figure(
    title="Python Libraries Used Over Time",
    x_axis_type='datetime',
    width=1000,
    x_range=(pd.Timestamp('2019-01-01'), pd.Timestamp('2028-12-31')),
    x_axis_label='Date',
    y_axis_label='Total Files'
)

# Formatting the x-axis to show every year
# Formatting the x-axis to show every year
p.xaxis.ticker = YearsTicker(desired_num_ticks=(2028 - 2019 + 1))
p.xaxis.formatter = DatetimeTickFormatter(years="%Y")

# Suppose df['Label'].unique() gives us all unique labels
unique_labels = df['Label'].unique()
num_labels = len(unique_labels)

# Use a large palette or combine multiple palettes
# Repeating Category20 to cover all labels if more than 20
if num_labels > 20:
    repeated_palette = list(Category20[20]) * (num_labels // 20) + list(Category20[20][:num_labels % 20])
else:
    repeated_palette = Category20[num_labels]

# Avoiding specific color (e.g., 'orange') for a specific label
if 'orange' in repeated_palette:
    orange_index = repeated_palette.index('orange')
    repeated_palette[orange_index] = 'blue'  # Replace orange with another color (green here)

# Color mapping, ensuring 'Data Science' gets a specific color
color_mapping = {label: color for label, color in zip(unique_labels, repeated_palette)}
color_mapping['Data Science'] = 'blue'  # Setting 'Data Science' explicitly to green

# Create a color mapper from your custom color mapping dictionary
color_mapper = CategoricalColorMapper(palette=list(color_mapping.values()), factors=list(color_mapping.keys()))

# Use the color mapper in your scatter plot
scatter = p.scatter(
    'Date_First_Used',
    'Total_Files',
    source=source,
    size='Scaled_Total_Files',
    color={'field': 'Label', 'transform': color_mapper},
    line_color='black',
    line_width=1,
    legend_field='Label'
)

# Annotations for specific libraries
specified_libraries = ['flask', 'keras', 'langchain', 'llama_index', 'nltk', 'openai', 'pandas', 'sagemaker', 'sklearn', 'tensorflow', 'torch', 'xgboost', 'pinecone', 'redis']
offsets = {
    'flask': (5, 20),
    'langchain': (10, 20),
    'llama_index': (15, 200),
    'nltk': (10, 70),
    'openai': (25, 65),
    'sagemaker': (10, 50),
    'sklearn': (5, 5),
    'tensorflow': (10, 40),
    'torch': (5, 120),
    'xgboost': (10, 100),
    'redis': (5, 180),
    'pinecone': (10, 100),
}

for library in specified_libraries:
    lib_data = df[df['Library'].str.lower() == library.lower()].sort_values('Date_First_Used', ascending=False).head(1)
    if not lib_data.empty:
        offset = offsets.get(library.lower(), (5, 5))  # Default offset if not specified
        annotation = Label(
            x=lib_data['Date_First_Used'].iloc[0],
            y=lib_data['Total_Files'].iloc[0],
            text=library.capitalize(),
            text_font_size='13pt',
            x_offset=offset[0],
            y_offset=offset[1],
            background_fill_color='white',
            background_fill_alpha=0.7
        )
        p.add_layout(annotation)
# Hover tool setup
hover = HoverTool(tooltips=[
    ("Library", "@Library"),
    ("Date First Used", "@Date_First_Used{%F}"),
    ("Total Files", "@Total_Files"),
    ("Category", "@Category"),
    ("Label", "@Label")
], formatters={'@Date_First_Used': 'datetime'})
p.add_tools(hover)

# Configure legend
p.legend.location = 'top_right'
p.legend.click_policy = "hide"  # Allows hiding of lines on legend item click

# Show the plot
show(p)
