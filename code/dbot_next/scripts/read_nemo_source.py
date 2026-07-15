import os

filepath = os.path.expanduser("~/.local/lib/python3.10/site-packages/nemo/collections/asr/parts/utils/streaming_utils.py")
if not os.path.exists(filepath):
    print("File not found")
    exit(1)

with open(filepath, "r") as f:
    lines = f.readlines()

print("--- Printing lines 1220 to 1350 ---")
for idx in range(1219, min(1350, len(lines))):
    print(f"{idx+1}: {lines[idx]}", end="")
