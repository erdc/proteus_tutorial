import numpy as np
from proteus import Domain, Context
from proteus.mprans import SpatialTools as st
import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow
from proteus import WaveTools as wt

# dependencies for FSI
from proteus.mbd import CouplingFSI as fsi
import pychrono


#   ____            _            _      ___        _   _
#  / ___|___  _ __ | |_ _____  _| |_   / _ \ _ __ | |_(_) ___  _ __  ___
# | |   / _ \| '_ \| __/ _ \ \/ / __| | | | | '_ \| __| |/ _ \| '_ \/ __|
# | |__| (_) | | | | ||  __/>  <| |_  | |_| | |_) | |_| | (_) | | | \__ \
#  \____\___/|_| |_|\__\___/_/\_\\__|  \___/| .__/ \__|_|\___/|_| |_|___/
#                                           |_|
# Context options
# used in command line directly with option -C
# e.g.: parun [...] -C "g=(0.,-9.81,0.) rho_0=998.2 genMesh=False"
#
# only change/add context options in the "other options section"
# other sections have variables used in _p and _n files

context_options = []
# physical constants
context_options += [
    ("rho_0", 998.2, "Water density"),
    ("nu_0", 1.004e-6, "Water kinematic viscosity m/sec^2"),
    ("rho_1", 1.205, "Air Densiy"),
    ("nu_1", 1.5e-5, "Air kinematic viscosity m/sec^2"),
    ("sigma_01", 0., "Surface tension"),
    ("g", (0, -9.81, 0.), "Gravitational acceleration vector"),
    ]
# run time options
context_options += [
    ("T", 0.1 ,"Simulation time in s"),
    ("dt_init", 0.001 ,"Value of initial time step"),
    ("dt_fixed", None, "Value of maximum time step"),
    ("archiveAllSteps", False, "archive every steps"),
    ("dt_output", 0.05, "number of saves per second"),
    ("runCFL", 0.5 ,"Target CFL value"),
    ("cfl", 0.5 ,"Target CFL value"),
    ]

he = 0.01
movingDomain = True
addedMass = True

# instantiate context options
opts=Context.Options(context_options)

rho_0 = 998.2
nu_0 = 1.004e-6
rho_1 = 1.205
nu_1 = 1.5e-5
g = np.array([0., -9.81, 0.])


# ----- CONTEXT ------ #

water_level = 0.515
wave_period = 0.87
wave_height = 0.05
wave_direction = np.array([1., 0., 0.])
wave_type = 'Fenton'  #'Linear'

# number of Fourier coefficients
Nf = 8

wave = wt.MonochromaticWaves(period=wave_period,
                             waveHeight=wave_height,
                             mwl=water_level,
                             depth=water_level,
                             g=g,
                             waveDir=wave_direction,
                             waveType=wave_type,
                             Nf=8)
wavelength = wave.wavelength



#  ____                        _
# |  _ \  ___  _ __ ___   __ _(_)_ __
# | | | |/ _ \| '_ ` _ \ / _` | | '_ \
# | |_| | (_) | | | | | | (_| | | | | |
# |____/ \___/|_| |_| |_|\__,_|_|_| |_|
# Domain
# All geometrical options go here (but not mesh options)

domain = Domain.PlanarStraightLineGraphDomain()

# ----- SHAPES ----- #

# TANK
tank = st.Tank2D(domain, dim=(2*wavelength, 2*water_level))

# SPONGE LAYERS
# generation zone: 1 wavelength
# absorption zone: 2 wavelengths
tank.setSponge(x_n=wavelength, x_p=2*wavelength)


caisson = st.Rectangle(domain, dim=(0.5, 0.2), coords=(0., 0.))
# set barycenter in middle of caisson
caisson.setBarycenter([0., 0.])
# caisson is considered a hole in the mesh
caisson.setHoles([[0., 0.]])
# 2 following lines only for py2gmsh
caisson.holes_ind = np.array([0])
tank.setChildShape(caisson, 0)
# translate caisson to middle of the tank
caisson.translate(np.array([1*wavelength, water_level]))

