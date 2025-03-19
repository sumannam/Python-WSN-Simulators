import unittest
import os
import sys
import hashlib
import shutil
import tempfile
import filecmp
import subprocess
import re
from datetime import datetime

# config.py에서 상수 가져오기
from test_config import *

class test_main(unittest.TestCase):
    """simulation.log 파일의 무결성을 테스트하는 클래스"""
    
    def setUp(self):
        """테스트 전 필요한 디렉토리 설정 및 환경 준비"""
        # 현재 디렉토리
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 원본 로그 파일 경로 (test/test_result/test_simulation.log)
        self.original_log_path = os.path.join(self.current_dir, 'test', 'test_result', 'test_simulation.log')
        
        # 새 로그 파일 저장 경로 (result/simulation.log)
        self.new_log_dir = os.path.join(self.current_dir, 'result')
        self.new_log_path = os.path.join(self.new_log_dir, 'simulation.log')
        
        # 새 로그 디렉토리가 없으면 생성
        if not os.path.exists(self.new_log_dir):
            os.makedirs(self.new_log_dir, exist_ok=True)
        
        # 테스트 후 복구를 위한 백업 디렉토리
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.temp_dir, 'backup')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 만약 이미 새 로그 파일이 존재한다면 백업
        if os.path.exists(self.new_log_path):
            shutil.copy2(self.new_log_path, os.path.join(self.backup_dir, 'simulation.log'))
    
    def tearDown(self):
        """테스트 후 정리 작업"""
        # 백업한 새 로그 파일 복원 (필요한 경우)
        backup_log = os.path.join(self.backup_dir, 'simulation.log')
        if os.path.exists(backup_log):
            shutil.copy2(backup_log, self.new_log_path)
        
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def calculate_file_hash(self, file_path, hash_type='sha256'):
        """파일의 해시값 계산"""
        hash_func = getattr(hashlib, hash_type)()
        
        with open(file_path, 'rb') as f:
            # 청크 단위로 파일 읽기
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def normalize_log_content(self, log_content):
        """
        로그 내용을 정규화하여 비교 가능한 형태로 변환
        - 타임스탬프 제거
        - 경로나 환경에 따라 달라질 수 있는 부분 정규화
        """
        # 타임스탬프 정규식 패턴
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        
        # 타임스탬프 제거
        normalized_content = re.sub(timestamp_pattern, 'TIMESTAMP', log_content)
        
        # 파일 경로 정규화
        normalized_content = re.sub(r'[A-Za-z]:\\.*?\\', 'PATH/', normalized_content)
        normalized_content = re.sub(r'/.*?/', 'PATH/', normalized_content)
        
        # 경과 시간 정규화 (부동 소수점 값)
        normalized_content = re.sub(r'(\d+\.\d+) seconds', 'X.XXXX seconds', normalized_content)
        
        return normalized_content
    
    def compare_logs_normalized(self, file1, file2):
        """두 로그 파일의 내용을 정규화하여 비교"""
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        normalized1 = self.normalize_log_content(content1)
        normalized2 = self.normalize_log_content(content2)
        
        return normalized1 == normalized2
    
    def run_simulation_and_get_log(self):
        """
        main.py를 실행하고 생성된 로그 파일 경로 반환
        result/simulation.log에 결과가 저장되도록 환경 설정
        """
        # 현재 환경변수 백업
        env = os.environ.copy()
        
        # 로그 파일이 저장될 디렉토리를 환경변수로 설정
        env['WSN_RESULTS_DIR'] = os.path.dirname(self.new_log_path)
        
        # main.py 실행
        main_py_path = os.path.join(self.current_dir, 'main.py')
        try:
            subprocess.run([sys.executable, main_py_path], 
                           env=env, 
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.fail(f"main.py 실행 실패: {e.stderr.decode('utf-8')}")
        
        # 로그 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists(self.new_log_path), 
                        f"로그 파일이 생성되지 않았습니다: {self.new_log_path}")
        
        return self.new_log_path
    
    def test_log_hash_integrity(self):
        """로그 파일의 해시 무결성 테스트"""
        # 원본 로그 파일이 있는지 확인
        if not os.path.exists(self.original_log_path):
            self.skipTest(f"원본 로그 파일이 존재하지 않습니다: {self.original_log_path}")
        
        # 원본 로그 파일의 해시 계산
        original_hash = self.calculate_file_hash(self.original_log_path)
        
        # main.py 실행 및 새 로그 파일 생성
        new_log_path = self.run_simulation_and_get_log()
        
        # 새 로그 파일의 해시 계산
        new_hash = self.calculate_file_hash(new_log_path)
        
        # 해시 비교 (타임스탬프 등으로 인해 정확히 일치하지 않을 수 있음)
        if original_hash != new_hash:
            # 해시가 다르면 내용 정규화 비교
            is_content_same = self.compare_logs_normalized(self.original_log_path, new_log_path)
            
            # 정규화 후에도 내용이 다르면 로그 파일의 일부분만 출력하여 차이점 제공
            if not is_content_same:
                with open(self.original_log_path, 'r', encoding='utf-8') as f1, open(new_log_path, 'r', encoding='utf-8') as f2:
                    original_lines = f1.readlines()[:20]  # 처음 20줄만
                    new_lines = f2.readlines()[:20]
                
                diff_message = "원본 로그와 새 로그의 차이점(처음 20줄):\n"
                diff_message += "===== 원본 로그 =====\n"
                diff_message += "".join(original_lines)
                diff_message += "\n===== 새 로그 =====\n"
                diff_message += "".join(new_lines)
                
                self.fail(f"로그 파일의 내용이 다릅니다.\n{diff_message}")
            
            # 해시는 다르지만 내용이 같다면 테스트 통과 (타임스탬프 등의 차이)
            else:
                print("해시 불일치: 타임스탬프 등의 차이가 있으나 정규화 후 내용은 동일합니다.")
        else:
            print("해시 일치: 로그 파일이 완전히 동일합니다.")
        
        # 테스트 성공 메시지
        print(f"\n원본 로그 해시: {original_hash}")
        print(f"새 로그 해시: {new_hash}")

    def test_log_content_integrity(self):
        """로그 파일의 내용 구조 무결성 테스트"""
        # 원본 로그 파일이 있는지 확인
        if not os.path.exists(self.original_log_path):
            self.skipTest(f"원본 로그 파일이 존재하지 않습니다: {self.original_log_path}")
        
        # main.py 실행 및 새 로그 파일 생성
        new_log_path = self.run_simulation_and_get_log()
        
        # 원본 및 새 로그 파일 읽기
        with open(self.original_log_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(new_log_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        # 중요 로그 메시지 패턴 확인
        key_patterns = [
            r"WSN Simulation Start",
            r"Field created with \d+ nodes",
            r"Routing setup completed",
            r"Simulating \d+ Report Transmissions",
            r"Sinkhole Attack Executed at \d+% of reports",
            r"Number of malicious nodes: \d+",
            r"Total Energy Consumed: [\d\.]+",
            r"WSN Simulation End"
        ]
        
        for pattern in key_patterns:
            original_match = re.search(pattern, original_content)
            new_match = re.search(pattern, new_content)
            
            self.assertIsNotNone(original_match, f"원본 로그에서 패턴 '{pattern}'을 찾을 수 없습니다.")
            self.assertIsNotNone(new_match, f"새 로그에서 패턴 '{pattern}'을 찾을 수 없습니다.")