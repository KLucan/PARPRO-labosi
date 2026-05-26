from mpi4py import MPI

comm = MPI.COMM_WORLD
print("Hello! I'm processor %s: rank %d from %d running in total..." % (MPI.Get_processor_name(), comm.rank, comm.size))

