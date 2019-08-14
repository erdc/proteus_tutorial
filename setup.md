---
layout: page
title: "Setup"
permalink: /setup/
---

## Installing Docker

[docker][docker] is a tool for running lightweight linux containers,
which are similar to virtual machines. They allow us to distribute a
standard working environment for modeling with Proteus. If you have
administrative access to your machine, you can install docker directly
from [http://docker.io][docker.io]. If you are a USACE employeed you,
can request installation of docker from ACE-IT.

## Starting the Proteus environment

We will teach the lessings using the [Jupyter environment][jupyter], a 
programming environment that runs in a web browser. Jupyter requires a reasonably 
up-to-date browser, preferably a current version of Chrome, Safari, or Firefox 
(note that Internet Explorer version 9 and below are *not* supported). If you 
installed Python using Anaconda, Jupyter should already be on your system. If 
you did not use Anaconda, use the Python package manager pip
(see the [Jupyter website][jupyter-install] for details.)

To start the notebook, open a terminal or git bash and type the command:

~~~
$ sudo docker run --net="host" -it erdc/proteus:latest start-notebook.sh
~~~
{: .bash}

To start a bash shell, open a terminal 
or git bash and type the command:

~~~
$ sudo docker run --net="host" -it erdc/proteus:latest /bin/bash
~~~
{: .bash}

[docker]: https://docker.io
[jupyter]: https://jupyter.org
