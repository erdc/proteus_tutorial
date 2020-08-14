"""
Towing Tank
"""

import numpy as np
from math import sqrt
from proteus import Domain
from proteus import Context
from proteus import WaveTools as wt
from proteus.mprans import SpatialTools as st
from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral
import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow

opts = Context.Options([
    # physical parameters
    ("rho_0", 998.2, "Water density"),
    ("nu_0", 1.004e-6,"Water viscosity"),
    ("rho_1", 1.205, "Air density"),
    ("nu_1",1.5e-5, "Air viscosity"),
    ("sigma_01", 0.,"surface tension"),
    ("g", np.array([0.,0.,-9.805]), "Gravity"),
    # wind 
    ("wind_velocity", np.array([0.2,0.,0.]), "wind velocity in m/s"),
    # water
    ("mwl", 2.19, "Mean level at inflow in m"),
    ("U", np.array([0.2,0.,0.]), "Water inflow velocity in m/s"),
    ("outlet_level",2.19, "outlet level"),
    # tank
    ("tank_dim", (6.4,4.0,3.6), "Dimensions (x,y,z) of the tank in m"),
    ("tank_sponge_x", (1.,1.), "Length of (generation, absorption) zones in m, if any"),
    ("tank_sponge_y", (1.,1.), "Width of (generation, absorption) zones in m, if any"),
    # refinement
    ("refinement", 12, " for manually defining element size he: he=horizontal tank dimension/refinement, he=0.02 for ref.125"),
    ("ecH", 1.5, "smoothing=ech*he"),
    ("cfl", 0.5, "Target cfl"),
    # run time
    ("dt_init", 0.001, "Minimum initial time step (otherwise dt_fixed/10) in s"),
    ("rampTime",0.,"duration in which the velocity magnitude is applied"),
    ("dt_output", 0.1, "output stepping"),
    ("Tend", 30., "Simulation time in s "),
    ("fract", 1.,"fraction of duration, Duration= opts.Tend/opts.fract"),
    ("dt_fixed", 0.025, "Fixed time step in s"),
    ("omega",1. ,"used to define dragAlpha")
    ])

# --- Domain
domain = Domain.PiecewiseLinearComplexDomain()

# --- Current steady velocity                              
current=wt.SteadyCurrent(U=opts.U,
                        mwl=opts.mwl,
                        rampTime=opts.rampTime)

y_current=wt.SteadyCurrent(U=np.array([0.2,0.0,0.]),
                        mwl=opts.mwl,
                        rampTime=opts.rampTime)

# --- Tank
tank = st.Tank3D(domain=domain,
                 dim=opts.tank_dim)

vert_axis = 2
xTop = max(tank.vertices[:,vert_axis])

# --- Genetation & Absorption Zones

he=opts.tank_dim[0]/opts.refinement
smoothing=opts.ecH*he
dragAlpha = 5.*opts.omega/opts.nu_0

tank.setSponge(
              x_n = opts.tank_sponge_x[0], 
              x_p = opts.tank_sponge_x[1], 
              y_n = opts.tank_sponge_y[0], 
              y_p = opts.tank_sponge_y[1]
             )

# set generation zone

tank.setGenerationZones(
                        x_n=True,
                        x_p=True,
                       y_n=True,
                       y_p=True,
                       waves=current,
                       dragAlpha=dragAlpha,
                       smoothing = smoothing,
                       wind_speed = opts.wind_velocity,
)

#tank.setAbsorptionZones(
#                       x_p=True,
#                       y_n=True,
#                       y_p=True,
#                       dragAlpha = dragAlpha,
#                       waves=current

#)

# --- Boundary Conditions
tank.BC['z+'].setAtmosphere()
tank.BC['z-'].setFreeSlip()
#tank.BC['z+'].setFreeSlip()
#tank.BC['z-'].setFreeSlip()
#tank.BC['y+'].setFreeSlip()
#tank.BC['y-'].setFreeSlip()
# tank.BC['x+'].setHydrostaticPressureOutletWithDepth(seaLevel=opts.outlet_level,
#                                                     rhoUp=opts.rho_1,
#                                                     rhoDown=opts.rho_0,
#                                                     g=opts.g,
#                                                     refLevel=opts.tank_dim[vert_axis],
#                                                     vert_axis=vert_axis,
#                                                     smoothing=smoothing,
#                                                     U = opts.U,
#                                                     Uwind = opts.wind_velocity)

