FROM erdc/proteus:bb7009d69c57c7053d8f51cb11275b1e67a0b7e8acfe3dc6543978b80343bcad

MAINTAINER Proteus Project <proteus@googlegroups.com>

WORKDIR /home/$NB_USER/training_proteus

USER $NB_USER

RUN pip install --no-cache-dir notebook==5.*
