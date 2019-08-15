---
title: "Modeling a Dambreak with Two-Phase Flow"
teaching: 30
exercises: 30
questions:
- "How can I change the geometry of the model domain?"
- "How can I modify the boundary and initial conditions for pressure, velocity, and water distribution?"
- "How can I modify units, physical constants, etc.?"
- "What are the most important numerical parameters and how should I modify them?"
objectives:
- "Successfully modify and extend the dambreak example."
- "Gain intuition about the essential elements of a two-phase flow model: geometry, boundary conditions, fluid distribution, and numerical methods."
keypoints:
- "The central task of the main input (Python) file is to create TwoPhaseFlowProblem object."
- "A domain object describtes the geometry, and Proteus supports many different types of domain."
- "Initial condition objects describe the value of pressure, velocity, etc. at the initial time (usualy T=0)."
- "Boundary conditions are required to complete the definition of the model."
- "The SpatialTools module helps automate domain and boundary condition creation."
- "The maximum cell diameter 'he' and the Courant number ('cfl') are the most important numerical parameters."
- "Context options are often used to expose commonly modified parameters."
---
## Domains

*   If you have expereince with computational models, you may be used to thinking of a grid or mesh as the model input.
*   Proteus is designed around the notion that the physics of the model should be independent from the numerical methods, and the mesh belongs to the latter category.
*   This design supports a more "declarative" style of modeling, that is, "declare what you want to do, not how you want to do it".
*   To declare the geometry, we import the proteus Domain module and select a type of domain 
    ~~~
    from proteus import Domain
    tank_dim = (3.22,1.8)#meters
    domain = Domain.RectangularDomain(tank_dim)
    ~~~
    {: .python}
*   This Python code declares that the domain object is a 3.22x1.8 meter "RectangularDomain".

> ## Proteus naming conventions.
>
> *   Capitalized names represent types or classes (abstractions) of objects such as the RectangularDomain type.
> *   Lowercase names reprsent concrete objects such as the ordered pair of the dimensions and the actual domain.
{: .callout}

## SpatialTools

*   A more general type of domain in two-dimensions is known as a planar straight line graph, which is general enough for large majority of two-dimensional geometries.
*   There is trade-off between generality and ease of use, so we introduce a helper module, SpatialTools, to enable easier domain and boundary condition creation for two-phase flow models.
*   Spatial tools predefines some basic domains and facilitates common boundary conditions.
    ~~~
    from proteus.mprans.SpatialTools import Tank2D
    domain = Domain.PlanarStraightLineGraphDomain()
    tank = Tank2D(domain, tank_dim)
    ~~~
    {: .python}

> ## Modifying the domain geometry.
>
> Rerun the dambreak example on a 1.5x1.5m domain
>
> > ## Solution
> > The quickest way to get a result is to edit the input file directly to change the dimensions:
> >
> > ~~~
> > tank_dim = (1.5,1.5) 
> > ~~~
> > {: .python}
> > 
> > A more elegant solution is to add a context option and run the desired case by declaring it on the command line:
> >
> > ~~~
> > opts= Context.Options([
> >     ("tank_dim",(3.22,1.8),"Dimensions of the domain in meters"),
> >     ...
> > tank_dim = opts.tank_dim
> > ~~~
> > {: .python}
> > Then you could run 
> > ~~~
> > $ parun --TwoPhaseFlow dambreak.py -C "tank_dim=(1.5,1.5)"
> > ~~~
> > {: .language-bash}
> {: .solution}
{: .challenge}


## Boundary conditions

*   Like the domain geometry, there are varying levels of automation and generality available.
*   We will focus first on the most automated and specialized approach using SpatialTools.
    ~~~
    tank.BC['y+'].setAtmosphere()
    tank.BC['y-'].setFreeSlip()
    tank.BC['x+'].setFreeSlip()
    tank.BC['x-'].setFreeSlip()
    ~~~
    {: .python}
*   Here we are declaring the type of boundary condition for each boundary of the tank: top, bottom, right, and left.

> ## Switch the tank bottom boundary condition to no-slip.
>
> Documentation can be found at [proteustoolkit.org](https://proteustoolkit.org), but you might guess or use Python built-in help
> (covered in next segment) to find that a "setNoSlip()" functions is available.
>
> > ## Solution
> > ~~~
> > tank.BC['y-'].setNoSlip()
> > ~~~
> > {: .python}
> {: .solution}
{: .challenge}

## Initial conditions

*   For the dambreak model, one of the most important inputs is the shape of the water column.
*   This shape is described by the initial conditions of the level set (signed distance).
*   In Proteus, initial conditions are defined as objects with a member function "uOfXT".
    ~~~
    class PHI_IC:
    def uOfXT(self, x, t):
        phi_x = x[0] - waterLine_x
        phi_y = x[1] - waterLine_y
        if phi_x < 0.0:
            if phi_y < 0.0:
                return max(phi_x, phi_y)
            else:
                return phi_y
        else:
            if phi_y < 0.0:
                return phi_x
            else:
                return (phi_x ** 2 + phi_y ** 2)**0.5
    ~~~
    {: .python}

> ## Change the initial distribution to a parabola.
>
> If we know the free surface height as a function of x, the an approximate
> signed distance is phi=h(x) - z.
>
> > ## Solution
> > ~~~
> > class PHI_IC:
> > def uOfXT(self, x, t):
> >     h = 0.5*tank_dim[1]*((0.5*tank_dim[0])**2 - (x[0] - 0.5*tank_dim[0])**2)
> >     return h - x[1]
~~~
{: .python}
> {: .solution}
{: .challenge}

## Physical Parameters

*   The TwoPhaseFlow object holds the required physical parameters with consistent default values.
*   These parameters can be accessed and modified from the object.
    ~~~
    myTpFlowProblem = TpFlow.TwoPhaseFlowProblem(ns_model=0,
                                                 ls_model=0,
                                                 nd=2,
                                                 cfl=opts.cfl,
                                                 outputStepping=outputStepping,
                                                 structured=structured,
                                                 he=he,
                                                 nnx=nnx,
                                                 nny=nny,
                                                 nnz=None,
                                                 domain=domain,
                                                 initialConditions=initialConditions,
                                                 boundaryConditions=None,
                                                 auxVariables=auxVariables,
                                                 useSuperlu=False)
    physical_parameters = myTpFlowProblem.Parameters.physical
    physical_parameters.kinematicViscosityA = 1000.0*1.004e-6 #sludge
    ~~~
    {: .python}

## Numerical Parmameters

*   The most common numerical parameter that requries changing is the maximum mesh cell diameter, "he".
*   In some examples you will exposed directly, in others you may see a refinement level integer.
*   In dynamical system, the numerical error in time is often closely related to the error in space.
*   If the time step is dt, then we often wish to keep the ratio of "dt*velocity" and "he" near unity.
*   This dimensionless ratio is known as the Courant number and the condition C < 1 is known as a Courant-Friedrichs-Lewy (CFL) condition.
*   As a general heuristic, we find that C=(0.1,0.0) provides sufficient time accuracy for most problems.
