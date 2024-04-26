import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('pythonic_journey.csv')

# Convert the 'First Usage Date' column to datetime type
df['First Usage Date'] = pd.to_datetime(df['First Usage Date'])

# Create the ColumnDataSource from the DataFrame
source = ColumnDataSource(df)

p = figure(title="Package Usage Over Time", x_axis_label='Date', y_axis_label='Usage Count', x_axis_type='datetime', tools=['hover'])

hover = HoverTool(tooltips=[
    ("Date First Used", "@{First Usage Date}{%F}"),
    ("Package", "@package"),
    ("Usage Count", "@Usage Count")
], formatters={'@{First Usage Date}': 'datetime'})

p.add_tools(hover)

p.scatter(x='First Usage Date', y='Usage Count', source=source, size=10, color='blue')

show(p)

