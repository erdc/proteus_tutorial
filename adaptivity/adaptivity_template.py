domain = Domain.PUMIDomain(dim=2) #initialize the domain
#read the geometry and mesh
from proteus import MeshTools
parallelPartitioningType = MeshTools.MeshParallelPartitioningTypes.element
domain.MeshOptions.setParallelPartitioningType('element')
#domain.AdaptManager.PUMIAdapter.loadModelAndMesh(b"Reconstructed.dmg", b"Reconstructed.smb")
domain.AdaptManager.PUMIAdapter.loadModelAndMesh(b"Reconstructed.dmg", b"4-Proc/.smb")

#vital and requires knowledge of problem setup
domain.AdaptManager.modelDict = {'flow':0,'phase':2,'correction':[3,4]}

#adaptation options
domain.AdaptManager.adapt = 1
domain.AdaptManager.sizeInputs = [b'interface',b'error_vms']
domain.AdaptManager.hmax = he*2.0
domain.AdaptManager.hmin= he/2.0
domain.AdaptManager.hphi= he/2.0
domain.AdaptManager.numAdaptSteps= 10
domain.AdaptManager.numIterations= 5
domain.AdaptManager.targetError= 2.0
domain.AdaptManager.gradingFactor= 1.5
domain.AdaptManager.logging= 0

