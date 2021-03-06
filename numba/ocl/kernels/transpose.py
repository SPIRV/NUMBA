from numba import ocl
from numba.ocl.ocldrv.driver import driver
from numba import numpy_support as nps
import math

def transpose(a, b=None):
    """Compute the transpose of 'a' and store it into 'b', if given,
    and return it. If 'b' is not given, allocate a new array
    and return that.

    This implements the algorithm documented in 
    http://devblogs.nvidia.com/parallelforall/efficient-matrix-transpose-cuda-cc/"""

    if not b:
        cols, rows = a.shape
        strides = a.dtype.itemsize * cols, a.dtype.itemsize
        b = ocl.ocldrv.devicearray.DeviceNDArray((rows, cols), strides, dtype=a.dtype)

    dt=nps.from_dtype(a.dtype)

    tpb = driver.get_device().MAX_THREADS_PER_BLOCK
    # we need to factor available threads into x and y axis
    tile_width = int(math.pow(2, math.log(tpb, 2)/2))
    tile_height = int(tpb / tile_width)

    tile_shape=(tile_height, tile_width + 1)

    @ocl.jit
    def kernel(input, output):

        tile = ocl.shared.array(shape=tile_shape, dtype=dt)

        tx = ocl.threadIdx.x
        ty = ocl.threadIdx.y
        bx = ocl.blockIdx.x * ocl.blockDim.x
        by = ocl.blockIdx.y * ocl.blockDim.y
        x = by + tx
        y = bx + ty

        if by+ty < input.shape[0] and bx+tx < input.shape[1]:
            tile[ty, tx] = input[by+ty, bx+tx]
        ocl.barrier()
        if y < output.shape[0] and x < output.shape[1]:
            output[y, x] = tile[tx, ty]


    # one block per tile, plus one for remainders
    blocks = int(b.shape[0]/tile_height + 1), int(b.shape[1]/tile_width + 1)
    # one thread per tile element
    threads = tile_height, tile_width
    kernel[blocks, threads](a, b)

    return b
