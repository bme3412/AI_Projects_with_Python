import os
import json
from datetime import datetime
import pandas as pd

def extract_metadata(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return process_file(file, file_path)
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:  # Fallback to Latin-1 if UTF-8 fails
            return process_file(file, file_path)

def process_file(file, file_path):
    if file_path.endswith('.ipynb'):
        notebook = json.load(file)
        return extract_ipynb_metadata(notebook, file_path)
    elif file_path.endswith('.py'):
        lines = file.readlines()
        return extract_py_metadata(lines, file_path)

def extract_ipynb_metadata(notebook, file_path):
    metadata = initialize_metadata(file_path)
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            update_code_cell_metadata(cell, metadata)
        elif cell['cell_type'] == 'markdown':
            metadata['num_markdown_cells'] += 1
    return finalize_metadata(metadata)

def extract_py_metadata(lines, file_path):
    metadata = initialize_metadata(file_path)
    if 'authored by brendan' in ' '.join(lines).lower():
        for line in lines:
            update_line_metadata(line, metadata)
    return finalize_metadata(metadata)

def initialize_metadata(file_path):
    created_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d')
    return {
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'created_date': created_date,
        'packages_used': set(),
        'first_used_date': {},
        'num_code_cells': 0,
        'num_markdown_cells': 0,
        'total_lines_of_code': 0
    }


def update_code_cell_metadata(cell, metadata):
    metadata['num_code_cells'] += 1
    metadata['total_lines_of_code'] += sum(1 for line in cell['source'] if line.strip() and not line.strip().startswith('#'))
    file_created_date = metadata['created_date']  # Retrieve the creation date from metadata
    for line in cell['source']:
        update_line_metadata(line, metadata, file_created_date)  # Pass the date when calling update_line_metadata


def update_line_metadata(line, metadata, file_created_date):
    if line.startswith('import ') or line.startswith('from '):
        package = line.split()[1].split('.')[0]
        metadata['packages_used'].add(package)
        if package not in metadata['first_used_date']:
            metadata['first_used_date'][package] = file_created_date
        else:
            # If the package date already exists, take the earliest date
            existing_date = datetime.strptime(metadata['first_used_date'][package], '%Y-%m-%d')
            current_date = datetime.strptime(file_created_date, '%Y-%m-%d')
            if current_date < existing_date:
                metadata['first_used_date'][package] = file_created_date


def finalize_metadata(metadata):
    # Convert set of packages to list of dictionaries including first used date
    packages_info = [{'package': pkg, 'first_used_date': metadata['first_used_date'][pkg]} for pkg in sorted(metadata['packages_used'])]
    metadata['packages_info'] = packages_info
    del metadata['packages_used']  # Cleanup if not needed
    del metadata['first_used_date']  # Cleanup if not needed
    return metadata



def crawl_directories(directories):
    file_metadata = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.ipynb') or file.endswith('.py'):
                    metadata = extract_metadata(file_path)
                    if metadata:
                        file_metadata.append(metadata)
    return file_metadata

# Define your directory paths and invoke the crawl function
directory_paths = [
    '/Users/brendan/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Data Science',
    '/Users/brendan/Desktop - Brendan’s MacBook Air/Python',
    '/Users/brendan/Desktop - Brendan’s MacBook Air/investment_apps',
    '/Users/brendan/Desktop - Brendan’s MacBook Air/Anthropic'
]

metadata_list = crawl_directories(directory_paths)
# Convert list of dictionaries into a DataFrame
all_packages_info = []
for metadata in metadata_list:
    for package_info in metadata['packages_info']:
        package_info.update({key: metadata[key] for key in metadata if key not in ['packages_info']})
        all_packages_info.append(package_info)

df = pd.DataFrame(all_packages_info)

# Ensure no NaN values and set the index
if not df.empty:
    df['First Usage Date'] = pd.to_datetime(df['first_used_date'], errors='coerce')
    package_df = df.groupby('package').agg({
        'First Usage Date': 'min',  # Get the earliest usage date
        'package': 'count'  # Count occurrences across files
    }).rename(columns={'package': 'Usage Count'}).reset_index()

    print(package_df)
    package_df.to_csv('pythonic_journey.csv', index=False)
    print(f"Total Files: {len(df)}")
    print(f"Total Lines of Code: {df['total_lines_of_code'].sum()}")
else:
    print("No data to display.")
