import subprocess

svi_exp = [26, 28, 30]
svi_b = [1024, 2048, 4096]

for exp in svi_exp:
    print(f"exp={exp}")
    print("CUDA kernel")
    for _ in range(10):
        out = subprocess.run(["uv", "run", "pi.py", str(exp)], capture_output=True, text=True)
        print(str(out.stdout).strip())
    if exp < 28:
        print("Numba vectorize")
        for _ in range(10):
            out = subprocess.run(["uv", "run", "numba_pi.py", str(exp)], capture_output=True, text=True)
            print(str(out.stdout).strip())
    if exp < 30:
        print("Numba guvectorize")
        for B in svi_b:
            print(f"block_size={B}")
            for _ in range(10):
                out = subprocess.run(["uv", "run", "numba_gu_pi.py", str(exp), "-b", str(B)], capture_output=True, text=True)
                print(str(out.stdout).strip())
