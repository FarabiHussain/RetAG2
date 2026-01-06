from __future__ import annotations
from pathlib import Path
import webbrowser
from icecream import ic
import os, re, datetime as dt, requests
from Popups import PromptPopup
import globals, calendar
import requests


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


def _get_latest_form_version(form_number: str, new_versions_found: list) -> dict:

    # Only process IMM forms, rest will throw errors as the link would be invalid and not found on IRCC site
    if not form_number.startswith("imm"):
        return

    # Avoid duplicate popups for the same form in one session
    if form_number in new_versions_found:
        return

    from Popups import InfoPopup
    from bs4 import BeautifulSoup

    BASE = "https://www.canada.ca/en/immigration-refugees-citizenship/services/application/application-forms-guides/"

    r = requests.get(f"{BASE}{form_number}.html", timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    # Look for "A new version of this form is available ..."
    m = re.search(r"A new version of this form is available\s*\((\d{2}-\d{4})\)", text)
    version = m.group(1) if m else None

    if not version:
        m2 = re.search(r"Last updated:\s*([A-Za-z]+)\s+(\d{4})", text)
        month_name, year = m2.group(1), m2.group(2)
        month_num = list(calendar.month_name).index(month_name)   # "November" -> 11
        mm_yyyy = f"{month_num:02d}-{year}"                       # "11-2025"
        version = mm_yyyy if mm_yyyy else None
    else:
        new_versions_found.append(form_number)

        if PromptPopup(f"A new version of form {form_number} ({version}) is currently available.\n\nPlease ensure you download the latest version from the IRCC website. Would you like to open the form page now?").get():
            webbrowser.open(f"{BASE}{form_number}.html")

    # Find the PDF link
    pdf_link = None
    for a in soup.find_all("a", href=True):
        if "PDF" in a.get_text(strip=True).upper() or a["href"].lower().endswith(".pdf"):
            href = a["href"]
            if form_number in href.lower():
                pdf_link = href if href.startswith("http") else "https://www.canada.ca" + href
                break

    return {
        "version": version,
        "pdf_link": pdf_link
    }


def _download_file(url: str, out_path: Path, normalized_name: str, form_name: str, console_messages: list, loadingsplash: None, new_versions_found: list) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _set_messages(normalized_name, form_name, console_messages, loadingsplash)

    _get_latest_form_version(form_name, new_versions_found)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def _set_messages(normalized_name: str, form_name: str, console_messages: list, loadingsplash: None) -> None:
    console_messages.append(f">>> downloaded {form_name} for {normalized_name}")
    loadingsplash.set_splash_text(f"{form_name} for\n{normalized_name}", 100)


def _sanitize_name(name: str, replacement: str = "_") -> str:
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


def _normalize_last_first(name: str) -> str:
    _sanitize_name(name)

    parts = re.split(r"\s+", name.strip())

    if len(parts) > 1:
        last = parts[-1]
        first = " ".join(parts[:-1])
        return f"{last} - {first}"

    return parts[0] if parts else name.strip()


def _get_downloads_dir() -> Path:
    # Mirrors PS behavior: UserProfile\Downloads on Windows; best-effort elsewhere.
    home = Path.home()
    downloads = home / "Downloads"

    return downloads


def _create_target_folder(principal_name: str) -> Path:
    normalized_name = _normalize_last_first(principal_name)
    folder_name = f"{normalized_name}"
    target_folder = _get_downloads_dir() / folder_name
    target_folder.mkdir(parents=True, exist_ok=True)

    return target_folder


def _retrieve_files_worker(components, loadingsplash):
    from Database import Database

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

        target_folder = _create_target_folder(applications[0]["name"])

        db = Database()
        dbname = db.get_database()
        collection_name = dbname["links"]
        entries = collection_name.find()

        new_versions_found = []

        for row in entries:
            url = row['url']
            globals.links_dict[row['form']] = (url + "&download=1") if not url.endswith("&download=1") else url

        links = globals.links_dict

        for index, application in enumerate(applications):
            application_type = application["type"]
            normalized_name = _normalize_last_first(application['name'])

            if index == 0 and application['type'].lower() == "sponsorship":
                application_type = "PR"

            info_name = f"_{normalized_name}_{application['type']}_{date_stamp}.{TYPE_CHOICES[application_type]['ext']}"
            _download_file(TYPE_CHOICES[application_type]["downloadUrl"], target_folder / info_name, normalized_name, "info sheet", console_messages, loadingsplash, new_versions_found)
            _download_file(links["5476"], target_folder / f"{normalized_name} - imm5476.pdf", normalized_name, "imm5476", console_messages, loadingsplash, new_versions_found)

            if application['type'].lower() == "work permit":
                _download_file(links["5710"], target_folder / f"{normalized_name} - imm5710.pdf", normalized_name, "imm5710", console_messages, loadingsplash, new_versions_found)
                _download_file(links["5707"], target_folder / f"{normalized_name} - imm5707.pdf", normalized_name, "imm5707", console_messages, loadingsplash, new_versions_found)

            elif application['type'].lower() == "study permit":
                _download_file(links["5709"], target_folder / f"{normalized_name} - imm5709.pdf", normalized_name, "imm5709", console_messages, loadingsplash, new_versions_found)
                _download_file(links["5645"], target_folder / f"{normalized_name} - imm5645.pdf", normalized_name, "imm5645", console_messages, loadingsplash, new_versions_found)

            elif application['type'].lower() == "sponsorship" and index == 1:
                _download_file(links["5532"], target_folder / f"{normalized_name} - imm5532.pdf", normalized_name, "imm5645", console_messages, loadingsplash, new_versions_found)
                _download_file(links["1344"], target_folder / f"{normalized_name} - imm1344.pdf", normalized_name, "imm5645", console_messages, loadingsplash, new_versions_found)
                _download_file(links["photos"], target_folder / f"{normalized_name} - Proof of Relationship to Sponsor - Relationship Photos.docx", normalized_name, "Relationship Photos", console_messages, loadingsplash, new_versions_found)

        components['progress output'].set("\n".join(console_messages))

        try:
            loadingsplash.stop()
            new_versions_found = []
            if os.name == "nt": os.startfile(target_folder)
        except Exception:
            pass

    except Exception as e:
        loadingsplash.stop()
        raise


def retrieve_files(components, root) -> None:
    import threading
    from GUI import LoadingSplash
    loadingsplash = LoadingSplash(root, opacity=1.0, splash_text="STARTING DOWNLOADS", text_size=100)

    # Start downloads in background
    def start_worker():
        threading.Thread(
            target=_retrieve_files_worker,
            args=(components, loadingsplash),
            daemon=True
        ).start()

    loadingsplash.show(task=start_worker)

