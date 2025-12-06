from __future__ import annotations

import os, sys, re, datetime as dt
from pathlib import Path
import threading

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
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:x:/g/personal/farabi_amcaim_ca/EXF65r3c07xJr_RCaGRvM1EBkRbBkCpdSXiynQswaBsCbw?e=7Wtxi5&download=1",
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
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:w:/g/personal/farabi_amcaim_ca/ET6sZyLyheRAhUUpB0cRDZIBFhcRRLcq3YKndc8JFRc6Zg?e=Sxhb7W&download=1",
        "ext": "docx",
    },
    "Study Permit": {
        "downloadUrl": "https://netorg5734909-my.sharepoint.com/:w:/g/personal/farabi_amcaim_ca/ET6sZyLyheRAhUUpB0cRDZIBFhcRRLcq3YKndc8JFRc6Zg?e=Sxhb7W&download=1",
        "ext": "docx",
    },
}

# IMM / supporting-doc URLs
URL_1344 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/EfWJwUl5kGxGngogRZUnnEsB-FJo6BwYJ4tKE_lAWbXsAw?e=77vbnb&download=1"
URL_5532 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/EXNqmnRsL8xBjF0JmPYGYq0Bhd8QDo5hw0JxVN3OrZ-KiA?e=B7ABEc&download=1"
URL_5476 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/IQDOCH5-_XuTTZtx3RFsXvEHAZ29084N1ktSuy1dj5shNc0?e=wcD0GF&download=1"
URL_5707 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/Eb-mrEba-qtBut_2PWOpU4kBa1MxrT2PnpjFf0c8N3eyNA?e=kOulpc&download=1"
URL_5709 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/EdOjB1t6_4NOhZaxWXVfp6kBtRmv1GaAnZ5TpI1W2t3CmQ?e=OAQwhK&download=1"
URL_5710 = "https://netorg5734909-my.sharepoint.com/:b:/g/personal/farabi_amcaim_ca/EdrIxBtsY-pDo0hvPOEYrdYBYCjZx8Odv1zqP_x12SIYeA?e=YACkO5&download=1"
URL_PHOTOS = "https://netorg5734909-my.sharepoint.com/:w:/g/personal/farabi_amcaim_ca/EX23P6Z_QZNKkgLkTlXzDKMBhEW2b-DzK4PB8CTJX5Vf9w?e=h1scjz&download=1"
SPONSOR_SHEET_URL = "https://netorg5734909-my.sharepoint.c...wKC7NgCdKkxnA2USM4A8BkE_6OxqTU0seo6_B0vEEUw?e=YNkLc3&download=1"


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
    # print(f">>> downloading {str(out_path).split('\\')[-1]}")
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


def spreadsheet_assistant(components) -> None:

    applications = []
    date_stamp = dt.datetime.now().strftime("%Y.%m.%d")

    for i in range(10):
        curr_application = {}
        is_valid_name = False
        is_valid_app_type = False

        curr_applicant = "Principal applicant" if i == 0 else f"Dependent {i}"

        if components[f"{curr_applicant} name"].get().strip() != "":
            is_valid_name = True
            curr_application["name"] = components[f"{curr_applicant} name"].get().strip()
        else:
            continue

        if components[f"{curr_applicant} application"].get().lower() in ["pr", "sponsorship", "express entry profile", "mpnp", "work permit", "study permit"]:
            is_valid_app_type = True
            curr_application["type"] = components[f"{curr_applicant} application"].get().strip()

        if is_valid_name and is_valid_app_type:
            applications.append(curr_application) 

    # create the target folder using PA's name in the format: "Last Name - First Name"
    target_folder = create_target_folder(applications[0]["name"])

    console_messages = []

    for application in applications:
        application_type = application["type"]
        nomalized_name = normalize_last_first(application['name'])

        # Download principal info sheet
        info_name = f"_{nomalized_name}_{application['type']}_{date_stamp}.{TYPE_CHOICES[application_type]['ext']}"
        info_path = target_folder / info_name

        progress_console = components['progress output']

        console_messages.append(f">>> downloading info sheet for {nomalized_name}")
        download_file(TYPE_CHOICES.get(application_type).get("downloadUrl"), info_path)
        download_file(URL_5476, target_folder / f"{nomalized_name} - imm5476.pdf")

        if application['type'].lower() == "work permit":
            download_file(URL_5710, target_folder / f"{nomalized_name} - imm5710.pdf")
            console_messages.append(f">>> downloading imm5710 for {nomalized_name}")
            download_file(URL_5707, target_folder / f"{nomalized_name} - imm5707.pdf")
            console_messages.append(f">>> downloading imm5707 for {nomalized_name}")
        elif application['type'].lower() == "study permit":
            download_file(URL_5709, target_folder / f"{nomalized_name} - imm5709.pdf")
            console_messages.append(f">>> downloading imm5709 for {nomalized_name}")
        elif application['type'].lower() == "sponsorship":
            download_file(URL_5532, target_folder / f"{nomalized_name} - imm5532.pdf")
            console_messages.append(f">>> downloading imm5532 for {nomalized_name}")
            download_file(URL_1344, target_folder / f"{nomalized_name} - imm1344.pdf")
            console_messages.append(f">>> downloading imm1344 for {nomalized_name}")
            download_file(URL_PHOTOS,target_folder / f"{nomalized_name} - Proof of Relationship to Sponsor - Relationship Photos.docx")
            console_messages.append(f">>> downloading Proof of Relationship to Sponsor - Relationship Photos for {nomalized_name}")
            sponsor_out = target_folder / f"_{normalize_last_first(applications[0]['name'])}_SPNSR_{date_stamp}.xlsx"
            print(f">>> downloading info sheet for sponsor, {normalize_last_first(applications[0]['name'])}")
            download_file(SPONSOR_SHEET_URL, sponsor_out)

    progress_console.set("\n".join(console_messages))

    try:
        if os.name == "nt":
            os.startfile(target_folder)  # type: ignore[attr-defined]
    except Exception:
        pass
