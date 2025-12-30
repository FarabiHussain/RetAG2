# updater_worker.py

import argparse
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path


def wait_for_pid_exit(pid: int, timeout_sec: int = 60):
    """
    Wait until a process with PID is gone.
    """
    start = time.time()
    while True:
        # tasklist returns non-zero when PID doesn't exist
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)

        if str(pid) not in r.stdout:
            return True

        if time.time() - start > timeout_sec:
            return False

        time.sleep(0.5)


def extract_zip(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)


def find_extracted_root(extract_dir: Path) -> Path:
    """
    If zip has a single top folder, return it; otherwise return extract_dir.
    """
    entries = [
        p
        for p in extract_dir.iterdir()
        if p.name not in ("__MACOSX",) and not p.name.startswith(".")
    ]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_dir


def overwrite_copy(src_dir: Path, dst_dir: Path, exclude_names: set[str] | None = None):
    exclude_names = exclude_names or set()

    for item in src_dir.iterdir():
        if item.name in exclude_names:
            continue

        dst_item = dst_dir / item.name

        if item.is_dir():
            if dst_item.exists():
                shutil.rmtree(dst_item)
            shutil.copytree(item, dst_item)
        else:
            dst_item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst_item)


def apply_update(zip_path: Path, target_dir: Path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        extract_zip(zip_path, tmp_path)
        extracted_root = find_extracted_root(tmp_path)

        # Avoid clobbering updater itself if it lives in the same folder
        exclude = {"Updater.exe", "updater.exe", "updater_worker.py", "updater_worker.exe"}  # add more if needed

        overwrite_copy(extracted_root, target_dir, exclude_names=exclude)


def restart_app(restart_cmd: str, target_dir: Path):
    """
    restart_cmd can be:
      - path to exe
      - or a full command string
    """
    # If restart_cmd is a path relative to target_dir, fix it
    cmd_path = Path(restart_cmd)
    if cmd_path.exists() is False:
        maybe = target_dir / restart_cmd
        if maybe.exists():
            restart_cmd = str(maybe)

    # If it's a .py file, run with python
    if restart_cmd.lower().endswith(".py"):
        subprocess.Popen(["python", restart_cmd], cwd=str(target_dir))
    else:
        subprocess.Popen([restart_cmd], cwd=str(target_dir))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pid", type=int, required=True)
    p.add_argument("--zip", type=str, required=True)
    p.add_argument("--target", type=str, required=True)
    p.add_argument("--restart", type=str, required=True)
    p.add_argument("--wait", type=int, default=120)  # seconds
    args = p.parse_args()

    pid = args.pid
    zip_path = Path(args.zip).resolve()
    target_dir = Path(args.target).resolve()

    # Wait for main app to exit
    ok = wait_for_pid_exit(pid, timeout_sec=args.wait)
    if not ok:
        # Hard fail: don't half-update a running app
        return

    # Apply update
    apply_update(zip_path, target_dir)

    # cleanup downloads folder
    downloads_dir = Path(target_dir) / "downloads"
    try:
        if downloads_dir.exists():
            shutil.rmtree(downloads_dir)
            print(f"Deleted: {downloads_dir}", flush=True)
    except Exception as e:
        print(f"Failed to delete {downloads_dir}: {e}", flush=True)

    restart_app(args.restart, target_dir)

    # Restart app
    restart_app(args.restart, target_dir)


if __name__ == "__main__":
    print("Updating RETAG2...")
    main()
