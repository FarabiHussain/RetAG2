import fileinput
import os
import glob
import shutil
import re
import sys
from datetime import datetime as dt
from subprocess import DEVNULL, STDOUT, check_call

# read the most recent version created
def get_version(cwd, ver):
    ver_log_dir = (cwd + '\\builder\\versions.log').replace('\\builder\\builder', '\\builder')

    try:
        with open(ver_log_dir, 'r') as log_file:
            latest = log_file.readlines()[-1]
            latest = latest.split("v")[1]
            latest = latest.split(".")

            ver = [
                str(latest[0]),
                str(latest[1]),
                str(latest[2]),
            ]

            ver[2] = "[" + ver[2] + "]"

            return ver

    except Exception as e:
        print(e)


# remove spaces and brackets
def unformat(formatted):
    return formatted.replace("]","").replace("[","").replace(" ","")


# clean up existing files
def cleanup(cwd, isInitial = False):
    if os.path.exists(cwd + "\\build"):
        shutil.rmtree(cwd + "\\build")

    if os.path.exists(cwd + "\\dist"):
        shutil.rmtree(cwd + "\\dist")

    if not os.path.exists(cwd + "\\releases"):
        os.makedirs(cwd + "\\releases")

    for f in glob.glob("*.spec"):
        os.remove(f)

    if isInitial:
        for f in glob.glob("v*.zip"):
            os.remove(f)


# pip install libs needed to build the app 
def install_dependencies():
    os.system('cls')

    libraries = [
        'pyinstaller', 
        'python-dateutil', 
        'python-docx', 
        'docx2pdf', 
        'customtkinter', 
        'CTkMessagebox', 
        'names', 
        'dotenv',
        'python-dotenv',
        'icecream',
    ]

    for library in libraries:
        print("installing dependency: " + library)
        check_call(['pip', 'install', library], stdout=DEVNULL, stderr=STDOUT)
    print("done")


# run the PyInstaller build command
def build_exe(cwd, ver):
    cleanup(cwd, isInitial = True)

    # build the exe from py files
    os.system("cls")
    print("building application exe...")
    check_call(['python', '-m', 'PyInstaller', 'main.py', '--noconsole', '--onefile', '-w', '--icon=' + cwd + '\\assets\\icons\\.ico', f'--name={((os.getcwd()).split("\\")[-1])}'], stdout=DEVNULL, stderr=STDOUT)
    print("building updater exe...")
    check_call(['python', '-m', 'PyInstaller', 'updater_worker.py', '--onefile', '-w', '--icon=' + cwd + '\\assets\\icons\\updater.ico', f'--name=Updater'], stderr=STDOUT)
    print("done")

    # after the exe is built, copy over the assets folder
    try:
        shutil.copytree(cwd + "\\assets\\", cwd + "\\dist\\assets\\")
    except: 
        print("could not copy assets folder")

    # zip the contents of the dist folder
    try:
        shutil.make_archive("v" + (".").join(ver), 'zip', cwd + "\\dist")
    except Exception as e: 
        print("could not zip dist folder: ", e)

    # move the created zip file into the releases folder
    try:
        filename = f"v{(".").join(ver)}.zip"
        for f in glob.glob(cwd + "\\releases\\" + filename):
            os.remove(f)
        for file in glob.glob(cwd + '\\v*.zip'):
            shutil.move(file, cwd + "\\releases")
    except Exception as e: 
        print("could not move zip file: ", e)

    # final cleanup of temporary files
    print("cleaning up...")
    cleanup(cwd, isInitial = False)
    print("done")

    # write the newest build to the log
    ver_log_dir = (cwd + '\\builder\\versions.log').replace('\\builder\\builder', '\\builder')

    with open(ver_log_dir, 'a') as log_file:
        log_file.write("\n[" + dt.now().strftime("%d/%m/%Y, %H:%M:%I" + "]\t") + "v" + (".").join(ver))

    output_dir = (cwd + "\\releases")
    os.startfile(f'{output_dir}\\{filename}')


# replace the app version in `variables.py` with the selected version 
def set_version(cwd, ver):
    variables_dir = (cwd + '\\App.py').replace('\\builder', '')
    print(variables_dir)
    version_regex = "v[0-9]+.[0-9]+.[0-9]+"

    # iterate through the file, attempt to find version_regex
    for line in fileinput.input(variables_dir, inplace=1):
        ver_match = re.search(version_regex, line)

        # if version_regex is found, replace it with the newly selected version number
        if (ver_match is not None):
            line = line.replace(ver_match.group(), f"v{(".").join(ver)}")

        # write all lines into file so that nothing else is changed
        sys.stdout.write(line)