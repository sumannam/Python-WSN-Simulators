import sys
import os
import psutil
import subprocess

from test_config import *

def test_build(file_name):
    try:
        result = subprocess.run(['python', file_name], check=True)
        print(f'{file_name} 빌드 성공')
    except subprocess.CalledProcessError:
        print(f'{file_name} 빌드 실패')

if __name__ == "__main__":
    # test_build('test\\test_engine.py')
    test_build('test\\test_main.py')
    test_build('test\\test_core.py')    