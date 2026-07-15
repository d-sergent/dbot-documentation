import os

filepath = os.path.expanduser("~/.local/lib/python3.10/site-packages/nemo/collections/asr/parts/utils/streaming_utils.py")
if not os.path.exists(filepath):
    print("File not found")
    exit(1)

with open(filepath, "r") as f:
    lines = f.readlines()

# Find the line containing shifted_indices
found_line = -1
for i, line in enumerate(lines):
    if "shifted_indices =" in line:
        found_line = i
        break

if found_line != -1:
    print(f"--- Source lines surrounding shifted_indices (line {found_line + 1}) ---")
    start = max(0, found_line - 20)
    end = min(len(lines), found_line + 20)
    for i in range(start, end):
        print(f"{i+1}: {lines[i]}", end="")
else:
    print("shifted_indices not found")
