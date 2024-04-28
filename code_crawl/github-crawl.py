import os
import json
from datetime import datetime
import pandas as pd
import requests

def extract_metadata(file_content, file_path, commit_date):
    try:
        return process_file(file_content, file_path, commit_date)
    except json.JSONDecodeError:
        return None

def process_file(file_content, file_path, commit_date):
    if file_path.endswith('.ipynb'):
        notebook = json.loads(file_content)
        return extract_ipynb_metadata(notebook, file_path, commit_date)
    elif file_path.endswith('.py'):
        lines = file_content.split('\n')
        return extract_py_metadata(lines, file_path, commit_date)

def extract_ipynb_metadata(notebook, file_path, commit_date):
    metadata = initialize_metadata(file_path, commit_date)
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            update_code_cell_metadata(cell, metadata)
        elif cell['cell_type'] == 'markdown':
            metadata['num_markdown_cells'] += 1
    return finalize_metadata(metadata)

def extract_py_metadata(lines, file_path, commit_date):
    metadata = initialize_metadata(file_path, commit_date)
    for line in lines:
        update_line_metadata(line, metadata, commit_date)
    return finalize_metadata(metadata)

def initialize_metadata(file_path, commit_date):
    return {
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'commit_date': commit_date,
        'packages_used': set(),
        'first_used_date': {},
        'num_code_cells': 0,
        'num_markdown_cells': 0,
        'total_lines_of_code': 0
    }

def update_code_cell_metadata(cell, metadata):
    metadata['num_code_cells'] += 1
    metadata['total_lines_of_code'] += sum(1 for line in cell['source'] if line.strip() and not line.strip().startswith('#'))
    for line in cell['source']:
        update_line_metadata(line, metadata, metadata['commit_date'])

def update_line_metadata(line, metadata, file_created_date=None):
    if line.startswith('import ') or line.startswith('from '):
        package = line.split()[1].split('.')[0]
        metadata['packages_used'].add(package)
        if package not in metadata['first_used_date']:
            metadata['first_used_date'][package] = file_created_date or metadata['commit_date']
        else:
            existing_date = datetime.strptime(metadata['first_used_date'][package], '%Y-%m-%d')
            current_date = datetime.strptime(file_created_date or metadata['commit_date'], '%Y-%m-%d')
            if current_date < existing_date:
                metadata['first_used_date'][package] = file_created_date or metadata['commit_date']

def finalize_metadata(metadata):
    packages_info = [{'package': pkg, 'first_used_date': metadata['first_used_date'][pkg]} for pkg in sorted(metadata['packages_used'])]
    metadata['packages_info'] = packages_info
    del metadata['packages_used']
    del metadata['first_used_date']
    return metadata

def crawl_github_repos(username, access_token):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    repos = response.json()
    file_metadata = []
    for repo in repos:
        repo_name = repo['name']
        default_branch = repo['default_branch']
        repo_url = f"https://api.github.com/repos/{username}/{repo_name}/git/trees/{default_branch}?recursive=1"
        repo_response = requests.get(repo_url, headers=headers)
        repo_tree = repo_response.json()
        if 'tree' in repo_tree:
            for item in repo_tree['tree']:
                if item['type'] == 'blob' and (item['path'].endswith('.ipynb') or item['path'].endswith('.py')):
                    file_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?path={item['path']}&page=1&per_page=1"
                    file_response = requests.get(file_url, headers=headers)
                    commits = file_response.json()
                    if commits:
                        commit_date = commits[-1]['commit']['author']['date'][:10]  # Extract the date portion of the first commit
                        file_content_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/{item['path']}"
                        file_content_response = requests.get(file_content_url)
                        file_content = file_content_response.text
                        metadata = extract_metadata(file_content, item['path'], commit_date)
                        if metadata:
                            file_metadata.append(metadata)
        else:
            print(f"Skipping repository '{repo_name}' due to missing 'tree' key in the API response.")
    return file_metadata

# Replace with your GitHub username and access token
github_username = "bme3412"
github_access_token = "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"

metadata_list = crawl_github_repos(github_username, github_access_token)
all_packages_info = []
for metadata in metadata_list:
    for package_info in metadata['packages_info']:
        package_info.update({key: metadata[key] for key in metadata if key not in ['packages_info']})
        all_packages_info.append(package_info)

df = pd.DataFrame(all_packages_info)

if not df.empty:
    df['First Usage Date'] = pd.to_datetime(df['first_used_date'], errors='coerce')
    package_df = df.groupby('package').agg({
        'First Usage Date': 'min',
        'package': 'count'
    }).rename(columns={'package': 'Usage Count'}).reset_index()

    print(package_df)
    package_df.to_csv('github_pythonic_journey.csv', index=False)
    print(f"Total Files: {len(df)}")
    print(f"Total Lines of Code: {df['total_lines_of_code'].sum()}")
else:
    print("No data to display.")