FROM erdc/proteus:python3

MAINTAINER Proteus Project <proteus@googlegroups.com>

WORKDIR /home/$NB_USER

USER $NB_USER

RUN git clone http://github.com/erdc/training_proteus