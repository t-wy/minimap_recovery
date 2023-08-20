# Instructions:
# This code only works for minimaps that each character contributes to 1x2 pixels of the minimap.
# Normal font weight is expected. If light font weight is used, change the line "normal = minimap * 12 // 15" to "normal = minimap * 50 // 60". Exhaust both options if both font weights exist in the source.
# Crop the minimap image beforehand to make sure that the top left of the image corrspond to the first character at the first line and the height is a multiple of 2.
# Enter the path of the image as the first argument or from the console input
import sys
if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = input("Filename: ")
# input file is filename + ".png" at the same directory
filename = filename.rstrip(".PNG").rstrip(".png")
if filename == "":
    filename = "minimap"
# Wait for the script to finish
# The recovered source is located at filename + "_recovered.txt"
# The image showing the clusters is located at filename + "_cluster.png" that colors used in vscode configuration can be extracted, and characters that are wrongly classified into another group can be manually identified.

# Reminders:
# Sometimes (background, color1, color2) are too close to linear that a color may be wrongly classified to be in another one. Check the cluster image to fix in case that happens.
# Sometimes the configuration color is too close to the background that a minimap color pair may correspond to more than 1 possible characters (especially for bracket pairs like `()`, `[]`, `{}`, `<>` which intensities differ too small). Manually fix the result if that happens.
# As the width of the minimap is fixed (e.g. 90), line breaks needs to be removed afterwards if long lines exist in the original source code.
# Non-ascii characters are not supported for recovery, expect gibberish characters and long running time if they exist.
# Some components may appear in minimap that are not characters (e.g. color preview). Expect a placeholder to be manually removed.
# Lines that are currently being edited, and lines with warning(s) / error(s) may have a different background color. It is recommended to separate them to another file for recovery.

# Code created by TWY (@t-wy), all rights reserved.
# License description:
# To fork, use, or modify the snippets in other projects, keep the attribution (here or in apparent places) and remind others that do the same to follow so.

import numpy as np
from PIL import Image
from tqdm import tqdm

arr = np.array(Image.open(filename + ".png"))[:,:,:3]
arr = arr.reshape((arr.shape[0] >> 1, 2, arr.shape[1], 3)).transpose((0, 2, 1, 3)).astype(int)

def format_color(r, g, b):
    return "#{0:02x}{1:02x}{2:02x} ({0}, {1}, {2})".format(r, g, b)

# find background color: assume the mode is the background
colors, count = np.unique(arr.reshape((-1, 3)), axis=0, return_counts=True)
background = tuple(colors[np.argmax(count)])
print("Background Color:", format_color(*background))

def sort_key(x):
    return sorted(x, reverse=True)

all_pairs = set()
for y in range(arr.shape[0]):
    for x in range(arr.shape[1]):
        all_pairs.add((tuple(arr[y, x, 0]), tuple(arr[y, x, 1])))
all_pairs = sorted(all_pairs, key=sort_key, reverse=True)

def get_theta_range(offset1, offset2):
    # angle range such that some vector from background can reach points that can be rounded to (offset1, offset2)
    import math
    # handle 9 kinds of range, angle should be < pi unless both signs are 0
    def sign(v):
        if v > 0.5:
            return 1
        if v < -0.5:
            return -1
        return 0
    sign1, sign2 = sign(offset1), sign(offset2)
    if sign1 == 0 and sign2 == 0:
        # accept all angles
        return (-math.pi, math.pi)
    if sign2 == 0:
        if sign1 == 1:
            xoffset = (offset1 - 0.5, offset1 - 0.5)
        else:
            xoffset = (offset1 + 0.5, offset1 + 0.5)
    elif sign2 == 1:
        xoffset = (offset1 + 0.5, offset1 - 0.5)
    else:
        xoffset = (offset1 - 0.5, offset1 + 0.5)
    if sign1 == 0:
        if sign2 == 1:
            yoffset = (offset2 - 0.5, offset2 - 0.5)
        else:
            yoffset = (offset2 + 0.5, offset2 + 0.5)
    elif sign1 == 1:
        yoffset = (offset2 - 0.5, offset2 + 0.5)
    else:
        yoffset = (offset2 + 0.5, offset2 - 0.5)
    return (math.atan2(yoffset[0], xoffset[0]), math.atan2(yoffset[1], xoffset[1]))

def merge_theta_ranges(r1, r2):
    # merge two angle ranges
    if r1 is None:
        return None
    if r2 is None:
        return None
    import math
    def is_full_range(r):
        return r[0] == -math.pi and r[1] == math.pi
    def is_pass_pi(r):
        return r[1] < r[0]
    if is_full_range(r1):
        return r2
    if is_full_range(r2):
        return r1
    # both are not full range
    if is_pass_pi(r1):
        if is_pass_pi(r2):
            return (max(r1[0], r2[0]), min(r1[1], r2[1]))
        if r1[1] >= r2[0]:
            return (r2[0], min(r1[1], r2[1]))
        return None
    else:
        if is_pass_pi(r2):
            if r2[1] >= r1[0]:
                return (r1[0], min(r1[1], r2[1]))
            return None
        if r1[1] >= r2[0] and r2[1] >= r1[0]:
            return (max(r1[0], r2[0]), min(r1[1], r2[1]))
        return None

