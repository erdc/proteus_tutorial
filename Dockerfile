FROM erdc/proteus:gcc8
MAINTAINER Proteus Project <proteus@googlegroups.com>

#ARG NB_USER=jovyan
#ARG NB_UID=1000
#ENV USER ${NB_USER}
#ENV NB_UID ${NB_UID}
#ENV HOME /home/${NB_USER}

USER root
#RUN adduser --disabled-password \
#    --gecos "Default user" \
#    --uid ${NB_UID} \
#    ${NB_USER}
COPY . /home/$NB_USER/proteus_tutorial
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
WORKDIR /home/$NB_USER/proteus_tutorial
RUN pip install --no-cache-dir notebook==5.*
