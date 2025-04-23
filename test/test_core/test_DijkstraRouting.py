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
from core.routing.DijkstraRouting import DijkstraRouting

class test_DijkstraRouting(unittest.TestCase):
    """DijkstraRouting 클래스에 대한 유닛 테스트"""
    
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
        
        # DijkstraRouting 객체 생성
        self.routing = DijkstraRouting(self.field)
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertEqual(self.routing.field, self.field)
        self.assertIsNotNone(self.routing.routing_table)
    
    def test_setup_routing(self):
        """라우팅 설정 테스트"""
        # 라우팅 설정
        self.routing.setup_routing()
        
        # 모든 노드가 라우팅 테이블에 있는지 확인
        for node_id in self.field.nodes:
            self.assertIn(node_id, self.routing.routing_table)
        
        # BS와 직접 연결된 노드 확인
        direct_connections = [node_id for node_id, next_hop in self.routing.routing_table.items() 
                            if next_hop == "BS"]
        self.assertTrue(len(direct_connections) > 0)
    
    def test_connect_direct_to_bs(self):
        """BS와 직접 연결 테스트"""
        # BS와 직접 연결 가능한 노드들 처리
        self.routing.connect_nodes_directly_to_bs()
        
        # 직접 연결된 노드 확인
        direct_connections = [node_id for node_id, next_hop in self.routing.routing_table.items() 
                            if next_hop == "BS"]
        
        # 직접 연결된 노드들이 BS와의 거리가 통신 범위 내에 있는지 확인
        for node_id in direct_connections:
            node = self.field.nodes[node_id]
            distance = np.sqrt((node.pos_x - self.bs_position[0])**2 + 
                             (node.pos_y - self.bs_position[1])**2)
            self.assertLessEqual(distance, node.comm_range)
    
    # def test_apply_dijkstra(self):
    #     """Dijkstra 알고리즘 적용 테스트"""
    #     # 라우팅 설정
    #     self.routing.setup_routing()
        
    #     # 모든 노드가 BS에 연결되어 있는지 확인
    #     for node_id in self.field.nodes:
    #         self.assertIn(node_id, self.routing.routing_table)
    #         next_hop = self.routing.routing_table[node_id]
            
    #         # next_hop이 None이 아니어야 함
    #         self.assertIsNotNone(next_hop)
            
    #         # next_hop이 "BS"이거나 다른 노드 ID여야 함
    #         if next_hop != "BS":
    #             self.assertIn(next_hop, self.field.nodes)
    
    def test_route_changes(self):
        """라우팅 변경 테스트"""
        # 초기 라우팅 설정
        self.routing.setup_routing()
        
        # 일부 노드의 에너지 레벨 변경
        for node_id, node in self.field.nodes.items():
            if node_id in self.routing.routing_table and self.routing.routing_table[node_id] == "BS":
                node.energy_level = 0  # 에너지 고갈
        
        # 라우팅 재설정
        self.routing.setup_routing()
        
        # 에너지가 고갈된 노드들이 다른 경로를 사용하는지 확인
        for node_id, node in self.field.nodes.items():
            if node.energy_level == 0:
                self.assertNotEqual(self.routing.routing_table[node_id], "BS")
    
    # def test_connect_nodes_iteratively(self):
    #     """반복적 노드 연결 테스트"""
    #     # 일부 노드의 통신 범위를 줄임
    #     for node in self.field.nodes.values():
    #         node.comm_range = 50  # 통신 범위 축소
        
    #     # 라우팅 설정
    #     self.routing.setup_routing()
        
    #     # 모든 노드가 연결되어 있는지 확인
    #     for node_id in self.field.nodes:
    #         self.assertIn(node_id, self.routing.routing_table)
    #         self.assertIsNotNone(self.routing.routing_table[node_id])
    
    def test_find_best_next_hop(self):
        """최적의 next hop 찾기 테스트"""
        # 테스트용 노드 생성
        node = self.field.nodes[1]  # 첫 번째 노드 사용
        
        # 최적의 next hop 찾기
        best_next_hop = self.routing._find_best_next_hop(node, set(self.field.nodes.keys()))
        
        # 결과 확인
        if best_next_hop is not None:
            self.assertIn(best_next_hop, self.field.nodes)
            neighbor = self.field.nodes[best_next_hop]
            
            # 거리 계산 (현재 노드와 이웃 노드 사이의 거리)
            distance = np.sqrt((neighbor.pos_x - node.pos_x)**2 + 
                             (neighbor.pos_y - node.pos_y)**2)
            
            # 통신 범위 내에 있어야 함
            self.assertLessEqual(distance, node.comm_range)

# if __name__ == '__main__':
#     unittest.main() 