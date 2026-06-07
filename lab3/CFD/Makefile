CC       = g++
CFLAGS   = -O2

NVCC     = nvcc
NVFLAGS  = -O2

LDFLAGS  = -lm

CPP_SRCS = arraymalloc.cpp boundary.cpp cfdio.cpp
CU_SRCS  = cfd.cu jacobi.cu
SRCS     = $(CPP_SRCS) $(CU_SRCS)
OBJS     = $(CPP_SRCS:.cpp=.o) $(CU_SRCS:.cu=.o)
TARGET   = cfd

# Run-time arguments (overridable on the command line, e.g. make run SCALE=2 ITER=500)
SCALE    ?= 64
ITER     ?= 1000

.PHONY: all run clean

# Default target: build the executable
all: $(TARGET)

# Link object files into the final executable (nvcc handles CUDA runtime linkage)
$(TARGET): $(OBJS)
	$(NVCC) $(NVFLAGS) -o $@ $^ $(LDFLAGS)

# Compile C++ source files
%.o: %.cpp
	$(CC) $(CFLAGS) -c -o $@ $<

# Compile CUDA source files (only if a .cu file is present)
%.o: %.cu
	$(NVCC) $(NVFLAGS) -c -o $@ $<

# Run the program with configurable scale factor and iteration count
run: $(TARGET)
	./$(TARGET) $(SCALE) $(ITER)

# Remove all build artifacts (object files and the executable)
clean:
	rm -f $(OBJS) $(TARGET)
