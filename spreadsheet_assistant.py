from __future__ import annotations
import os, sys, re, datetime as dt
from pathlib import Path
import globals
from Database import Mongo

try:
    import requests
except ImportError:
    print("This script requires 'requests'. Install with: pip install requests")
    sys.exit(1)


# Main per-type download URL (info sheet), extension, and typeName.
TYPE_CHOICES = {
    "PR": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:x:/g/personal/farabi_amcaim_ca/IQBxeua93NO8Sa_0QmhkbzNRAX0oHCBgEu3MQ1_tx3aDFV0?e=DYPran&download=1",
        "ext": "xlsx",
    },
    "Sponsorship": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:x:/g/personal/farabi_amcaim_ca/IQDdMCguzYAnSpMZwNlEjOAPAaT6hYGmPjJiH4V3sFE2I1k?e=YyJwyP&download=1",
        "ext": "xlsx",
    },
    "Express Entry Profile": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:x:/g/personal/farabi_amcaim_ca/Eb1F4IL-uydLvVM2iTAWVGgBzmhHiEA8bxjvjc7JLuF4LA?e=x1p5gE&download=1",
        "ext": "xlsx",
    },
    "MPNP": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:x:/g/personal/farabi_amcaim_ca/EW-tGeYtpftOtMvfZe9OJQABZktOPrMd3dQZ7r_8YP1S0g?e=H6Nw6X&download=1",
        "ext": "xlsx",
    },
    "Work Permit": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:w:/g/personal/farabi_amcaim_ca/IQCxEz6QzvDPS5LDsP6TL10KAZXkvw15RHHha0njwhp50E0?e=CCvP6J&download=1",
        "ext": "docx",
    },
    "Study Permit": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:w:/g/personal/farabi_amcaim_ca/IQDWWELv1zpiS5u7yeLJlBdJAbrjJXILREPChhWhr9sLISs?e=IfPLrb&download=1",
        "ext": "docx",
    },
}


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Replace invalid filename characters with `replacement`.

    Targets Windows-invalid characters: <>:"/\\|?* and ASCII control chars.
    Also collapses runs of replacements and trims trailing dots/spaces
    (to avoid Windows path issues).
    """
    if name is None:
        return ""

    # 1) Replace invalid chars + control chars
    invalid = r'[<>:"/\\|?*\x00-\x1F]'
    cleaned = re.sub(invalid, replacement, str(name))

    # 2) Collapse multiple replacements into one
    rep_esc = re.escape(replacement)
    cleaned = re.sub(rf"{rep_esc}+", replacement, cleaned)

    # 3) Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    # 4) Windows also disallows trailing dots/spaces
    cleaned = cleaned.rstrip(" .")

    # 5) Avoid empty result
    return cleaned or "untitled"


def download_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def normalize_last_first(name: str) -> str:
    parts = re.split(r"\s+", name.strip())
    if len(parts) > 1:
        last = parts[-1]
        first = " ".join(parts[:-1])
        return f"{last} - {first}"
    return parts[0] if parts else name.strip()


def get_downloads_dir() -> Path:
    # Mirrors PS behavior: UserProfile\Downloads on Windows; best-effort elsewhere.
    home = Path.home()
    downloads = home / "Downloads"
    return downloads


def create_target_folder(principal_name: str) -> Path:
    normalized_name = normalize_last_first(principal_name)
    folder_name = f"{normalized_name}"
    target_folder = get_downloads_dir() / folder_name
    target_folder.mkdir(parents=True, exist_ok=True)
    return target_folder


def prompt_int(prompt: str) -> int:
    raw = input(prompt).strip()
    try:
        return int(raw)
    except ValueError:
        print("Invalid number entered. Exiting.")
        sys.exit(1)


def print_title() -> None:
    os.system("cls")
    print(
        r"""
____ ___  ____ ____ ____ ___  ____ _  _ ____ ____ ___
[__  |__] |__/ |___ |__| |  \ [__  |__| |___ |___  |
___] |    |  \ |___ |  | |__/ ___] |  | |___ |___  |
____ ____ ____ _ ____ ___ ____ _  _ ___
|__| [__  [__  | [__   |  |__| |\ |  |
|  | ___] ___] | ___]  |  |  | | \|  |   [2025.12.02]
_____________________________________________________

