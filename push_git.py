import os
import subprocess
from time import sleep

repo_path = r"D:\Github Doc\AstrBotLauncher"
files_per_batch = 50
branch = "master"

os.chdir(repo_path)

def run(cmd_list):
    result = subprocess.run(cmd_list, capture_output=True, text=True, shell=False)
    cmd_str = " ".join(cmd_list)
    if result.returncode != 0:
        print(f"[ERROR] {cmd_str}\n{result.stderr}")
    else:
        print(f"[OK] {cmd_str}\n{result.stdout}")
    return result.stdout.strip()

def get_changed_files():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, shell=False
    )
    lines = result.stdout.splitlines()
    files = []
    for line in lines:
        path = line[3:]
        files.append(path)
    return files

def split_batches(files, batch_size):
    for i in range(0, len(files), batch_size):
        yield files[i:i+batch_size]

def main():
    all_files = get_changed_files()
    if not all_files:
        print("✅ No files to commit.")
        return

    print(f"📦 Found {len(all_files)} changed/untracked files.")

    for i, batch in enumerate(split_batches(all_files, files_per_batch), 1):
        print(f"\n🚀 Processing batch {i} with {len(batch)} files...")
        for file in batch:
            run(["git", "add", file])
        run(["git", "commit", "-m", f"Auto batch commit {i}"])
        run(["git", "push", "origin", branch])
        sleep(1)

    print("\n✅ All batches pushed.")

if __name__ == "__main__":
    main()
