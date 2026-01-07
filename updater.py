# updater.py
import os
import json
import re
import requests
import webbrowser
from icecream import ic
from pathlib import Path
from packaging.version import Version, InvalidVersion

OWNER = "FarabiHussain"
REPO = "RetAG2"
API_LATEST = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

# Optional token: set env var GITHUB_TOKEN to avoid rate limits
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

CACHE_FILE = Path("update_cache.json")


def _headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def _normalize_tag(tag: str) -> str:
    # Keep your current scheme "vX.Y.Z"
    # packaging.version accepts "2.1.18" better than "v2.1.18"
    return tag.lstrip("vV").strip()


def _parse_version(tag: str) -> Version:
    return Version(_normalize_tag(tag))


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache: dict):
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    except Exception:
        pass


def _get_latest_release(current_version: str) -> dict:
    """
    Returns:
    {
        "ok": bool,
        "update_available": bool,
        "latest_tag": str|None,
        "release_url": str|None,
        "assets": list[(name,url)],
        "error": str|None,
    }
    """
    cache = load_cache()
    etag = cache.get("etag")

    headers = _headers()
    if etag:
        headers["If-None-Match"] = etag

    try:
        r = requests.get(API_LATEST, headers=headers, timeout=10)

        # If unchanged since last check
        if r.status_code == 304 and "latest" in cache:
            data = cache["latest"]

            # If cached assets are empty, force a refresh in case assets were added
            if not data.get("assets"):
                r = requests.get(API_LATEST, headers=_headers(), timeout=10)
                r.raise_for_status()
                data = r.json()
        else:
            if r.status_code == 404:
                return {
                    "ok": False,
                    "update_available": False,
                    "latest_tag": None,
                    "release_url": None,
                    "assets": [],
                    "error": "No GitHub Releases found (publish a Release first)."
                }

            r.raise_for_status()
            data = r.json()

            # Save new ETag + payload
            cache["etag"] = r.headers.get("ETag")
            cache["latest"] = data
            save_cache(cache)

        latest_tag = data.get("tag_name")
        release_url = data.get("html_url")
        assets = [(a["name"], a["browser_download_url"]) for a in data.get("assets", [])]

        # Compare versions
        try:
            current_v = _parse_version(current_version)
            latest_v = _parse_version(latest_tag)
        except (InvalidVersion, TypeError):
            # If versions are not semver-compliant, fall back to tag string compare (less reliable)
            current_v = None
            latest_v = None

        if current_v and latest_v:
            update_available = latest_v > current_v
        else:
            update_available = (latest_tag != current_version)

        return {
            "ok": True,
            "update_available": update_available,
            "latest_tag": latest_tag,
            "release_url": release_url,
            "assets": assets,
            "error": None
        }

    except Exception as e:
        return {
            "ok": False,
            "update_available": False,
            "latest_tag": None,
            "release_url": None,
            "assets": [],
            "error": str(e)
        }


def open_release_page(url: str):
    if url:
        webbrowser.open(url)


def _download_asset(url: str, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers = _headers()
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return out_path


def _download_update(result: dict):
    # - surrounding single quotes REQUIRED
    # - leading v optional, any case
    # - each numeric section is 1 or 2 digits

    zip_name_re = re.compile(r"[vV]?\d{1,2}\.\d{1,2}\.\d{1,2}\.zip")

    for name, url in result["assets"]:
        ic(name, url)
        match = zip_name_re.match(name)

        if match:
            path = _download_asset(url, f"downloads/{name}")
            print("Downloaded to:", path)
            return path

    raise RuntimeError("No matching .zip asset found.")


def search_update_on_startup(app):
    import subprocess

    # check for updates before querying attendance
    latest_release = (_get_latest_release(app.version))

    if not latest_release["update_available"]:
        print("on latest version")
        return

    try:
        if latest_release["update_available"]:
            subprocess.Popen(
                ["cmd.exe", "/k", "echo RETAG2 Update found. Downloading update. Do not attempt to open RETAG. It will open after updating & ping -n 6 127.0.0.1 >nul & exit"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            target_dir = Path(os.getcwd()).resolve()
            updater_exe = (target_dir / "Updater.exe").resolve()
            restart_target = "RETAG2.exe"
            pid = os.getpid()

            if not updater_exe.exists():
                raise FileNotFoundError(f"{updater_exe} not found")

            zip_path = Path(_download_update(latest_release)).resolve()

            if zip_path.exists():
                subprocess.Popen(
                    [
                        str(updater_exe),
                        "--pid", str(pid),
                        "--zip", str(zip_path),
                        "--target", str(target_dir),
                        "--restart", str(restart_target),
                        "--wait", "180",
                    ],
                    cwd=str(target_dir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )

                app.root.destroy()
                raise SystemExit

            else:
                print(f"`{zip_path}` does not exist")
    except Exception as e:
        print(e)


def swap_updater_if_present():
    target_dir = Path(os.getcwd()).resolve()

    new_updater = target_dir / "Updater.new.exe"
    updater = target_dir / "Updater.exe"
    old_updater  = target_dir / "Updater.old.exe"
    print(f"searching for ```{new_updater}```")

    if not new_updater.exists():
        return

    try:
        # Remove any previous old updater
        if old_updater.exists():
            old_updater.unlink()

        # Replace Updater.exe with Updater.new.exe (keep a temporary backup)
        if updater.exists():
            updater.replace(old_updater)

        new_updater.replace(updater)

        # If we got here, the swap worked. Delete the backup.
        if old_updater.exists():
            old_updater.unlink()

        print("Updater updated.", flush=True)
    except Exception as e:
        print(f"Failed to update Updater.exe: {e}", flush=True)