#   ____ _
#  / ___| |__  _ __ ___  _ __   ___
# | |   | '_ \| '__/ _ \| '_ \ / _ \
# | |___| | | | | | (_) | | | | (_) |
#  \____|_| |_|_|  \___/|_| |_|\___/
# Chrono

# SYSTEM

# create system
system = fsi.ProtChSystem()
# communicate gravity to system
system.ChSystem.Set_G_acc(pychrono.ChVectorD(g[0], g[1], g[2]))
# set maximum time step for system
system.setTimeStep(1e-4)

system.ChSystem.SetSolverType(pychrono.ChSolver.Type_MINRES)

# BODY

# create floating body
body = fsi.ProtChBody(system=system)
# give it a name
body.setName(b'my_body')
# attach shape: this automatically adds a body at the barycenter of the caisson shape
body.attachShape(caisson)
# set 2D width (for force calculation)
body.setWidth2D(1.)
# record values
body.setRecordValues(all_values=True)
# impose constraints
free_x = np.array([0., 1., 0.]) # translational
free_r = np.array([0., 0., 1.]) # rotational
body.setConstraints(free_x=free_x, free_r=free_r)
# access pychrono ChBody
chbody = body.ChBody
# set mass
chbody.SetMass(16.)
# set inertia
chbody.SetInertiaXX(pychrono.ChVectorD(1., 1., 0.236))


#  ____                        _                   ____                _ _ _   _
# | __ )  ___  _   _ _ __   __| | __ _ _ __ _   _ / ___|___  _ __   __| (_) |_(_) ___  _ __  ___
# |  _ \ / _ \| | | | '_ \ / _` |/ _` | '__| | | | |   / _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
# | |_) | (_) | |_| | | | | (_| | (_| | |  | |_| | |__| (_) | | | | (_| | | |_| | (_) | | | \__ \
# |____/ \___/ \__,_|_| |_|\__,_|\__,_|_|   \__, |\____\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
#                                           |___/
# Boundary Conditions

# CAISSON

# set no-slip conditions on caisson
for tag, bc in caisson.BC.items():
    bc.setNoSlip()

# TANK

# atmosphere on top
tank.BC['y+'].setAtmosphere()
# free slip on bottom
tank.BC['y-'].setFreeSlip()
# free slip on the right
tank.BC['x+'].setFreeSlip()
# non material boundaries for sponge interface
tank.BC['sponge'].setNonMaterial()

# fix in space nodes on the boundaries of the tank
for tag, bc in tank.BC.items():
    bc.setFixedNodes()

# WAVE AND RELAXATION ZONES

smoothing = he*1.5
dragAlpha = 5*2*np.pi/wave_period/(1.004e-6)
tank.BC['x-'].setUnsteadyTwoPhaseVelocityInlet(wave,
                                               smoothing=smoothing,
                                               vert_axis=1)
tank.setGenerationZones(x_n=True,
                        waves=wave,
                        smoothing=smoothing,
                        dragAlpha=dragAlpha)
tank.setAbsorptionZones(x_p=True,
                        dragAlpha=dragAlpha)



#  ___       _ _   _       _    ____                _ _ _   _
# |_ _|_ __ (_) |_(_) __ _| |  / ___|___  _ __   __| (_) |_(_) ___  _ __  ___
#  | || '_ \| | __| |/ _` | | | |   / _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
#  | || | | | | |_| | (_| | | | |__| (_) | | | | (_| | | |_| | (_) | | | \__ \
# |___|_| |_|_|\__|_|\__,_|_|  \____\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
# Initial Conditions

from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral
smoothing = 1.5*he
nd = domain.nd

class P_IC:
    def uOfXT(self, x, t):
        p_L = 0.0
        phi_L = tank_dim[nd-1] - water_level
        phi = x[nd-1] - water_level
        p = p_L -g[nd-1]*(rho_0*(phi_L - phi)
                          +(rho_1 -rho_0)*(smoothedHeaviside_integral(smoothing,phi_L)
                                                -smoothedHeaviside_integral(smoothing,phi)))
        return p
class U_IC:
    def uOfXT(self, x, t):
        return 0.0
class V_IC:
    def uOfXT(self, x, t):
        return 0.0
class W_IC:
    def uOfXT(self, x, t):
        return 0.0
