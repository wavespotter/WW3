import tools

logger = tools.getLogger( )


# 1) Clean temporary file from possible previous compilation
logger.info('1) cleaning existing temporary files')
tools.clean()

# 2) make serial code
if not tools.make( 'ser',logger):
    message = 'Serial compilation failed'
    logger.info( message)
    raise Exception(message)

# 3) make MPI code
if not tools.make( 'mpi',logger):
    message = 'Serial compilation failed'
    logger.info( message)
    raise Exception(message)

# 4) Copy results to AWS:
tools.copy_to_aws()

# 5) Clean up - do not delete executables
logger = tools.clean(clean_executable=False)