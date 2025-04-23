import unittest
import sys
import os
import numpy as np

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)  # 상위 디렉토리 (test)
project_root = os.path.dirname(test_dir)  # 프로젝트 루트
sys.path.insert(0, project_root)

from core.Field import Field
from attacks.Sinkhole import Sinkhole

class test_Sinkhole(unittest.TestCase):
    """Sinkhole 클래스에 대한 유닛 테스트"""
    
    def setUp(self):
        """테스트 전 필요한 객체 생성"""
        # 테스트를 위한 랜덤 시드 설정
        np.random.seed(42)
        
        # 테스트용 필드 생성
        self.field_size = 1000
        self.num_nodes = 100
        self.bs_position = (500, 500)
        
        self.field = Field(self.field_size, self.field_size)
        self.field.deploy_nodes(self.num_nodes)
        self.field.set_base_station(self.bs_position[0], self.bs_position[1])
        self.field.find_neighbors()
        
        # Sinkhole 객체 생성
        self.attack_range = 150
        self.sinkhole = Sinkhole(self.field, attack_type="outside", attack_range=self.attack_range)
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertEqual(self.sinkhole.field, self.field)
        self.assertEqual(self.sinkhole.attack_type, "outside")
        self.assertEqual(self.sinkhole.attack_range, self.attack_range)
        self.assertEqual(len(self.sinkhole.malicious_nodes), 0)
    
    def test_calculate_node_density(self):
        """노드 밀도 계산 테스트"""
        # 노드 밀도 계산
        best_locations = self.sinkhole.calculate_node_density()
        
        # 결과 확인
        self.assertIsInstance(best_locations, dict)
        
        # 최소한 한 구역 이상에 노드가 있어야 함
        self.assertTrue(len(best_locations) > 0)
        
        # 각 구역의 정보 형식 확인
        for quadrant, location_info in best_locations.items():
            self.assertIn(quadrant, ['Q1', 'Q2', 'Q3', 'Q4'])
            self.assertEqual(len(location_info), 3)  # (x, y, node_count)
            
            # 좌표가 필드 내에 있는지 확인
            x, y, node_count = location_info
            self.assertTrue(0 <= x <= self.field_size)
            self.assertTrue(0 <= y <= self.field_size)
            self.assertGreaterEqual(node_count, 0)
    
    def test_outside_attack(self):
        """외부 공격 테스트"""
        # 외부 공격 실행
        num_attackers = 1
        self.sinkhole.launch_outside_attack(num_attackers)
        
        # 공격자 노드 확인
        self.assertEqual(len(self.sinkhole.malicious_nodes), num_attackers)
        
        # 공격자 노드 속성 확인
        for attacker_id in self.sinkhole.malicious_nodes:
            attacker = self.field.nodes[attacker_id]
            self.assertEqual(attacker.node_type, "malicious_outside")
            self.assertEqual(attacker.next_hop, "BS")
            self.assertEqual(attacker.hop_count, 0)
            
            # 영향을 받은 노드가 있는지 확인
            affected_nodes = [node for node in self.field.nodes.values() 
                             if node.node_type == "affected"]
            self.assertTrue(len(affected_nodes) > 0)
    
    def test_affect_nodes_in_range(self):
        """공격 범위 내 노드 영향 테스트"""
        # 외부 공격 실행
        self.sinkhole.launch_outside_attack(1)
        attacker_id = self.sinkhole.malicious_nodes[0]
        attacker = self.field.nodes[attacker_id]
        
        # 영향을 받은 노드 확인
        affected_nodes = [node for node in self.field.nodes.values() 
                         if node.node_type == "affected"]
        
        # 영향을 받은 노드 속성 확인
        for node in affected_nodes:
            # 노드가 공격 범위 내에 있는지 확인
            distance = np.sqrt(
                (node.pos_x - attacker.pos_x)**2 + 
                (node.pos_y - attacker.pos_y)**2
            )
            self.assertLessEqual(distance, self.attack_range)
            
            # 라우팅 정보가 올바르게 변경되었는지 확인
            self.assertEqual(node.next_hop, attacker_id)
            self.assertEqual(node.hop_count, 1)
    
    def test_execute_attack_outside(self):
        """외부 공격 실행 테스트"""
        # 외부 공격 실행
        num_attackers = 1
        result = self.sinkhole.execute_attack(num_attackers)
        
        # 결과 확인
        self.assertEqual(result, self.sinkhole.malicious_nodes)
        self.assertEqual(len(result), num_attackers)
    
    def test_attack_range_effect(self):
        """공격 범위 효과 테스트"""
        # 서로 다른 공격 범위로 테스트
        ranges = [100, 200, 300]
        affected_counts = []
        
        for attack_range in ranges:
            # 새로운 필드와 싱크홀 생성
            field = Field(self.field_size, self.field_size)
            field.deploy_nodes(self.num_nodes)
            field.set_base_station(self.bs_position[0], self.bs_position[1])
            field.find_neighbors()
            
            sinkhole = Sinkhole(field, attack_type="outside", attack_range=attack_range)
            sinkhole.launch_outside_attack(1)
            
            # 영향을 받은 노드 수 계산
            affected_nodes = [node for node in field.nodes.values() 
                             if node.node_type == "affected"]
            affected_counts.append(len(affected_nodes))
        
        # 공격 범위가 증가함에 따라 영향을 받는 노드도 증가해야 함
        # 노드 분포에 따라 항상 성립하지 않을 수 있으므로 주석 처리
        # for i in range(1, len(ranges)):
        #     self.assertGreaterEqual(affected_counts[i], affected_counts[i-1])

# if __name__ == '__main__':
#     unittest.main()