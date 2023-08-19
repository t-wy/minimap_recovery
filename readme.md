# Instructions:
**This code only works for minimaps that each character contributes to 1x2 pixels of the minimap.**
1. Crop the minimap image beforehand to make sure the top left of the image corrspond to the first character at the first line and the height is a multiple of 2.
1. Enter the filename
1. Wait for the script to finish
1. The recovered source is located at filename + "_recovered.txt"
1. The image showing the clusters is located at filename + "_cluster.png" that colors used in vscode configuration can be extracted, and characters that are wrongly classified into another group can be manually identified.

# Reminders:
1. Sometimes (background, color1, color2) are too close to linear that a color may be wrongly classified to be in another one. Check the cluster image to fix in case that happens.
1. Sometimes the configuration color is too close to the background that a minimap color pair may correspond to more than 1 colors. Manually fix the result if that happens.
1. As the width of the minimap is fixed (e.g. 90), line breaks needs to be moved afterwards if long lines exist in the original source code.
