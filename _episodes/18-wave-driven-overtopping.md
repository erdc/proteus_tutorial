---
title: "Wave-Driven Overtopping"
teaching: 15
exercises: 15
questions:
- "How do I add obstacles to the model domain?"
- "How do I generate waves?"
objectives:
- "Provide some approaches for adding structure to the domain using `proteus.SpatialTools`."
- "Summarize the library of wave generation functions in `proteus.WaveTools`."
- "Show how to run in parallel on HPC machines."
keypoints:
- "`SpatialTools` support composition of the domain from smaller/simpler parts."
- "`WaveTools` contains most common wave generation needs (linear, nonlinear, random)."
- "Running in parallel requires setting up the HPC environment in a PBS script but is otherwise the same as running in serial."
---
## Geometry of the `floodwall.py` problem

*   The example adds a wall structure to a rectangular tank.
*   

~~~
domain = Domain.PlanarStraightLineGraphDomain()

boundaries=['gate','left','right','bottom','top']
boundaryTags=dict([(key,i+1) for (i,key) in enumerate(boundaries)])

vertices=[[0.0,0.0],#0
          [2.0,0.0],#1
          [2.1,1.0],#2
          [2.15,1.0],#3
          [2.75 - 0.75*(2.75-2.15)/(1.0-0.0),0.75],#4
          [3.,0.75],#5
          [3.,1.5],#6
          [0.0,1.5],#7
]

vertexFlags=[boundaryTags['bottom'],
             boundaryTags['gate'],
             boundaryTags['gate'],
             boundaryTags['gate'],
             boundaryTags['gate'],
             boundaryTags['bottom'],
             boundaryTags['top'],
             boundaryTags['top'],
             ]

segments=[[0,1],
          [1,2],
          [2,3],
          [3,4],
          [4,5],
          [5,6],
          [6,7],
          [7,0]]

segmentFlags=[boundaryTags['bottom'],
              boundaryTags['gate'],
              boundaryTags['gate'],
              boundaryTags['gate'],
              boundaryTags['bottom'],
              boundaryTags['right'],
              boundaryTags['top'],
              boundaryTags['left']]

regions=[[0.1,0.1]]
regionFlags=[1]

tank = st.CustomShape(domain,
                      vertices=vertices,
                      vertexFlags=vertexFlags,
                      segments=segments,
                      segmentFlags=segmentFlags,
                      regions = regions,
                      regionFlags = regionFlags,
                      boundaryTags=boundaryTags,
                      boundaryOrientations=boundaryOrientations)
~~~
{: .python}

## Boundary conditions using `proteus.WaveTools`


~~~
wave=wt.MonochromaticWaves(period=2.5,
                           waveHeight=waterLevel/3.0,
                           mwl=waterLevel,
                           depth=waterLevel,
                           g=g,
                           waveDir=np.array([1.,0.,0.]))
tank.BC['left'].setUnsteadyTwoPhaseVelocityInlet(wave, smoothing=1.5*he)
tank.BC['bottom'].setFreeSlip()
tank.BC['gate'].setFreeSlip()
tank.BC['right'].setFreeSlip()
tank.BC['top'].setAtmosphere()
~~~
{: .python}

## PBS Script for Onyx

~~~
#!/bin/bash
#PBS -A ERDCV00898R40
#PBS -l walltime=001:00:00
#PBS -l select=1:ncpus=44:mpiprocs=44
#PBS -l place=scatter:excl
#PBS -q debug
#PBS -N dambreak
#PBS -j oe
#PBS -l application=proteus
#PBS -m eba
##PBS -M myemail@mydomain
#setup modules and check proteus version
. ${MODULESHOME}/etc/modules.sh
export MODULEPATH=${PROJECTS_HOME}/proteus/modulefiles:${MODULEPATH}
module load proteus/1.7.0
which parun
#create a working directory and copy over the inputs use
cd $PBS_O_WORKDIR
mkdir $WORKDIR/$PBS_JOBNAME.$PBS_JOBID
cp dambreak.py $WORKDIR/$PBS_JOBNAME.$PBS_JOBID
cp dambreak.pbs $WORKDIR/$PBS_JOBNAME.$PBS_JOBID
#change into the work directory and run
cd  $WORKDIR/$PBS_JOBNAME.$PBS_JOBID
aprun -n ${BC_MPI_TASKS_ALLOC}  parun -l 5 --TwoPhaseFlow dambreak.py -C "he=0.0125"
~~~
{: .bash}
