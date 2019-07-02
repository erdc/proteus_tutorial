FROM erdc/proteus:latest

MAINTAINER Proteus Project <proteus@googlegroups.com>

WORKDIR /home/$NB_USER

USER $NB_USER

RUN rm -rf chmod u+rwX -R /home/$NB_USER/.hashdist/src
RUN rm -rf rm -rf /home/$NB_USER/.hashdist/src
RUN rm -rf /home/$NB_USER/proteus/.git
RUN rm -rf /home/$NB_USER/stack/.git
RUN rm -rf /home/$NB_USER/air-water-vv/.git
RUN rm -rf /home/$NB_USER/.cache
RUN git clone http://github.com/erdc/training_proteus

WORKDIR /home/$NB_USER/training_proteus