"""
    )


def print_application_options(applicant_number) -> None:
    print(
        f"""Select the application type for {"principal applicant" if applicant_number == 0 else (f"applicant #{applicant_number + 1}")}:
    1. PR application
    2. Sponsorship application
    3. Express Entry application
    4. MPNP application
    5. Work Permit application
    6. Study Permit application
        """
    )


def print_applications_list(applications, title_width=53):
    if not applications:
        print("No applications.")
        return

    inner_width = title_width - 2          # between '+' borders
    content_width = inner_width - 2        # leave 1 space padding on each side
    sep_total = 6                         # " | " twice

    idx_width = len(str(len(applications)))
    app_width = max(len("Application"), max(len(a.get("typeName", "")) for a in applications))

    # Name gets the rest (within content_width)
    name_width = content_width - idx_width - sep_total - app_width
    if name_width < len("Name"):
        name_width = len("Name")
        app_width = content_width - idx_width - sep_total - name_width
        app_width = max(app_width, len("Application"))

    def trunc(s, w):
        s = str(s)
        if len(s) <= w:
            return s
        if w <= 3:
            return "." * w
        return s[:w - 3] + "..."

    def make_row(idx, name, app):
        core = f"{idx:>{idx_width}} | {name:<{name_width}} | {app:<{app_width}}"
        # core must be exactly content_width
        if len(core) < content_width:
            core += " " * (content_width - len(core))
        else:
            core = core[:content_width]
        return f"| {core} |"  # adds 1 space each side, total length stays inner_width+2

    border = "+" + "-" * inner_width + "+"

    print(border)
    print(make_row("#", "Name", "Application"))
    print(border)

    for i, a in enumerate(applications, start=1):
        name = trunc(a.get("name", ""), name_width)
        app = trunc(a.get("type", ""), app_width)
        print(make_row(i, name, app))

    print(border + "\n")


def spreadsheet_assistant(components, root) -> None:
    import threading
    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(root, opacity=1.0, splash_text="starting downloads", text_size=70)

    # Start downloads in background
    def start_worker():
        threading.Thread(
            target=_spreadsheet_worker,
            args=(components, loadingsplash),
            daemon=True
        ).start()

    loadingsplash.show(task=start_worker)

def _spreadsheet_worker(components, loadingsplash):
    try:
        console_messages = []

        applications = []
        date_stamp = dt.datetime.now().strftime("%Y.%m.%d")

        for i in range(10):
            curr_application = {}
            curr_applicant = "Principal applicant" if i == 0 else f"Dependent {i}"

            name = components[f"{curr_applicant} name"].get().strip()
            if not name:
                continue

            app_type = components[f"{curr_applicant} application"].get().strip()
            if app_type.lower() not in ["pr", "sponsorship", "express entry profile", "mpnp", "work permit", "study permit"]:
                continue

            curr_application["name"] = name
            curr_application["type"] = app_type
            applications.append(curr_application)

        if not applications:
            return

        target_folder = create_target_folder(applications[0]["name"])

        db = Mongo()
        dbname = db.get_database()
        collection_name = dbname["links"]
        entries = collection_name.find()

        for row in entries:
            url = row['url']
            globals.links_dict[row['form']] = (url + "&download=1") if not url.endswith("&download=1") else url

        links = globals.links_dict

        for index, application in enumerate(applications):
            application_type = application["type"]
            normalized_name = normalize_last_first(application['name'])

            if index == 0 and application['type'].lower() == "sponsorship":
                application_type = "PR"

            info_name = f"_{normalized_name}_{application['type']}_{date_stamp}.{TYPE_CHOICES[application_type]['ext']}"
            info_path = target_folder / info_name

            console_messages.append(f">>> downloaded info sheet for {normalized_name}")
            download_file(TYPE_CHOICES[application_type]["downloadUrl"], info_path)

            download_file(links["5476"], target_folder / f"{normalized_name} - imm5476.pdf")

            if application['type'].lower() == "work permit":
                download_file(links["5710"], target_folder / f"{normalized_name} - imm5710.pdf")
                console_messages.append(f">>> downloaded imm5710 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm5710 for\n{normalized_name}", text_size=70)

                download_file(links["5707"], target_folder / f"{normalized_name} - imm5707.pdf")
                console_messages.append(f">>> downloaded imm5707 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm5707 for\n{normalized_name}", text_size=70)

            elif application['type'].lower() == "study permit":
                download_file(links["5709"], target_folder / f"{normalized_name} - imm5709.pdf")
                console_messages.append(f">>> downloaded imm5709 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm5709 for\n{normalized_name}", text_size=70)
                download_file(links["5645"], target_folder / f"{normalized_name} - imm5645.pdf")
                console_messages.append(f">>> downloaded imm5645 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm5645 for\n{normalized_name}", text_size=70)

            elif application['type'].lower() == "sponsorship" and index == 1:
                download_file(links["5532"], target_folder / f"{normalized_name} - imm5532.pdf")
                console_messages.append(f">>> downloaded imm5532 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm5532 for\n{normalized_name}", text_size=70)

                download_file(links["1344"], target_folder / f"{normalized_name} - imm1344.pdf")
                console_messages.append(f">>> downloaded imm1344 for {normalized_name}")
                loadingsplash.set_splash_text(f"imm1344 for\n{normalized_name}", text_size=70)

                download_file(links["photos"], target_folder / f"{normalized_name} - Proof of Relationship to Sponsor - Relationship Photos.docx")
                console_messages.append(f">>> downloaded Relationship Photos for {normalized_name}")
                loadingsplash.set_splash_text(f"Relationship Photos for\n{normalized_name}", text_size=70)

        components['progress output'].set("\n".join(console_messages))

        try:
            # popup.after(0, popup.destroy)
            loadingsplash.stop()

            if os.name == "nt":
                os.startfile(target_folder)
        except Exception:
            pass

    except Exception as e:
        # Ensure popup closes even on error
        # popup.after(0, lambda: popup.destroy())
        loadingsplash.stop()
        raise
