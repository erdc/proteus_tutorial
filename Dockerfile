FROM erdc/proteus:latest

MAINTAINER Proteus Project <proteus@googlegroups.com>

WORKDIR /home/$NB_USER

USER $NB_USER

RUN git clone http://github.com/erdc/proteus_tutorial

WORKDIR /home/$NB_USER/proteus_tutorial

USER root

RUN mkdir /home/$NB_USER/proteus_tutorial/work
RUN chown -R $NB_USER:users /home/$NB_USER/proteus_tutorial/work
VOLUME /home/$NB_USER/proteus_tutorial/work

USER $NB_USER
