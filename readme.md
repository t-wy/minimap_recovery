A tool to recover the text in a VSCode minimap image (i.e. the overview of the source code next to the vertical scroll bar).

# Instructions:
**This code only works for minimaps that each character contributes to 1x2 pixels of the minimap.**

_Normal font weight is expected. If light font weight is used, change the line "normal = minimap * 12 // 15" to "normal = minimap * 50 // 60". Exhaust both options if both font weights exist in the source._

1. Crop the minimap image beforehand to make sure that the top left of the image correspond to the first character at the first line and the height is a multiple of 2.
1. Enter the path of the image as the first argument or from the console input
1. Wait for the script to finish
1. The recovered source is located at filename + "_recovered.txt"
1. The image showing the clusters is located at filename + "_cluster.png" that colors used in vscode configuration can be extracted, and characters that are wrongly classified into another group can be manually identified.

# Reminders:
1. Sometimes (background, color1, color2) are too close to linear that a color may be wrongly classified to be in another one. Check the cluster image to fix in case that happens.
1. Sometimes the configuration color is too close to the background that a minimap color pair may correspond to more than 1 possible characters (especially for bracket pairs like `()`, `[]`, `{}`, `<>` which intensities differ too small). Manually fix the result if that happens.
1. As the width of the minimap is fixed (e.g. 90), line breaks needs to be removed afterwards if long lines exist in the original source code.
1. Non-ascii characters can only be recovered to gibberish characters with the same code point (modulo 96).
1. Some components may appear in minimap that are not characters (e.g. color preview). Expect a placeholder to be manually removed.
1. Lines that are currently being edited, and lines with warning(s) / error(s) may have a different background color. It is recommended to separate them to another file for recovery (or to manually cover them up with the background color).
    - Expect gibberish characters and long running time if they are not separated.

# Working Mechanism:
1. Obtain the background color
1. Gather all color pairs (1x2)
1. Cluster all pairs (in a tolerant way that pairs of the same shade always belong to the same cluster)
1. Try to see if the cluster only contains a single shade
    - If so, exhaust all `256` possibilities for each color channel to obtain the possible list of colors
    - Exhaust the list of colors to see if the "prebaked minimap" of any color matches all pairs (i.e. a fitting character exists)
    - If nothing matches, execute greedy algorithm in the cluster to repeatedly choose the color matching the most pairs in the cluster until all characters are recovered

__**Notice that most clique problems are NP-complete, which means clustering using greedy algorithm may return sub-optimal results.**__

## How to (reliably) cluster:
1. Get the angle range from the origin (background color) to each color in the pair
    - Referring to the angle range from background to the point (cube) (r±0.5, g±0.5, b±0.5)
1. Find the intersection of the 2 ranges to get a single angle range of the shade of the character (in 3d)
1. Two pairs are said to be compatible if the ranges overlap, otherwise they must be of different color shades

# License description:
- Code created by TWY (@t-wy), all rights reserved.
- To fork, use, or modify the snippets in other projects, keep the attribution (at the same place in the source code or in apparent places) and remind others that do the same to follow so.