def get_range(color):
    v = tuple(a - b for a, b in zip(color, background))
    return (get_theta_range(v[0], v[1]), get_theta_range(v[1], v[2]), get_theta_range(v[2], v[0]))

def merge_range(r1, r2):
    return (merge_theta_ranges(r1[0], r2[0]), merge_theta_ranges(r1[1], r2[1]), merge_theta_ranges(r1[2], r2[2]))

# the standard one
def compatible(pair1, pair2):
    temp = merge_range(
        merge_range(get_range(pair1[0]), get_range(pair1[1])),
        merge_range(get_range(pair2[0]), get_range(pair2[1]))
    )
    return all(t is not None for t in temp)

# https://github.com/microsoft/vscode/blob/main/src/vs/editor/browser/viewParts/minimap/minimapPreBaked.ts
minimap = np.array(list(bytes.fromhex("0000511D6300CF609C709645A78432005642574171487021003C451900274D35D762755E8B629C5BA856AF57BA649530C167D1512A272A3F6038604460398526BCA2A968DB6F8957C768BE5FBE2FB467CF5D8D5B795DC7625B5DFF50DE64C466DB2FC47CD860A65E9A2EB96CB54CE06DA763AB2EA26860524D3763536601005116008177A8705E53AB738E6A982F88BAA35B5F5B626D9C636B449B737E5B7B678598869A662F6B5B8542706C704C80736A607578685B70594A49715A4522E792"))).reshape((-1, 2))

# https://github.com/microsoft/vscode/blob/main/src/vs/editor/browser/viewParts/minimap/minimapCharRenderer.ts#L16
normal = minimap * 12 // 15

def composite(bg, fg, alpha):
    return round(bg + (fg - bg) * alpha / 255)

def find_candidates(pairs, channel):
    bg = background[channel]
    # pairs: values from a single channel
    _max, _min = max(v for p in pairs for v in p), min(v for p in pairs for v in p)
    assert _max <= bg or _min >= bg

    pairs_set = set(pairs)
    # never going to have 127.5 so no problem with rounding
    if _max <= bg:
        if _min == bg:
            return [bg] # list(range(255)) # no way to determine the color, just take one of them to reduce iteration count
        else:
            # only need to test [0, _max]
            test_range = range(0, _max + 1)
    else:
        # only need to test [_min, 255]
        test_range = range(_min, 256)
    temp = []
    for test in test_range:
        test_set = set(tuple(composite(bg, test, it) for it in i) for i in normal)
        if pairs_set.issubset(test_set):
            temp.append(test)
    return temp


clusters = []
# do clustering
for pair in all_pairs:
    if pair == (background, background):
        continue
    clusters2 = []
    clusters3 = [pair]
    for cl in clusters:
        for co in cl:
            if compatible(co, pair):
                clusters3.extend(cl)
                break
        else:
            clusters2.append(cl)        
    clusters2.append(clusters3)
    clusters = clusters2

cluster_num = {}
for index, cluster in enumerate(clusters):
    for i in cluster:
        cluster_num[i] = index

# isolate all comment block pairs (may get a better result if used)
# hash_color = None
# for y in range(arr.shape[0]):
#     is_comment = None
#     last = 0
#     for x in range(arr.shape[1]):
#         key = (tuple(arr[y, x, 0]), tuple(arr[y, x, 1]))
#         if x == 0 and key == (background, background):
#             is_comment = False # ignore indented comments for now
#             break
#         # if the comment character is more than 1 characters
#         # (e.g. // something), then change the below 1 to 2.
#         if x == 1 and key != (background, background):
#             is_comment = False # ignore shebang for now
#             break
#         if key != (background, background):
#             last = x
#             index = cluster_num[key]
#             if is_comment is None:
#                 is_comment = index
#             elif index != is_comment:
#                 is_comment = False
#                 break
#     if last > 2 and is_comment != False and is_comment != None:
#         hash_color = (tuple(arr[y, 0, 0]), tuple(arr[y, 0, 1]))
#         break

# new_cluster = set()
# for y in range(arr.shape[0]):
#     for x in range(arr.shape[1]):
#         key = (tuple(arr[y, x, 0]), tuple(arr[y, x, 1]))
#         if key == hash_color:
#             for x in range(x, arr.shape[1]):
#                 key = (tuple(arr[y, x, 0]), tuple(arr[y, x, 1]))
#                 new_cluster.add(key)
#             break
# clusters[is_comment] = [i for i in clusters[is_comment] if i not in new_cluster]
# if len(clusters[is_comment]) == 0:
#     clusters.pop(is_comment)
# clusters.append(list(new_cluster))

def list_product(*x):
    if len(x) == 1:
        for i in x[0]:
            yield (i, )
    else:
        for i in x[0]:
            for j in list_product(*x[1:]):
                yield (i, ) + j

