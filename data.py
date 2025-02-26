import os
import git
import requests
import shutil
from tqdm import tqdm

def search_github_rtl_repos(query="verilog vhdl", num_repos=5):
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page={num_repos}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [repo["clone_url"] for repo in response.json().get("items", [])]
    else:
        print("GitHub API request failed.")
        return []

def clone_and_extract_rtl(repo_url, dataset_path="rtl_dataset"):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    temp_repo_path = os.path.join("temp_repos", repo_name)
    os.makedirs(temp_repo_path, exist_ok=True)
    
    try:
        git.Repo.clone_from(repo_url, temp_repo_path)
        for root, _, files in os.walk(temp_repo_path):
            for file in files:
                if file.endswith(('.v', '.sv', '.vhdl', '.vhd')):
                    os.makedirs(dataset_path, exist_ok=True)
                    shutil.copy(os.path.join(root, file), dataset_path)
        print(f"Extracted RTL files from {repo_name}.")
    except Exception as e:
        print(f"Error cloning {repo_name}: {e}")
    finally:
        shutil.rmtree(temp_repo_path, ignore_errors=True)

def main():
    repos = search_github_rtl_repos()
    if not repos:
        print("No repositories found.")
        return
    
    os.makedirs("rtl_dataset", exist_ok=True)
    for repo in tqdm(repos, desc="Cloning and Extracting RTL Files"):
        clone_and_extract_rtl(repo)
    print("RTL dataset collection completed.")

if __name__ == "__main__":
    main()
