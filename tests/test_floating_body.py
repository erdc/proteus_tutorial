import subprocess
import os
import pytest

@pytest.mark.floating_body

# def teardown_method():
#     """ Tear down function """
#     FileList = ['floating_body.xmf',
#                 'floating_body.h5',
#                 'forceHistory_p.txt',
#                 'forceHistory_v.txt',
#                 'momentHistory.txt',
#                 'wettedAreaHistory.txt',
#                 'timeHistory.txt',
#                 'floating_body.log'
#     ]
#     for file in FileList:
#         if os.path.isfile(file):
#             os.remove(file)
#         else:
#             pass
        
def test_run_floating_body_serial():
    """Test restart workflow"""
    currentPath = os.path.dirname(os.path.abspath(__file__))
    runCommand = "cd "+currentPath+"/../2d/; parun --TwoPhaseFlow floating_body.py -l 5 -C \"final_time=0.2\" -D ../tests/serial"
    subprocess.check_call(runCommand,shell=True)
        
@pytest.mark.skipif(os.getenv('TEST_PROFILE')=="proteus-conda-osx", reason="need to fix locally on osx")
def test_check_for_failure_serial():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    log_file=open(currentPath+"/serial/floating_body.log")
    text = log_file.read()
    if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
        print("Serial simulation finished without failures")
        subprocess.check_call("rm "+currentPath+"/serial/floating_body*",shell=True)
    else:
        raise pytest.fail("Serial simulation did not converged")
        
def test_run_floating_body_parallel():
    """Test restart workflow"""
    currentPath = os.path.dirname(os.path.abspath(__file__))
    runCommand = "cd "+currentPath+"/../2d/; mpiexec -np 2 parun --TwoPhaseFlow floating_body.py -l 5 -C \"final_time=0.2\" -D ../tests/parallel"
    subprocess.check_call(runCommand,shell=True)

def test_check_for_failure_parallel():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    log_file=open(currentPath+"/parallel/floating_body.log")
    text = log_file.read()
    if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
        print("Parallel simulation finished without failures")
        subprocess.check_call("rm "+currentPath+"/parallel/floating_body*",shell=True)
    else:
        raise pytest.fail("Parallel simulation did not converged")
    
if __name__ == '__main__':
    pass