class VF_IC:
    def uOfXT(self, x, t):
        return smoothedHeaviside(smoothing, x[nd-1]-water_level)
class PHI_IC:
    def uOfXT(self, x, t):
        return x[nd-1] - water_level

# instanciating the classes for *_p.py files
initialConditions = {'pressure': P_IC(),
                     'vel_u': U_IC(),
                     'vel_v': V_IC(),
                     'vel_w': W_IC(),
                     'vof': VF_IC(),
                     'ncls': PHI_IC(),
                     'rdls': PHI_IC()}

#  __  __           _        ___        _   _
# |  \/  | ___  ___| |__    / _ \ _ __ | |_(_) ___  _ __  ___
# | |\/| |/ _ \/ __| '_ \  | | | | '_ \| __| |/ _ \| '_ \/ __|
# | |  | |  __/\__ \ | | | | |_| | |_) | |_| | (_) | | | \__ \
# |_|  |_|\___||___/_| |_|  \___/| .__/ \__|_|\___/|_| |_|___/
#                                |_|


domain.MeshOptions.use_gmsh = False
domain.MeshOptions.genMesh = True
domain.MeshOptions.he = he
mesh_fileprefix = 'mesh'
domain.MeshOptions.setOutputFiles(mesh_fileprefix)
st.assembleDomain(domain)
domain.use_gmsh = domain.MeshOptions.use_gmsh
domain.geofile = mesh_fileprefix




#  _   _                           _
# | \ | |_   _ _ __ ___   ___ _ __(_) ___ ___
# |  \| | | | | '_ ` _ \ / _ \ '__| |/ __/ __|
# | |\  | |_| | | | | | |  __/ |  | | (__\__ \
# |_| \_|\__,_|_| |_| |_|\___|_|  |_|\___|___/
# Numerics

outputStepping = TpFlow.OutputStepping(
    final_time=opts.T,
    dt_init=opts.dt_init,
    # cfl=opts.cfl,
    dt_output=opts.dt_output,
    nDTout=None,
    dt_fixed=opts.dt_fixed,
)

myTpFlowProblem = TpFlow.TwoPhaseFlowProblem(
    ns_model=None,
    ls_model=None,
    nd=domain.nd,
    cfl=opts.cfl,
    outputStepping=outputStepping,
    structured=False,
    he=he,
    domain=domain,
    initialConditions=initialConditions,
)

# Necessary for moving domains
myTpFlowProblem.movingDomain = movingDomain

params = myTpFlowProblem.Parameters

# PHYSICAL PARAMETERS
params.physical.densityA = rho_0  # water
params.physical.densityB = rho_1  # air
params.physical.kinematicViscosityA = nu_0  # water
params.physical.kinematicViscosityB = nu_1  # air
params.physical.gravity = g
params.physical.surf_tension_coeff = 0.

m = myTpFlowProblem.Parameters.Models

# MODEL PARAMETERS
ind = -1
if movingDomain:
    m.moveMeshElastic.index = ind+1
    ind += 1
m.rans2p.index = ind+1
ind += 1
m.vof.index = ind+1
ind += 1
m.ncls.index = ind+1
ind += 1
m.rdls.index = ind+1
ind += 1
m.mcorr.index = ind+1
ind += 1
if addedMass is True:
    m.addedMass.index = ind+1
    ind += 1

# ADD RELAXATION ZONES TO AUXILIARY VARIABLES
m.rans2p.auxiliaryVariables += domain.auxiliaryVariables['twp']
# ADD SYSTEM TO AUXILIARY VARIABLES
m.rans2p.auxiliaryVariables += [system]

if addedMass is True:
    # passed in added_mass_p.py coefficients
    m.addedMass.auxiliaryVariables += [system.ProtChAddedMass]
    max_flag = 0
    max_flag = max(domain.vertexFlags)
    max_flag = max(domain.segmentFlags+[max_flag])
    max_flag = max(domain.facetFlags+[max_flag])
    flags_rigidbody = np.zeros(max_flag+1, dtype='int32')
    for s in system.subcomponents:
        if type(s) is fsi.ProtChBody:
            for i in s.boundaryFlags:
                flags_rigidbody[i] = 1
    m.addedMass.p.coefficients.flags_rigidbody = flags_rigidbody
