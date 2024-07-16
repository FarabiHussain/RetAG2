from fontTools import ttLib
font = ttLib.TTFont("Poppins Medium.ttf")
fontFamilyName = font['name'].getDebugName(1)
fullName= font['name'].getDebugName(4)

print(fontFamilyName, fullName)