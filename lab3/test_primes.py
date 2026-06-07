import subprocess

svi_exp = [26]
svi_L = [32, 64, 128, 256, 512]
svi_B = [16, 32, 64, 128, 256]

for exp in svi_exp:
    for L in svi_L:
        for B in svi_B:
            print(f"exp={exp}, L={L}, B={B}, G={L*B}")
            for _ in range(10):
                out = subprocess.run(["uv", "run", "primes.py", str(exp), str(L), str(B)], capture_output=True, text=True)
                print(str(out.stdout).strip())
