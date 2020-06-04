import os


#
# Wave Watch 3 specific paths and executables
#
ww3_paths = {}
ww3_paths['python']      = os.getcwd()
ww3_paths['ww3'] , __    = os.path.split(ww3_paths['python'])
ww3_paths['model']       = os.path.join( ww3_paths['ww3'] , 'model' )
ww3_paths['exe']         = os.path.join( ww3_paths['model'] , 'exe' )
ww3_paths['bin']         = os.path.join( ww3_paths['model'] , 'bin' )

ww3_executables = { 'ser':( 'ww3_grid',
                            'ww3_outf',
                            'ww3_outp',
                            'ww3_prep',
                            'ww3_strt',
			                'ww3_uprstr'),
                   'mpi':( 'ww3_sbs1',
                           'ww3_multi',
                           'ww3_shel'),
                   'openmp': ('ww3_sbs1',
                            'ww3_multi',
                            'ww3_shel'),
                   'ww3ser':
                            ('ww3_sbs1',
                            'ww3_multi',
                            'ww3_shel'),
                    }


#
# AWS
#
aws_bucket_name = 'sofar-ww3-model'
aws_prefix      = 'worker/staging/ww3_executables'


#
# Cleanup function
#
def clean( paths = None , clean_executable= True):
    import shutil

    if paths is None:
        #
        global ww3_paths
        paths = ww3_paths

    # Temporary directories generated during complilation
    temporary_directories = ['mod','mod_MPI','mod_SEQ','mod_OMP','obj_OMP','obj','obj_MPI','obj_SEQ','tmp']
    #
    for directory in temporary_directories:
        #
        abs_path = os.path.join( paths['model'] , directory )
        if os.path.exists( abs_path ):
            #
            if os.path.islink(abs_path):
                #
                os.unlink( abs_path )
                #
            else:
                #
                shutil.rmtree( abs_path )
                #
    #

    if clean_executable:
        global ww3_executables

        for executable in ww3_executables:
            #
            abs_path = os.path.join( ww3_paths['exe'] , executable )
            if os.path.exists(abs_path):
                #
                os.remove(abs_path)
                #
            #
        #
    #
#

def make( kind , logger, debug):
    #
    import os
    import shutil
    import subprocess
    global  ww3_paths
    global ww3_executables

    print(kind, debug)
    # Copy sofar specific COMP and LINK files
    if debug:
        comp_source_file = 'comp.Sofar.debug'
        link_source_file = 'link.Sofar.debug'
    else:
        comp_source_file = 'comp.Sofar'
        link_source_file = 'link.Sofar'

    shutil.copyfile(  os.path.join(ww3_paths['bin'],comp_source_file) ,
                      os.path.join(ww3_paths['bin'],'comp'      )  )
    shutil.copyfile(  os.path.join(ww3_paths['bin'],link_source_file) ,
                      os.path.join(ww3_paths['bin'],'link'      )  )

    # Copy appropriate SWITCH file depending on if we are using mpi or ser
    source_file = 'switch'
    if kind.lower() == 'mpi':
        #
        source_file  = os.path.join(ww3_paths['bin'],'switch_Sofar_MPI')
    elif kind.lower() == 'openmp':
            #
            source_file = os.path.join(ww3_paths['bin'], 'switch_Sofar_OPENMP')
        #
    elif kind.lower() == 'ser' or kind.lower() == 'ww3ser':
        #
        source_file = os.path.join(ww3_paths['bin'], 'switch_Sofar')

    make_targets = ''
    for executable in ww3_executables[kind.lower()]:
        #
        make_targets = make_targets + ' ' + executable
        #
    #
    shutil.copyfile(source_file ,
                    os.path.join(ww3_paths['bin'], 'switch'))

    #
    # Run the compile script provided by ww3
    #

    handler  = logger.handlers[0]
    filename = handler.baseFilename

    # Pipe output to file associated with logger
    with open(filename, 'at') as handler:
        #
        code = subprocess.run( [ os.path.join( ww3_paths['bin'],'w3_make') ,make_targets]
                             ,cwd=ww3_paths['bin'],stdout=handler, stderr=handler)
        #

    # Check if we succeeded:
    success = True
    for executable in ww3_executables[kind.lower()]:
        #
        abs_path = os.path.join(ww3_paths['exe'] , executable)
        #
        if not os.path.exists(abs_path):
            #
            logger.info('Executable:' + ' ' + executable + ' ' + 'does not exist' )
            success =False
            #
        #
    return success
    #
#


def copy_locally(target_path):
    import os
    import shutil

    for kind in ww3_executables:
        #
        for executable in ww3_executables[kind]:
            #
            source = os.path.join( ww3_paths['exe'] ,  executable )
            target = os.path.join( target_path ,  executable)

            if os.path.isfile(target):
                os.remove(target)
            shutil.copyfile( source, target )
            #
        #
    #

def copy_to_aws( compilation_platform = None ):
    #
    import boto3
    import os
    import platform

    global aws_bucket_name
    global aws_prefix
    global ww3_executables
    global ww3_paths

    if compilation_platform is None:
        #
        compilation_platform = platform.system()
        #
    #

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(aws_bucket_name)
    #
    for kind in ww3_executables:
        #
        for executable in ww3_executables[kind]:
            #
            source = os.path.join( ww3_paths['exe'] ,  executable )
            target = aws_prefix + '/' + compilation_platform + '/' + executable
            bucket.upload_file( source , target )
            #
        #
    #
#
def getLogger( level=None ):
    #
    # Get a logging object to log console output to compile.log in the python sub-directory
    #
    import logging
    import os
    global ww3_paths
    name = 'compile'
    fileName = os.path.join( ww3_paths['python'] , name + '.log' )
    #
    if os.path.exists( fileName ):
        #
        # On first entry, clear remove existing logs
        #
        os.remove( fileName )
        #
    #
    # Loggers should be associated with files - otherwise logic in the various ww3 driver componenst will break!
    #
    handler = logging.FileHandler(fileName)
    logger  = logging.getLogger(name)
    logger.addHandler(handler)
    #
    if level is None:
        #
        logger.setLevel(logging.DEBUG)
        #
    #
    return logger
    #
#
