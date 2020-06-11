FROM erdc/proteus:gcc8
MAINTAINER Proteus Project <proteus@googlegroups.com>

USER root
COPY . /home/${NB_USER}/proteus_tutorial
RUN chown -R ${NB_USER}:users /home/${NB_USER}

USER ${NB_USER}
WORKDIR /home/$NB_USER/proteus_tutorial
RUN PKG_CONFIG=x86_64-pc-linux-gnu-pkg-config pip install --no-cache-dir notebook==5.* matplotlib ipywidgets
