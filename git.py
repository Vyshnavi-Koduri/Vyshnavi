import os
import git
import requests
import shutil
from tqdm import tqdm

def search_github_rtl_repos(query="verilog vhdl -test -tb -sim", num_repos=5):
    """
    Searches GitHub for repositories containing RTL code.
    The query is refined to exclude repositories with keywords like "test", "tb", and "sim".
    """
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page={num_repos}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [repo["clone_url"] for repo in response.json().get("items", [])]
    else:
        print("GitHub API request failed.")
        return []

def is_useful_rtl_file(filepath):
    """
    Determines if a file is likely to be useful RTL code.
    Filters out files based on filename keywords and basic content checks.
    """
    filename = os.path.basename(filepath).lower()
    # Skip files whose names suggest they are testbenches, simulations, or non-synthesizable code.
    if any(substr in filename for substr in ["tb", "testbench", "dummy", "sim", "glbl", "blackbox"]):
        return False
    try:
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()
            # Check for typical RTL keywords
            if "module" in content or "entity" in content:
                return True
            else:
                return False
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return False

def clone_and_extract_rtl(repo_url, dataset_path="rtl_dataset"):
    """
    Clones a repository, then searches for RTL files (.v, .sv, .vhdl, .vhd) within it.
    Only files that pass the is_useful_rtl_file() filter are copied to the dataset_path.
    """
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    temp_repo_path = os.path.join("temp_repos", repo_name)
    os.makedirs(temp_repo_path, exist_ok=True)
    
    try:
        print(f"Cloning repository: {repo_name}")
        git.Repo.clone_from(repo_url, temp_repo_path)
        for root, _, files in os.walk(temp_repo_path):
            for file in files:
                if file.endswith(('.v', '.sv', '.vhdl', '.vhd')):
                    full_path = os.path.join(root, file)
                    if is_useful_rtl_file(full_path):
                        os.makedirs(dataset_path, exist_ok=True)
                        shutil.copy(full_path, dataset_path)
                        print(f"  Copied: {file}")
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
