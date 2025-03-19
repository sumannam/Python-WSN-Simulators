import hashlib
import os
import unittest

class test_Main(unittest.TestCase):
    """CSV 및 로그 파일 해시값 비교를 통한 무결성 테스트"""
    
    def setUp(self):
        # 현재 디렉토리 경로
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 프로젝트 루트 디렉토리 (test 폴더의 상위 폴더)
        self.project_root = os.path.abspath(os.path.join(self.current_dir, os.pardir))
        self.project_root = os.path.abspath(os.path.join(self.project_root, os.pardir))
        print(self.project_root)
        
        # 원본 CSV 파일과 새 CSV 파일 경로 (절대 경로로 명확하게 지정)
        self.original_csv = os.path.join(self.project_root, 'test', 'test_results', 'test_final_nodes_state.csv')
        self.new_csv = os.path.join(self.project_root, 'results', 'final_nodes_state.csv')
        
        # 원본 로그 파일과 새 로그 파일 경로 (절대 경로로 명확하게 지정)
        self.original_log = os.path.join(self.project_root, 'test', 'test_results', 'test_simulation.log')
        self.new_log = os.path.join(self.project_root, 'results', 'simulation.log')
        
        # 경로 출력 (디버깅용)
        print(f"원본 CSV 경로: {self.original_csv}")
        print(f"새 CSV 경로: {self.new_csv}")
        print(f"원본 로그 경로: {self.original_log}")
        print(f"새 로그 경로: {self.new_log}")
    
    def calculate_hash(self, file_path, algorithm='sha256'):
        """파일의 해시 값을 계산"""
        hash_obj = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as file:
            # 청크 단위로 파일 읽기
            for chunk in iter(lambda: file.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    
    def test_csv_hash_integrity(self):
        """CSV 파일 해시 무결성 테스트"""
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(self.original_csv), 
                        f"원본 CSV 파일이 없습니다: {self.original_csv}")
        self.assertTrue(os.path.exists(self.new_csv), 
                        f"새 CSV 파일이 없습니다: {self.new_csv}")
        
        # 해시값 계산
        original_hash = self.calculate_hash(self.original_csv)
        new_hash = self.calculate_hash(self.new_csv)
        
        # 결과 출력
        print(f"\n원본 CSV 파일 해시: {original_hash}")
        print(f"새 CSV 파일 해시: {new_hash}")
        
        # 해시값 비교
        self.assertEqual(original_hash, new_hash, 
                         "CSV 파일 해시값이 일치하지 않습니다. 파일이 변경되었습니다.")
    
    def test_log_hash_integrity(self):
        """로그 파일 해시 무결성 테스트"""
        # 파일 존재 여부 확인
        self.assertTrue(os.path.exists(self.original_log), 
                        f"원본 로그 파일이 없습니다: {self.original_log}")
        self.assertTrue(os.path.exists(self.new_log), 
                        f"새 로그 파일이 없습니다: {self.new_log}")
        
        # 해시값 계산
        original_hash = self.calculate_hash(self.original_log)
        new_hash = self.calculate_hash(self.new_log)
        
        # 결과 출력
        print(f"\n원본 로그 파일 해시: {original_hash}")
        print(f"새 로그 파일 해시: {new_hash}")
        
        # 해시값 비교
        self.assertEqual(original_hash, new_hash, 
                         "로그 파일 해시값이 일치하지 않습니다. 파일이 변경되었습니다.")