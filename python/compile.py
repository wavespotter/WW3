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

kind = 'mpi'
if 'mpi' in flags:
    kind = 'mpi'
elif 'openmp' in flags:
    kind = 'openmp'
elif 'ww3ser' in flags:
    kind = 'ww3ser'

logger = tools.getLogger( )

# 1) Clean temporary file from possible previous compilation
logger.info('1) cleaning existing temporary files')
tools.clean()

# 2) make serial code
print('Compiling strictly serial ww3 code')
if not tools.make( 'ser',logger,debug):
    message = 'Serial compilation failed'
    logger.info( message)
    raise Exception(message)

# 3) make MPI/OPENMP code
print('Compiling parallel ww3 code')
if not tools.make( kind,logger,debug):
    message = '{kind} compilation failed'
    logger.info( message)
    raise Exception(message)

if debug:
    tools.copy_locally(os.path.expanduser('~/work') )

# 4) Copy results to AWS:
tools.copy_to_aws(kind, debug=debug)

# 5) Clean up - do not delete executables
#logger = tools.clean(clean_executable=False)