# tank.BC['x-'].setUnsteadyTwoPhaseVelocityInlet(wave=current, 
#                                                vert_axis=vert_axis,
#                                                smoothing=smoothing,
#                                                wind_speed = opts.wind_velocity)

# tank.BC['y+'].setUnsteadyTwoPhaseVelocityInlet(wave=current, 
#                                                vert_axis=vert_axis,
#                                                smoothing=smoothing,
#                                                wind_speed = opts.wind_velocity)

# tank.BC['y-'].setUnsteadyTwoPhaseVelocityInlet(wave=current, 
#                                                vert_axis=vert_axis,
#                                                smoothing=smoothing,
#                                                wind_speed = opts.wind_velocity)

#tank.BC['y-'].setUnsteadyTwoPhaseVelocityInlet(wave=current,
#                                               vert_axis=vert_axis,
#                                               smoothing=smoothing,
#                                               wind_speed = np.array([0.2,0.0,0.]))


#tank.BC['y-'].setTwoPhaseVelocityInlet(U=opts.U,
#                                       waterLevel=opts.outlet_level,
#                                       smoothing=smoothing,
#                                       Uwind=opts.wind_velocity,
#                                       vert_axis=vert_axis,
#                                       air=1., water=0.,)

tank.BC['sponge'].setNonMaterial()
# Assemble domain
domain.MeshOptions.he = he
st.assembleDomain(domain)
#--- Initial Conditions
class AtRest:
    def uOfXT(self, x, t):
        return 0.0
class VEL_U_IC:
    def uOfXT(self, x, t):
        return opts.U[0]
def sdf(x):
    return x[vert_axis]-opts.outlet_level
class PHI_IC:
    def uOfXT(self, x, t):
        return sdf(x)
class VF_IC:
    def uOfXT(self, x, t):
        return smoothedHeaviside(smoothing,sdf(x))
class P_IC:
    def uOfXT(self, x, t):        
        p_top = 0.0
        phi_top = xTop
        phi = x[vert_axis] - opts.outlet_level
        return p_top - opts.g[vert_axis] * (opts.rho_0 * (phi_top - phi) +
                                       (opts.rho_1 - opts.rho_0) *
                                       (smoothedHeaviside_integral(smoothing, phi_top)-
                                        smoothedHeaviside_integral(smoothing, phi)))

# --- Two Phase Flow

dt_init = opts.dt_init
nDTout = int(round(opts.Tend / opts.dt_fixed))
Duration= opts.Tend/opts.fract

initialConditions = {'pressure': P_IC(),
                     'vel_u': VEL_U_IC(),
                     'vel_v': AtRest(),
                     'vel_w': AtRest()}

initialConditions['vof'] = VF_IC()
initialConditions['ncls'] = PHI_IC()
initialConditions['rdls'] = PHI_IC()
outputStepping = TpFlow.OutputStepping(final_time=Duration,
                                                   dt_init=opts.dt_init,
                                                   # cfl=cfl,
                                                   dt_output=opts.dt_output,
                                                   nDTout=None,
                                                   dt_fixed=None)

myTpFlowProblem = TpFlow.TwoPhaseFlowProblem(ns_model=0, #0: rans2p, 1: rans3p
                                            ls_model=0, #0: vof+ncls+rdls+mcorr, 1: clsvof
                                            nd=domain.nd,
                                            cfl=opts.cfl,
                                            outputStepping=outputStepping,
                                            structured=False,
                                            he=he,
                                            nnx=None,
                                            nny=None,
                                            nnz=None,
                                            domain=domain,
                                            initialConditions=initialConditions,
                                            boundaryConditions=None,
                                             useSuperlu=False,
                                             )

# see Parameters.py
params = myTpFlowProblem.Parameters
params.physical.gravity = opts.g
params.physical.useRANS = 0 # Turbulence Closure Model: 0=No Model, 1=Smagorinksy, 2=Dynamic Smagorinsky, 3=K-Epsilon, 4=K-Omega
myTpFlowProblem.Parameters.Models.rans2p.auxiliaryVariables += domain.auxiliaryVariables['twp']