# do strict clustering
# Notice that clique problem is NP-complete, while means the below method may return sub-optimal results
answer = {}
refer = {}

def gen_test_map(r, g, b):
    return {tuple(tuple(composite(bg, test, it) for bg, test in zip(background, (r, g, b))) for it in i): chr(32 + c) for c, i in enumerate(normal)}

def add_answers(test_map, cluster, color):
    for pair in cluster:
        if pair not in answer and pair in test_map:
            answer[pair] = test_map[pair]
            refer[pair] = color

def get_score(test_map, cluster):
    return sum(pair in test_map for pair in cluster)

def output_choice(r, g, b):
    print("Chosen: " + format_color(r, g, b))

def exhaust(all_pairs):
    # do a lazy search to reduce the exhaust complexity
    failed_candidates = set()
    candidates_cache = {}
    while True:
        left_out = [pair for pair in all_pairs if pair not in answer]
        if len(left_out) == 0:
            return
        # get all pairs that are compatible with all other pairs
        good_pairs = []
        bad_pairs = []
        for i in left_out:
            for j in left_out:
                if not compatible(i, j):
                    bad_pairs.append(i)
                    break
            else:
                good_pairs.append(i)
        if len(good_pairs):
            channel_cand = []
            for i in range(3):
                channel_cand.append(find_candidates([(p[0][i], p[1][i]) for p in good_pairs], i))
                # print("RGB"[i], list(map(hex, channel_cand[-1])))
            scores = []
            for r, g, b in list_product(*channel_cand):
                # check if r, g, b is a possible answer
                test_map = gen_test_map(r, g, b)
                if all(pair in test_map for pair in good_pairs):
                    scores.append((get_score(test_map, left_out), (r, g, b)))
            scores.sort(reverse=True)
            if len(scores):
                score, (r, g, b) = scores[0]
                test_map = gen_test_map(r, g, b)
                output_choice(r, g, b)
                add_answers(test_map, left_out, (r, g, b))
                continue
        # greedily choose a color that matches the most of remaining pairs
        print("Exhausting...")
        scores = []
        candidates = set()
        print("Finding candidates...")
        for pair in tqdm(left_out):
            if pair in candidates_cache:
                candidates |= candidates_cache[pair]
            else:
                channel_cand = []
                for i in range(3):
                    channel_cand.append(find_candidates([(pair[0][i], pair[1][i])], i))
                candidates_cache[pair] = set(list_product(*channel_cand))
                candidates |= candidates_cache[pair]
        print("Evaluating candidates...")
        candidates -= set(failed_candidates)
        for r, g, b in tqdm(list(candidates)):
            test_map = gen_test_map(r, g, b)
            scores.append((get_score(test_map, left_out), (r, g, b)))
        scores.sort(reverse=True)
        for score, (r, g, b) in reversed(scores):
            if score > 0:
                break
            failed_candidates.add((r, g, b))
        if len(scores) and scores[0][0] > 0:
            score, (r, g, b) = scores[0]
            output_choice(r, g, b)
            print("Match: {:.2f}% of the remaining pairs".format(score * 100 / (len(left_out))))
            test_map = gen_test_map(r, g, b)
            add_answers(test_map, left_out, (r, g, b))
        else:
            print("Non-ascii characters detected!")
            # Probably all characters here are non-ascii
            add_answers({pair: "?" for pair in left_out}, left_out, background)


for cluster in clusters:
    # check if all pairs are compatible
    flag = True
    for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
            if not compatible(cluster[i], cluster[j]):
                flag = False
    if flag:
        # Found a potentially good cluster
        channel_cand = []
        for i in range(3):
            channel_cand.append(find_candidates([(p[0][i], p[1][i]) for p in cluster], i))
            # print("RGB"[i], list(map(hex, channel_cand[-1])))
        for r, g, b in list_product(*channel_cand):
            # check if r, g, b is a possible answer
            test_map = gen_test_map(r, g, b)
            if all(pair in test_map for pair in cluster):
                output_choice(r, g, b)
                add_answers(test_map, cluster, (r, g, b))
                break
        else:
            exhaust(cluster)
    else:
       # Found a bad cluster
        exhaust(cluster)

lines = []
cluster_arr = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
for y in range(arr.shape[0]):
    line = []
    for x in range(arr.shape[1]):
        key = (tuple(arr[y, x, 0]), tuple(arr[y, x, 1]))
        if key == (background, background):
            line.append(" ")
            cluster_arr[y, x] = background
        elif key in answer:
            line.append(answer[key])
            cluster_arr[y, x] = refer[key]
        else:
            line.append("?")
            cluster_arr[y, x] = (128, 128, 128)
    lines.append("".join(line).rstrip())
open(filename + "_recovered.txt", "w").write("\n".join(lines))

# provide the reference cluster image for manual fixing / color config extraction
cluster_img = Image.fromarray(cluster_arr)
cluster_img.save(filename + "_cluster.png")
