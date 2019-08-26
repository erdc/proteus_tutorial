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
from [docker.io][docker]. If you are a USACE employee you,
can request installation of docker from ACE-IT.

## Starting the Proteus environment

We will teach the lessings using the [Jupyter environment][jupyter], a 
programming environment that runs in a web browser. Jupyter requires a reasonably 
up-to-date browser, preferably a current version of Chrome, Safari, or Firefox 
(note that Internet Explorer version 9 and below are *not* supported). x

To start the notebook, open a terminal or git bash and type the command:

~~~
$ docker run -it -p 8888:8888 erdc/proteus_tutorial:latest jupyter notebook --ip=0.0.0.0 --port 8888 --no-browser
~~~
{: .bash}

To start a bash shell, open a terminal 
or git bash and type the command:

~~~
$ sudo docker run -it erdc/proteus_tutorial:latest /bin/bash
~~~
{: .bash}

[docker]: https://docker.io
[jupyter]: https://jupyter.org
