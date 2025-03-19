import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# Field 클래스와 MicazMotes 클래스 임포트
from core.Field import Field
from core.nodes.MicazMotes import MicazMotes

class test_Field(unittest.TestCase):
    """
    이 클래스는 Field 클래스의 기능을 테스트합니다.
    """

    def setUp(self):
        """
        테스트 환경을 설정합니다.
        """
        self.field = Field(100.0, 100.0)

    def test_init(self):
        """
        필드 초기화를 테스트합니다.
        
        이 테스트는 Field 클래스의 생성자가 올바르게 작동하는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        self.assertEqual(self.field.width, 100.0)
        self.assertEqual(self.field.height, 100.0)
        self.assertEqual(self.field.nodes, {})
        self.assertIsNone(self.field.base_station)

    @patch('numpy.random.uniform')
    def test_deploy_nodes(self, mock_uniform):
        """
        노드 배치 기능을 테스트합니다.
        
        이 테스트는 균등 분포로 노드가 올바르게 배치되는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # numpy.random.uniform 모의 설정
        mock_uniform.side_effect = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        
        # 노드 배치
        self.field.deploy_nodes(3)
        
        # 노드 수 확인
        self.assertEqual(len(self.field.nodes), 3)
        
        # 노드 위치 확인
        self.assertEqual(self.field.nodes[1].pos_x, 10.0)
        self.assertEqual(self.field.nodes[1].pos_y, 20.0)
        self.assertEqual(self.field.nodes[2].pos_x, 30.0)
        self.assertEqual(self.field.nodes[2].pos_y, 40.0)
        self.assertEqual(self.field.nodes[3].pos_x, 50.0)
        self.assertEqual(self.field.nodes[3].pos_y, 60.0)
        
        # 노드 ID 확인
        self.assertIn(1, self.field.nodes)
        self.assertIn(2, self.field.nodes)
        self.assertIn(3, self.field.nodes)
        
        # MicazMotes 타입 확인
        for node in self.field.nodes.values():
            self.assertIsInstance(node, MicazMotes)

    def test_set_base_station(self):
        """
        베이스 스테이션 설정 기능을 테스트합니다.
        
        이 테스트는 베이스 스테이션 설정 시 모든 노드가 베이스 스테이션까지의 거리를 
        계산하는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # 노드 생성
        node1 = MagicMock()
        node2 = MagicMock()
        
        self.field.nodes = {1: node1, 2: node2}
        
        # 베이스 스테이션 설정
        self.field.set_base_station(50.0, 50.0)
        
        # 베이스 스테이션 위치 확인
        self.assertEqual(self.field.base_station, {"x": 50.0, "y": 50.0})
        
        # 각 노드에서 베이스 스테이션까지 거리 계산 호출 확인
        node1.calculate_distance_to_bs.assert_called_once_with(50.0, 50.0)
        node2.calculate_distance_to_bs.assert_called_once_with(50.0, 50.0)

    def test_find_neighbors(self):
        """
        이웃 노드 찾기 기능을 테스트합니다.
        
        이 테스트는 각 노드의 통신 범위 내에 있는 노드들이 이웃으로 
        올바르게 설정되는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # 테스트용 노드 생성
        node1 = MicazMotes(1, 10.0, 10.0)
        node2 = MicazMotes(2, 15.0, 15.0)  # node1과 근접 (범위 내)
        node3 = MicazMotes(3, 150.0, 150.0)  # node1과 멀리 떨어짐 (범위 밖)
        
        self.field.nodes = {1: node1, 2: node2, 3: node3}
        
        # 기본 통신 범위와 노드 간 거리 계산
        comm_range = node1.comm_range
        dist_1_to_2 = np.sqrt((10.0 - 15.0)**2 + (10.0 - 15.0)**2)
        
        # 이웃 노드 찾기
        self.field.find_neighbors()
        
        # node1의 이웃 확인
        if dist_1_to_2 <= comm_range:
            self.assertIn(2, node1.neighbor_nodes)
        else:
            self.assertNotIn(2, node1.neighbor_nodes)
            
        # print(f"통신 범위: {node1.comm_range}")
        # print(f"노드 1과 노드 3 사이의 거리: {np.sqrt((10.0 - 60.0)**2 + (10.0 - 60.0)**2)}")
            
        self.assertNotIn(3, node1.neighbor_nodes)  # 거리가 멀어 이웃이 아님
        
        # node2의 이웃 확인
        if dist_1_to_2 <= comm_range:
            self.assertIn(1, node2.neighbor_nodes)
        else:
            self.assertNotIn(1, node2.neighbor_nodes)

    def test_find_unconnected_nodes(self):
        """
        연결되지 않은 노드 찾기 기능을 테스트합니다.
        
        이 테스트는 next_hop이 없는 노드들이 올바르게 식별되는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # 테스트용 노드 생성
        node1 = MicazMotes(1, 10.0, 10.0)
        node1.next_hop = 2  # 연결된 노드
        
        node2 = MicazMotes(2, 20.0, 20.0)
        node2.next_hop = None  # 연결되지 않은 노드
        node2.neighbor_nodes = [1]  # 이웃 추가
        
        node3 = MicazMotes(3, 30.0, 30.0)
        node3.next_hop = None  # 연결되지 않은 노드
        node3.neighbor_nodes = [1, 2]  # 이웃 추가
        
        self.field.nodes = {1: node1, 2: node2, 3: node3}
        
        # 연결되지 않은 노드 찾기
        unconnected = self.field.find_unconnected_nodes()
        
        # 결과 확인
        self.assertEqual(len(unconnected), 2)
        
        # node2 확인
        node2_info = next(n for n in unconnected if n['node_id'] == 2)
        self.assertEqual(node2_info['position'], (20.0, 20.0))
        self.assertEqual(node2_info['neighbor_count'], 1)
        
        # node3 확인
        node3_info = next(n for n in unconnected if n['node_id'] == 3)
        self.assertEqual(node3_info['position'], (30.0, 30.0))
        self.assertEqual(node3_info['neighbor_count'], 2)

    def test_get_network_stats(self):
        """
        네트워크 상태 정보 기능을 테스트합니다.
        
        이 테스트는 네트워크의 전체 노드 수, 활성 노드 수, 평균 이웃 수가 
        올바르게 계산되는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # 테스트용 노드 생성
        node1 = MicazMotes(1, 10.0, 10.0)
        node1.status = "active"
        node1.neighbor_nodes = [2, 3]
        
        node2 = MicazMotes(2, 20.0, 20.0)
        node2.status = "active"
        node2.neighbor_nodes = [1]
        
        node3 = MicazMotes(3, 30.0, 30.0)
        node3.status = "inactive"
        node3.neighbor_nodes = [1]
        
        self.field.nodes = {1: node1, 2: node2, 3: node3}
        
        # 네트워크 상태 가져오기
        stats = self.field.get_network_stats()
        
        # 결과 확인
        self.assertEqual(stats["total_nodes"], 3)
        self.assertEqual(stats["active_nodes"], 2)
        self.assertEqual(stats["average_neighbors"], (2 + 1 + 1) / 3)

    def test_create_node(self):
        """
        노드 생성 기능을 테스트합니다.
        
        이 테스트는 create_node 메서드가 MicazMotes 인스턴스를 
        올바르게 생성하고 반환하는지 확인합니다.
        
        :작성일: 2025.03.12
        """
        # 노드 생성
        node = self.field.create_node(4, 40.0, 40.0)
        
        # 반환된 노드 속성 확인
        self.assertEqual(node.node_id, 4)
        self.assertEqual(node.pos_x, 40.0)
        self.assertEqual(node.pos_y, 40.0)
        
        # 클래스 이름으로 확인 (타입 비교 대신)
        self.assertEqual(node.__class__.__name__, 'MicazMotes')