import os
import msvcrt
from builder_utils import *

cwd = os.getcwd()
ver = ['0', '0', '0']
kb = None
cur = 2

ver = get_version(cwd, ver)
latest_build = unformat(ver[0]) + "." + unformat(ver[1]) + "." + unformat(ver[2])

# increment the patch number for the current build
ver[2] = "[" + str(int(unformat(ver[2])) + 1) + "]"

# install dependencies needed to build the file
if '--deps' in sys.argv:
    install_dependencies()

# skip the interface if not in args
if '--selector' not in sys.argv:
    for i in range(len(ver)):
        ver[i] = unformat(ver[i])

    set_version(cwd, ver)
    build_exe(cwd, ver)

else:
    while True:
        os.system('cls')

        print(
            ("Use 'a' and 'd' keys to navigate, 'w' and 's' to change version, 'e' to confirm, 'q' to quit.\n") +
            ("Latest build found: v" + latest_build + "\n") +
            ("New build version: v" + ver[0] + "." + ver[1] + "." + ver[2])
        )

        kb = msvcrt.getch()

        # remove formatting from each element
        for i in range(len(ver)):
            ver[i] = unformat(ver[i])

        try:
            kb = kb.decode(encoding='utf-8')
        except:
            pass

        if kb == "a":
            cur = (cur - 1) % 3
        elif kb == "d":
            cur = (cur + 1) % 3
        elif kb == "w":
            ver[cur] = str(int(ver[cur]) + 1)
        elif kb == "s" and int(ver[cur]) > 0:
            ver[cur] = str(int(ver[cur]) - 1)
        elif kb == "e":
            for i in range(len(ver)):
                ver[i] = unformat(ver[i])
            set_version(cwd, ver)
            build_exe(cwd, ver)
            break
        elif kb == "q":
            break

        # add square brackets to the currently selected element
        ver[cur] = "[" + ver[cur].replace(" ", "") + "]"
