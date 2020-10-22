# ---------------------------------------------------- #
# This image compiles a version of the Wave Watch III
# model optimized for the Sofar use cases and intended 
# for benchmarking and other lightweight applications.

FROM ubuntu:18.04 AS stage1

RUN apt-get update
RUN apt-get -yq install build-essential gfortran mpich curl

# download tarball of sofarmaster branch &
# rename the directory to WW3 for ease of use
# then clear out some unused documentation files
COPY . /WW3
RUN rm -rf /WW3/manual /WW3/regtests /WW3/smc_docs

WORKDIR /WW3

RUN yes n | ./model/bin/w3_setup model
# you need to run make_Sofar twice to get the preprocessing tools to build
RUN cd ./model/bin/ && ./make_Sofar && ./make_Sofar

RUN apt-get -yq remove build-essential curl

# Stage 2
FROM ubuntu:18.04
COPY --from=stage1 /WW3 /WW3
COPY --from=stage1 /usr/lib/* /usr/lib/
COPY --from=stage1 /lib/* /lib/
COPY --from=stage1 /lib64/* /lib64/
COPY --from=stage1 /usr/bin/mpiexec /usr/bin/hydra_pmi_proxy /usr/bin/
