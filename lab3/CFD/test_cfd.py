import subprocess
from time import time

print("Compiling...")
subprocess.run(["make", "all"], capture_output=True)
print("Running...")
for _ in range(10):
    start = time()
    out = subprocess.run(["./cfd", "64", "1000"], capture_output=True, text=True)
    print("\n".join([x for x in str(out.stdout).strip().split("\n") if "error" in x]))
    end = time()
    print(f"Time: {end - start}")
