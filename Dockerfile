FROM erdc/proteus:gcc8
MAINTAINER Proteus Project <proteus@googlegroups.com>

USER root
RUN apt-get update \
    && apt-get install -yq --no-install-recommends --fix-missing libfreetype6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY . /home/$NB_USER/proteus_tutorial
RUN chown -R ${NB_UID} ${HOME}

USER ${NB_USER}
WORKDIR /home/$NB_USER/proteus_tutorial
RUN pip install --no-cache-dir notebook==5.* matplotlib
