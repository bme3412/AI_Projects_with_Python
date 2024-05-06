# Interactive US Inflation Map

The Interactive US Inflation Map is a powerful data visualization tool that showcases inflation rates across major cities in the United States. Built using Python and leveraging libraries such as Folium, Bokeh, and Pandas, this project aims to provide users with an intuitive and informative way to explore inflation trends over time.

## Key Features

- **Interactive Map**: The application presents an interactive map of the United States, allowing users to easily navigate and explore inflation data for different cities.
- **City-specific Inflation Plots**: Each city on the map is represented by a marker that, when clicked, displays a detailed inflation plot specific to that city.
- **Inflation Rate Comparison**: The inflation plots showcase the inflation rates for various categories such as Commodities, Energy, Nondurables, and Services, enabling users to compare and analyze trends across different sectors.
- **Time-based Analysis**: The plots are generated for each year from 2020 onwards, providing a comprehensive view of inflation rates over time.
- **Tooltips and Popups**: Hovering over the markers on the map reveals tooltips with the city name, while clicking on a marker opens a popup containing the detailed inflation plot for that city.

## Technical Details

The Interactive US Inflation Map is implemented using Python and utilizes several powerful libraries:
- **Folium** is used to create the interactive map and handle marker placement and popups.
- **Bokeh** is employed to generate the interactive inflation plots, allowing for panning, zooming, and hovering interactions.
- **Pandas** is utilized for data manipulation and analysis, enabling efficient processing of inflation data stored in CSV files.

The project follows a modular approach, with separate functions for generating city-specific inflation plots and creating the overall interactive map. The inflation data is stored in CSV files organized by city and category, ensuring easy maintainability and extensibility.

## Example Usage

1. Open the "us_map_with_tooltips.html" file in a web browser.
2. Explore the interactive map of the United States, zooming and panning as desired.
3. Hover over a city marker to view the city name in a tooltip.
4. Click on a city marker to open a popup containing the detailed inflation plot for that city.
5. Analyze the inflation rates for different categories and years using the interactive plot features such as panning, zooming, and hovering.
