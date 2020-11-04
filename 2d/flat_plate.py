import numpy as np
from proteus import (Domain, Context,
                     WaveTools as wt)
from proteus.mprans import SpatialTools as st
import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow
import proteus.TwoPhaseFlow.utils.Parameters as Parameters
from proteus import Gauges as ga
from proteus.mprans import BoundaryConditions as bc 


opts=Context.Options([
    # Geometry
    ('Lx', 4., 'Domain length'),
    ('Ly', 0.4, 'Domain height'),
    # Flow
    ('U', [0.2, 0.0, 0.0], 'Set inlet velocity'),
    ('ramp',1.,"ramp time"),
    ('nu', 1e-6, 'Kinematic viscosity'),
    ('rho', 1000., 'Density'),
    ('g',np.array([0,-9.81,0]),"gravitational acceleration"),
    # Turbulence and parameters
    ("useRANS", 1, "Switch ON turbulence models: 0-None, 1-K-Epsilon, 2-K-Omega1998, 3-K-Omega1988"), # ns_closure: 1-classic smagorinsky, 2-dynamic smagorinsky, 3-k-epsilon, 4-k-omega
    ("sigma_k", 1.0, "sigma_k coefficient for the turbulence model"),
    ("K", 0.41, "von Karman coefficient for the turbulence model"),
    ("B", 5.57, "Wall coefficient for the turbulence model"),
    ("Cmu", 0.09, "Cmu coefficient for the turbulence model"),
    # simulation options
    ('duration', 10., 'Simulation duration'),
    ('dt_init', 0.001, 'Initial timestep'),
    ('dt_output', 0.1, 'time output interval'),
    ("he", 0.03,"Mesh size"),
    ("cfl", 0.5 ,"Target cfl")
    ])
  

#########################################
#domain
#########################################
domain = Domain.PlanarStraightLineGraphDomain()
tank = st.Tank2D(domain, dim=[opts.Lx,opts.Ly])
##################################
#turbulence calculations
##################################
# Reynodls
Re0 = opts.U[0]*opts.Ly/opts.nu
# Skin friction and friction velocity for defining initial shear stress at the wall
cf = 0.045*(Re0**(-1./4.))
Ut = opts.U[0]*np.sqrt(cf/2.)
kappaP = (Ut**2)/np.sqrt(opts.Cmu)
Y_ = opts.he 
Yplus = Y_*Ut/opts.nu
dissipationP = (Ut**3)/(0.41*Y_)

# ke or kw
useRANS = opts.useRANS  # 0 -- None
                        # 1 -- K-Epsilon
                        # 2 -- K-Omega, 1998
                        # 3 -- K-Omega, 1988

model = 'ke'

if opts.useRANS >= 2:
    # k-omega in kw model w = e/k
    model = 'kw'
    dissipationP = np.sqrt(kappaP)/(opts.K*Y_*(opts.Cmu**0.25)) # dissipationP/kappaP

# inlet values 
kInflow = kappaP 
dissipationInflow = dissipationP 

#####################################################
# Boundaries
#####################################################
boundaryOrientations = {'y-': np.array([0., -1.,0.]),
                        'x+': np.array([+1, 0.,0.]),
                        'y+': np.array([0., +1.,0.]),
                        'x-': np.array([-1., 0.,0.]),
                           }
boundaryTags = {'y-': 1,
                'x+': 2,
                'y+': 3,
                'x-': 4,
}


# Attached to 'kappa' in auxiliary variables
kWallTop = bc.kWall(Y=Y_, Yplus=Yplus, nu=opts.nu)
kWallBottom = bc.kWall(Y=Y_, Yplus=Yplus, nu=opts.nu)
kWalls = [kWallTop, kWallBottom]
# Attached to 'twp' in auxiliary variables
wallTop = bc.WallFunctions(turbModel=model, kWall=kWallTop, Y=Y_, Yplus=Yplus, U0=opts.U, nu=opts.nu, Cmu=opts.Cmu, K=opts.K, B=opts.B)
wallBottom = bc.WallFunctions(turbModel=model, kWall=kWallBottom, Y=Y_, Yplus=Yplus, U0=opts.U, nu=opts.nu, Cmu=opts.Cmu, K=opts.K, B=opts.B)
walls = [wallTop, wallBottom]


tank.BC['x-'].setConstantInletVelocity(U=opts.U,ramp= opts.ramp,kk= kInflow, dd=dissipationP ,b_or=boundaryOrientations['y+'] )

tank.BC['x+'].setConstantOutletPressure(p = 0, g = opts.g, rho=opts.rho, kk=kInflow, dd= dissipationP ,b_or=boundaryOrientations['y+'])

tank.setTurbulentWall(walls)
tank.setTurbulentKWall(kWalls)
tank.BC['y+'].setWallFunction(walls[0])
tank.BC['y-'].setWallFunction(walls[1])

tank.BC['x-'].setConstantInletVelocity(opts.U,opts.ramp,kInflow,dissipationP,boundaryOrientations['x-'])
tank.BC['x+'].setConstantOutletPressure(0.,opts.rho,opts.g,kInflow,dissipationP,boundaryOrientations['x+'])
class AtRest:
    def uOfXT(self, x, t):
        return 0.0
class kIn:
    def uOfXT(self, x, t):
        return kInflow 

class dIn:
    def uOfXT(self, x, t):
        return dissipationP 

########################
# Assemble domain

##########################

domain.MeshOptions.he = opts.he
st.assembleDomain(domain)

initialConditions = {'pressure':AtRest(),
                     'vel_u': AtRest(),
                     'vel_v': AtRest(),
                     'k':kIn(),
                     'dissipation':dIn()}
                     
myTpFlowProblem = TpFlow.TwoPhaseFlowProblem()
myTpFlowProblem.outputStepping.final_time = opts.duration
myTpFlowProblem.outputStepping.dt_output=opts.dt_output
myTpFlowProblem.outputStepping.dt_init=opts.dt_init
myTpFlowProblem.domain = domain

myTpFlowProblem.SystemNumerics.cfl = opts.cfl

#myTpFlowProblem.SystemPhysics.setDefaults()

physics = myTpFlowProblem.SystemPhysics
physics.addModel(Parameters.ParametersModelRANS2P,'flow')
physics.addModel(Parameters.ParametersModelKappa,'kappa')
physics.addModel(Parameters.ParametersModelDissipation,'dissipation')

m = myTpFlowProblem.SystemPhysics.modelDict 

m['flow'].p.initialConditions['p'] = AtRest()
m['flow'].p.initialConditions['u'] = AtRest()
m['flow'].p.initialConditions['v'] = AtRest()
m['kappa'].p.initialConditions['kappa'] = kIn() 
m['dissipation'].p.initialConditions['epsilon'] = dIn()
                     
params = myTpFlowProblem.SystemPhysics

params['rho_0'] = opts.rho  # water
params['rho_1'] = opts.rho # air
params['nu_0'] = opts.nu  # water
params['nu_1'] = opts.nu  # air
params['surf_tension_coeff'] = 0.
params['gravity'] = opts.g
params['useRANS'] = True

