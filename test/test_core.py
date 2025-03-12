import os
import sys
import unittest

# # 프로젝트 루트 디렉토리 설정
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, project_root)

# 테스트 실행
# 상대 경로로 모듈 임포트
from test_core.test_Field import test_Field


def test_engine():
    test_field = unittest.TestLoader().loadTestsFromTestCase(test_Field)

    allTests = unittest.TestSuite()
    
    allTests.addTest(test_field)

    unittest.TextTestRunner(verbosity=2, failfast=True).run(allTests)

if __name__ == "__main__":
    test_engine()