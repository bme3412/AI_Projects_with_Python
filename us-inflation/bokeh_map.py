from string import Template
import folium
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import CDN
from branca.element import IFrame
import pandas as pd
import os
from bokeh.models import ColumnDataSource, HoverTool, FactorRange
from bokeh.layouts import gridplot
from bokeh.palettes import Category20

def generate_city_plot(city):
    directory_path = f"./{city}"

    selected_files = [
        "Commodities_less_food.csv",
        "Energy.csv",
        "Nondurables.csv",
        "Services_less_medical_care_services.csv"
    ]
    
    file_paths = {file[:-4]: os.path.join(directory_path, file) for file in selected_files}
    
    all_data = pd.DataFrame()

    for category, path in file_paths.items():
        df = pd.read_csv(path)
        df = df[df['Year'].between(2019, 2024)]
        df_long = df.melt(id_vars='Year', value_vars=df.columns[1:13], var_name='Month', value_name='Price Level')
        df_long['Category'] = category
        df_long['Inflation Rate'] = df_long.groupby(['Category', 'Month'])['Price Level'].pct_change(fill_method=None) * 100
        all_data = pd.concat([all_data, df_long], ignore_index=True)

    all_items_path = os.path.join(directory_path, "All_items.csv")
    all_items_df = pd.read_csv(all_items_path)
    all_items_df = all_items_df[all_items_df['Year'].between(2019, 2024)]
    all_items_df_long = all_items_df.melt(id_vars='Year', value_vars=all_items_df.columns[1:13], var_name='Month', value_name='Price Level')
    all_items_df_long['Category'] = 'All_items'
    all_items_df_long['Inflation Rate'] = all_items_df_long.groupby(['Category', 'Month'])['Price Level'].pct_change(fill_method=None) * 100

    all_data = all_data[all_data['Year'] >= 2020]
    all_items_df_long = all_items_df_long[all_items_df_long['Year'] >= 2020]

    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    all_data['Month'] = pd.Categorical(all_data['Month'], categories=months_order, ordered=True)
    all_items_df_long['Month'] = pd.Categorical(all_items_df_long['Month'], categories=months_order, ordered=True)

    category_colors = {category: color for category, color in zip(file_paths.keys(), Category20[len(file_paths)])}
    plot_list = []

    for year in all_data['Year'].unique():
        year_data = all_data[all_data['Year'] == year]
        year_all_items_data = all_items_df_long[all_items_df_long['Year'] == year]

        year_pivot = year_data.pivot_table(index='Month', columns='Category', values='Inflation Rate')
        year_all_items_pivot = year_all_items_data.pivot_table(index='Month', columns='Category', values='Inflation Rate')

        p = figure(x_range=FactorRange(*months_order), title=f"Inflation Rates - {year} ({city})", width=800, height=400, tools="pan,wheel_zoom,box_zoom,reset")
        bar_width = 0.8

        for i, category in enumerate(year_pivot.columns):
            category_display = category.replace('_', ' ')
            color = category_colors[category]
            source = ColumnDataSource(year_pivot)
            p.vbar(x='Month', top=category, source=source, width=bar_width, color=color, legend_label=category_display)

        hover_tooltips = [('Month', '@Month')]
        for category in year_pivot.columns:
            category_display = category.replace('_', ' ')
            hover_tooltips.append((category_display, f'@{{{category}}}{{0.2f}}%'))

        year_pivot_with_all_items = pd.concat([year_pivot, year_all_items_pivot], axis=1)
        hover_tooltips.append(('All Items', '@{All_items}{0.2f}%'))

        source_with_all_items = ColumnDataSource(year_pivot_with_all_items)

        hover = HoverTool(tooltips=hover_tooltips, mode='mouse', point_policy='follow_mouse')
        p.add_tools(hover)

        p.xaxis.major_label_orientation = 1.57
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

        plot_list.append(p)

    grid = gridplot(plot_list, ncols=1)
    return file_html(grid, CDN, f"{city} Inflation Plots")


map_us = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

cities = ["New_York", "Los_Angeles", "Chicago", "Atlanta", "Dallas", "Miami", "Phoenix", "San_Francisco", "Seattle"]
lats = [40.7128, 34.0522, 41.8781, 33.7490, 32.7767, 25.7617, 33.4484, 37.7749, 47.6062]
lons = [-74.0060, -118.2437, -87.6298, -84.3880, -96.7970, -80.1918, -112.0740, -122.4194, -122.3321]

for city, lat, lon in zip(cities, lats, lons):
    if city in ["New_York", "Los_Angeles", "Chicago", "Atlanta", "Dallas", "Miami", "Phoenix", "San_Francisco", "Seattle"]:
        city_plot_html = generate_city_plot(city)
        iframe_html = folium.IFrame(city_plot_html, width=800, height=600)
        popup_html = folium.Popup(iframe_html, max_width=800)
        tooltip_html = f"<b>{city}</b>"
        marker = folium.Marker(location=[lat, lon], popup=popup_html, tooltip=tooltip_html)
    else:
        plot = figure(title=f"Data for {city}", x_axis_label="Data X", y_axis_label="Data Y")
        plot.line([2010, 2011, 2012], [2.5, 3.2, 2.8], legend_label="Sample Data")
        plot_html = file_html(plot, CDN, f"Plot for {city}")
        iframe_html = folium.IFrame(plot_html, width=400, height=300)
        popup_html = folium.Popup(iframe_html, max_width=400)
        tooltip_html = f"<b>{city}</b>"
        marker = folium.Marker(location=[lat, lon], popup=popup_html, tooltip=tooltip_html)
    
    marker.add_to(map_us)

map_us.save("us_map_with_tooltips.html")