from random import randint
from time import sleep, time

from mpi4py import MPI

MAX_BROJ_ITERACIJA = 200

def misli(vrijeme):
    begin = time()
    while time() < begin + vrijeme:
        # odgovaraj na zahtjeve
        sleep(1)
    return

comm = MPI.COMM_WORLD
# ukupan broj procesa
world_size =  comm.Get_size()
if world_size < 2:
    print("Trebaju nam barem 2 filozofa!")
    exit(1)
# moj redni broj
world_rank = comm.Get_rank()
# vilice
left, right = -1, 0
# susjedi
lijevi = (world_rank - 1) % world_size
desni = (world_rank + 1) % world_size
# zahtjevi
zahtjevi = [0, 0]
#init
if world_rank == 0:
    left = 0
    right = 0

#radi
for i in range(MAX_BROJ_ITERACIJA):
    # misli
    begin = time()
    while time() < begin + randint(1, 6):
        print(f"Filozof {world_rank} misli.")
        if comm.iprobe():
            zahtjev = comm.recv()
            match zahtjev:
                case -1: # lijevi
                    if right >= 0:
                        comm.send(1, lijevi) # daj lijevom vilicu
                        right = -1
                    else:
                        zahtjevi[0] = 1
                case -2: # desni
                    if left >= 0:
                        comm.send(2, desni) # daj desnom vilicu
                        left = -1
                    else:
                        zahtjevi[1] = 1
        sleep(1)

    #gladan
    while (left < 0 or right < 0):
        if left < 0:
            comm.isend(-1, lijevi) # reci lijevom da trebaš vilicu
        if right < 0:
            comm.isend(-2, desni) # reci desnom da trebaš vilicu
    
        while(left < 0 or right < 0):
            msg = comm.recv()
            match msg:
                case -1: # desni kaže da treba vilicu
                    if right >= 0: # imam desnu vilicu
                        comm.send(2, desni) # daj desnom vilicu
                        right = -1
                    else:
                        zahtjevi[1] = 1
                case -2: # lijevi kaže da treba vilicu
                    if left >= 0: # imam lijevu vilicu
                        comm.send(1, lijevi) # daj lijevom vilicu
                        left = -1
                    else:
                        zahtjevi[0] = 1
                case 1: # desni šalje vilicu
                    right = 1
                case 2: # lijevi šalje vilicu
                    left = 1
        
    print(f"Filozof {world_rank} jede.")
    left = 0
    right = 0
    if zahtjevi[0]: # lijevi zahtjev
        comm.send(2, desni)
        zahtjevi[0] = 0
    if zahtjevi[1]: # desni zahtjev
        comm.send(1, lijevi)
        zahtjevi[1] = 0
