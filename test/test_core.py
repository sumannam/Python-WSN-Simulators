import os
import sys
import unittest

from test_config import *

# 현재 디렉토리의 절대 경로 구하기
current_dir = os.path.dirname(os.path.abspath(__file__))
# 상위 디렉토리(프로젝트 루트)의 경로 구하기
parent_dir = os.path.dirname(current_dir)
# 상위 디렉토리를 시스템 경로에 추가
sys.path.insert(0, parent_dir)
# test_core 디렉토리를 시스템 경로에 추가
sys.path.insert(0, os.path.join(current_dir, 'test_core'))

print(sys.path)

from test_Field import test_Field


def test_core():
    test_field = unittest.TestLoader().loadTestsFromTestCase(test_Field)

    allTests = unittest.TestSuite()
    
    allTests.addTest(test_field)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(allTests)

test_core()