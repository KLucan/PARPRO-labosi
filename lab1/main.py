from random import randint
from time import sleep, time

from mpi4py import MPI

MAX_BROJ_ITERACIJA = 200

REQUEST = 1
PROVIDE = 2

TABULATOR = "   "

comm = MPI.COMM_WORLD
# ukupan broj procesa
world_size = comm.Get_size()
if world_size < 2:
    print("Trebaju nam barem 2 filozofa!")
    exit(1)
# moj redni broj
world_rank = comm.Get_rank()
# vilice
forks = {"l": None, "r": None}
# susjedi
lijevi = (world_rank - 1) % world_size
desni = (world_rank + 1) % world_size
# zahtjevi
zahtjevi = []
# init
if world_rank == 0:
    forks = {"l": "dirty", "r": "dirty"}
elif world_rank == world_size - 1:
    pass
else:
    forks["r"] = "dirty"
# radi
while True:
    # misli
    begin = time()
    sleep_time = randint(1, 5)
    while time() < begin + sleep_time:
        print(f"{world_rank * TABULATOR}Mislim.")
        while comm.iprobe(tag=REQUEST):
            request = comm.recv(tag=REQUEST)
            if (request == lijevi and forks["l"] is not None) or (
                request == desni and forks["r"] is not None
            ):
                comm.send(world_rank, request, PROVIDE)
                if request == lijevi and (forks["l"] is not None):
                    forks["l"] = None
                elif request == desni:
                    forks["r"] = None
            else:
                zahtjevi.append(request)
        sleep(1)

    # gladan
    while not all(forks.values()):
        if forks["l"] is None:
            print(f"{world_rank * TABULATOR}Trazim lijevu vilicu.")
            comm.isend(world_rank, lijevi, REQUEST)
        if forks["r"] is None:
            print(f"{world_rank * TABULATOR}Trazim desnu vilicu.")
            comm.isend(world_rank, desni, REQUEST)

        while not all(forks.values()):
            if comm.iprobe(tag=PROVIDE):
                request = comm.recv(tag=PROVIDE)
                if request == lijevi and (forks["l"] != "clean"):
                    forks["l"] = "clean"
                elif request == desni:
                    forks["r"] = "clean"
                else:
                    raise ValueError
            elif comm.iprobe(tag=REQUEST):
                request = comm.recv(tag=REQUEST)
                if request == lijevi and forks["l"] == "dirty":
                    comm.isend(world_rank, lijevi, PROVIDE)
                    forks["l"] = None
                    comm.isend(world_rank, lijevi, REQUEST)
                elif request == desni and forks["r"] == "dirty":
                    comm.isend(world_rank, desni, PROVIDE)
                    forks["r"] = None
                    comm.isend(world_rank, desni, REQUEST)
                elif request in (lijevi, desni):
                    zahtjevi.append(request)
                else:
                    raise ValueError

    print(f"{world_rank * TABULATOR}Jedem.")
    forks["l"] = "dirty"
    forks["r"] = "dirty"

    for request in zahtjevi:
        comm.isend(world_rank, request, PROVIDE)
        if request == lijevi:
            forks["l"] = None
        elif request == desni:
            forks["r"] = None
        else:
            raise ValueError
    zahtjevi = []
