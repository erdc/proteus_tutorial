import subprocess
import os
import pytest

@pytest.mark.dambreak
        
def test_run_dambreak_serial():
    """Test restart workflow"""
    currentPath = "../2d"
    runCommand = "cd "+currentPath+"; parun --TwoPhaseFlow dambreak.py -l 5 -C \"final_time=0.2\" -D ../tests/serial"
    subprocess.check_call(runCommand,shell=True)

def test_check_for_failure_serial():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    log_file=open(currentPath+"/serial/dambreak.log")
    text = log_file.read()
    if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
        print("Serial simulation finished without failures")
        subprocess.check_call("rm -r serial/dambreak*",shell=True)
    else:
        raise pytest.fail("Serial simulation did not converged")
        
def test_run_dambreak_parallel():
    """Test restart workflow"""
    currentPath = "../2d"
    runCommand = "cd "+currentPath+"; mpiexec -np 2 parun --TwoPhaseFlow dambreak.py -l 5 -C \"final_time=0.2\" -D ../tests/parallel"
    subprocess.check_call(runCommand,shell=True)

def test_check_for_failure_parallel():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    log_file=open(currentPath+"/parallel/dambreak.log")
    text = log_file.read()
    if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
        print("Parallel simulation finished without failures")
        subprocess.check_call("rm -r parallel/dambreak*",shell=True)
    else:
        raise pytest.fail("Parallel simulation did not converged")
    
if __name__ == '__main__':
    pass

