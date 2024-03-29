import subprocess
import os
import pytest

@pytest.mark.marin



def test_run_marin_serial():
    """Test restart workflow"""
    currentPath = os.path.dirname(os.path.abspath(__file__))
    runCommand = "cd "+os.path.join(currentPath,"..","3d")+" && which parun && parun --TwoPhaseFlow marin.py -l 5 -C \"final_time=0.2\" -D ../tests/serial"
    print(runCommand)
    subprocess.check_call(runCommand,shell=True)

def test_check_for_failure_serial():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(currentPath,"serial","marin.log")) as log_file:
        text = log_file.read()
        if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
            print("Serial simulation finished without failures")
            runCommand="rm "+os.path.join(currentPath,"serial","*")
            subprocess.check_call(runCommand,shell=True)
        else:
            raise pytest.fail("Serial simulation did not converged")

def test_run_marin_parallel():
    """Test restart workflow"""
    currentPath = os.path.dirname(os.path.abspath(__file__))
    runCommand = "cd "+os.path.join(currentPath,"..","3d")+" && mpiexec -np 2 parun --TwoPhaseFlow marin.py -l 5 -C \"final_time=0.2\" -D ../tests/parallel"
    subprocess.check_call(runCommand,shell=True)

def test_check_for_failure_parallel():
    currentPath=os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(currentPath,"parallel","marin.log")) as log_file:
        text = log_file.read()
        if (text.find('Step failed') == -1) and (text.find('Done with garbage') != -1):
            print("Parallel simulation finished without failures")
            runCommand="rm "+os.path.join(currentPath,"parallel","*")
            subprocess.check_call(runCommand,shell=True)
        else:
            raise pytest.fail("Parallel simulation did not converged")

if __name__ == '__main__':
    pass

