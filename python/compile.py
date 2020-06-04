import tools
import os
import sys

if len(sys.argv) > 0:
    flags = sys.argv[1:]
else:
    flags = ['mpi']

if 'debug' in flags:
    debug = True
else:
    debug = False

if 'mpi' in flags:
    mpi = True
else:
    mpi = False

if 'openmp' in flags:
    openmp = True
else:
    openmp = False

if 'ww3ser' in flags:
    ww3ser = True
else:
    ww3ser = False

logger = tools.getLogger( )


# 1) Clean temporary file from possible previous compilation
logger.info('1) cleaning existing temporary files')
tools.clean()

# 2) make serial code
if not tools.make( 'ser',logger,debug):
    message = 'Serial compilation failed'
    logger.info( message)
    raise Exception(message)

# 3) make MPI/OPENMP code
if mpi:
    if not tools.make( 'mpi',logger,debug):
        message = 'MPI compilation failed'
        logger.info( message)
        raise Exception(message)

elif openmp:
    # 3) make MPI code
    if not tools.make( 'openmp',logger,debug):
        message = 'OPENMP compilation failed'
        logger.info( message)
        raise Exception(message)


if debug:
    tools.copy_locally(os.path.expanduser('~/work') )

# 4) Copy results to AWS:
tools.copy_to_aws()

# 5) Clean up - do not delete executables
logger = tools.clean(clean_executable=False)