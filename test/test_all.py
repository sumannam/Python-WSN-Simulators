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
sys.path.insert(0, os.path.join(current_dir, 'test_main'))
sys.path.insert(0, os.path.join(current_dir, 'test_core'))
sys.path.insert(0, os.path.join(current_dir, 'test_attacks'))

# print(sys.path)

from test_Sinkhole import test_Sinkhole
from test_Field import test_Field
from test_MicazMotes import test_MicazMotes
from test_Main import test_Main
from test_core.test_DijkstraRouting import test_DijkstraRouting


def test_attacks():
    test_main = unittest.TestLoader().loadTestsFromTestCase(test_Main)
    test_sinkhole = unittest.TestLoader().loadTestsFromTestCase(test_Sinkhole)
    test_field = unittest.TestLoader().loadTestsFromTestCase(test_Field)
    test_micazmotes = unittest.TestLoader().loadTestsFromTestCase(test_MicazMotes)
    test_dijkstra = unittest.TestLoader().loadTestsFromTestCase(test_DijkstraRouting)

    allTests = unittest.TestSuite()
    
    allTests.addTest(test_main)
    allTests.addTest(test_sinkhole)
    allTests.addTest(test_field)
    allTests.addTest(test_micazmotes)
    allTests.addTest(test_dijkstra)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(allTests)

test_attacks()