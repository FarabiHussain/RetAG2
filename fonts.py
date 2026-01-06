from ctypes import windll, byref, create_unicode_buffer
import shutil
import winreg
from pathlib import Path

FR_PRIVATE  = 0x10
FR_NOT_ENUM = 0x20

USER_FONTS_REG = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"

FONT_FILES = {
    "Roboto Condensed Regular.ttf",
    "Roboto Condensed Medium.ttf",
    "Roboto Condensed Bold.ttf",
}


def _get_user_font_paths():
    paths = set()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, USER_FONTS_REG) as key:
            i = 0
            while True:
                try:
                    _, value, _ = winreg.EnumValue(key, i)
                    paths.add(str(value).lower())
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass

    return paths


def _install_roboto_condensed_if_missing():
    assets_fonts = Path.cwd() / "assets" / "fonts"

    if not assets_fonts.exists():
        raise FileNotFoundError(f"Missing fonts directory: {assets_fonts}")

    user_fonts_dir = (
        Path.home()
        / "AppData"
        / "Local"
        / "Microsoft"
        / "Windows"
        / "Fonts"
    )
    user_fonts_dir.mkdir(parents=True, exist_ok=True)

    installed_paths = _get_user_font_paths()

    for font_path in assets_fonts.glob("*.ttf"):
        dst = user_fonts_dir / font_path.name

        # skip if already installed
        if dst.exists() or str(dst).lower() in installed_paths:
            continue

        shutil.copy2(font_path, dst)

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            USER_FONTS_REG,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(
                key,
                font_path.stem,
                0,
                winreg.REG_SZ,
                str(dst)
            )


def loadfont(fontpath, private=True, enumerable=False):
    _install_roboto_condensed_if_missing()

    if not isinstance(fontpath, str):
        raise TypeError("fontpath must be a str in Python 3")

    AddFontResourceExW = windll.gdi32.AddFontResourceExW
    pathbuf = create_unicode_buffer(fontpath)

    flags = (FR_PRIVATE if private else 0) | (0 if enumerable else FR_NOT_ENUM)

    num_fonts_added = AddFontResourceExW(byref(pathbuf), flags, 0)
    return bool(num_fonts_added)