# ---------------------------------------------------- #
# This image compiles a version of the Wave Watch III
# model optimized for the Sofar use cases. It's compiled
# with NetCDF 4 support.

FROM ubuntu:20.04 AS stage1

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC"  apt-get -y install tzdata
#RUN apt-get -yq install build-essential gcc gfortran mpich curl libnetcdf-dev libnetcdff-dev nco
#RUN apt-get -yq install build-essential gcc gfortran openmpi-bin libopenmpi-dev curl libnetcdf-dev libnetcdff-dev nco
RUN apt-get -yq install build-essential gcc gfortran libomp-dev curl libnetcdf-dev libnetcdff-dev nco

# set environmental variables
# for netcdf4
ENV NCDIR /usr/include/netcdf
ENV WWATCH3_NETCDF NC4
ENV NETCDF_CONFIG /usr/bin/nf-config


COPY . /WW3
# clear out some unused documentation files
RUN rm -rf /WW3/manual /WW3/regtests /WW3/smc_docs

WORKDIR /WW3

RUN yes n | ./model/bin/w3_setup model
# you need to run make_Sofar twice to get the preprocessing tools to build
RUN cd ./model/bin/ && ./make_Sofar && ./make_Sofar

RUN apt-get -yq remove build-essential curl

# Stage 2
#FROM ubuntu:20.04
#COPY --from=stage1 /WW3 /WW3
#COPY --from=stage1 /usr/lib/* /usr/lib/
#COPY --from=stage1 /lib/* /lib/
#COPY --from=stage1 /lib64/* /lib64/
##COPY --from=stage1 /usr/bin/mpiexec /usr/bin/hydra_pmi_proxy /usr/bin/ncrcat /usr/bin/
#COPY --from=stage1 /usr/bin/mpirun /usr/bin/hydra_pmi_proxy /usr/bin/ncrcat /usr/bin/
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC"  apt-get -yq install awscli && rm -rf /var/lib/apt/lists/*
