import os

filepath = os.path.expanduser("~/.local/lib/python3.10/site-packages/nemo/collections/asr/parts/utils/streaming_utils.py")
if not os.path.exists(filepath):
    print("File not found")
    exit(1)

with open(filepath, "r") as f:
    lines = f.readlines()

# Find the start of class BatchedFrameASRRNNT
class_line = -1
for i, line in enumerate(lines):
    if "class BatchedFrameASRRNNT" in line:
        class_line = i
        break

if class_line != -1:
    print(f"--- Source lines starting from class definition (line {class_line + 1}) ---")
    for i in range(class_line, min(class_line + 200, len(lines))):
        print(f"{i+1}: {lines[i]}", end="")
else:
    print("Class BatchedFrameASRRNNT not found")
