import unittest
import sys
import os
import math

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)  # test_core의 상위 디렉토리 (test)
project_root = os.path.dirname(test_dir)  # test의 상위 디렉토리 (프로젝트 루트)
sys.path.insert(0, project_root)

from core.nodes.MicazMotes import MicazMotes

class test_MicazMotes(unittest.TestCase):
    """MicazMotes 클래스에 대한 유닛 테스트"""
    
    def setUp(self):
        """테스트 전 필요한 객체 생성"""
        # 테스트용 MicazMotes 인스턴스 생성
        self.node_id = 1
        self.pos_x = 100.0
        self.pos_y = 200.0
        self.node = MicazMotes(self.node_id, self.pos_x, self.pos_y)
    
    def test_initialization(self):
        """초기화 테스트"""
        # 노드 기본 정보 확인
        self.assertEqual(self.node.node_id, self.node_id)
        self.assertEqual(self.node.pos_x, self.pos_x)
        self.assertEqual(self.node.pos_y, self.pos_y)
        
        # 초기 상태 확인
        self.assertEqual(self.node.status, "active")
        self.assertEqual(self.node.node_type, "normal")
        
        # 통신 속성 확인
        self.assertEqual(self.node.comm_range, 100)  # 100m
        self.assertEqual(self.node.data_rate, 250000)  # 250kbps
        
        # 전원 특성 확인
        self.assertEqual(self.node.voltage, 3.0)
        self.assertEqual(self.node.tx_current, 0.0174)
        self.assertEqual(self.node.rx_current, 0.0197)
        
        # 에너지 관련 확인
        self.assertEqual(self.node.initial_energy, 1)  # 1 Joule
        self.assertEqual(self.node.energy_level, self.node.initial_energy)
        self.assertEqual(self.node.consumed_energy_tx, 0)
        self.assertEqual(self.node.consumed_energy_rx, 0)
        self.assertEqual(self.node.total_consumed_energy, 0)
        
        # 패킷 카운터 확인
        self.assertEqual(self.node.tx_count, 0)
        self.assertEqual(self.node.rx_count, 0)
    
    def test_power_calculation(self):
        """전력 계산 테스트"""
        # 전력 계산이 올바르게 되었는지 확인
        expected_tx_power = self.node.voltage * self.node.tx_current
        expected_rx_power = self.node.voltage * self.node.rx_current
        
        self.assertEqual(self.node.tx_power, expected_tx_power)
        self.assertEqual(self.node.rx_power, expected_rx_power)
    
    def test_packet_time_calculation(self):
        """패킷 전송 시간 계산 테스트"""
        # 다양한 패킷 크기에 대한 전송 시간 계산 확인
        packet_sizes = [32, 64, 128]
        
        for size in packet_sizes:
            expected_time = (size * 8) / self.node.data_rate  # bits / bits per second
            calculated_time = self.node.calculate_packet_time(size)
            self.assertEqual(calculated_time, expected_time)
    
    def test_transmit_packet(self):
        """패킷 전송 및 에너지 소비 테스트"""
        # 패킷 전송 전 초기 상태 확인
        initial_energy = self.node.energy_level
        
        # 패킷 전송
        packet_size = 32
        energy_consumed = self.node.transmit_packet(packet_size)
        
        # 전송 후 상태 확인
        self.assertEqual(self.node.tx_count, 1)
        self.assertGreater(energy_consumed, 0)
        self.assertEqual(self.node.consumed_energy_tx, energy_consumed)
        self.assertEqual(self.node.total_consumed_energy, energy_consumed)
        self.assertEqual(self.node.energy_level, initial_energy - energy_consumed)
    
    def test_receive_packet(self):
        """패킷 수신 및 에너지 소비 테스트"""
        # 패킷 수신 전 초기 상태 확인
        initial_energy = self.node.energy_level
        
        # 패킷 수신
        packet_size = 32
        energy_consumed = self.node.receive_packet(packet_size)
        
        # 수신 후 상태 확인
        self.assertEqual(self.node.rx_count, 1)
        self.assertGreater(energy_consumed, 0)
        self.assertEqual(self.node.consumed_energy_rx, energy_consumed)
        self.assertEqual(self.node.total_consumed_energy, energy_consumed)
        self.assertEqual(self.node.energy_level, initial_energy - energy_consumed)
    
    def test_multiple_packets(self):
        """다중 패킷 전송/수신 테스트"""
        initial_energy = self.node.energy_level
        total_energy_consumed = 0
        
        # 여러 패킷 전송
        for _ in range(5):
            energy = self.node.transmit_packet(32)
            total_energy_consumed += energy
        
        # 여러 패킷 수신
        for _ in range(3):
            energy = self.node.receive_packet(32)
            total_energy_consumed += energy
        
        # 상태 확인
        self.assertEqual(self.node.tx_count, 5)
        self.assertEqual(self.node.rx_count, 3)
        self.assertAlmostEqual(self.node.total_consumed_energy, total_energy_consumed, places=10)
        self.assertAlmostEqual(self.node.energy_level, initial_energy - total_energy_consumed, places=10)
    
    def test_node_deactivation(self):
        """에너지 소진 시 노드 비활성화 테스트"""
        # 노드 에너지 레벨을 매우 낮게 설정
        self.node.energy_level = 0.000001  # 거의 0에 가까운 값
        
        # 패킷 전송으로 남은 에너지 소진
        self.node.transmit_packet(32)
        
        # 노드 상태 확인
        self.assertEqual(self.node.status, "inactive")
        
        # 비활성화된 노드는 추가 에너지를 소비하지 않음
        old_energy = self.node.energy_level
        old_consumed = self.node.total_consumed_energy
        
        self.node.transmit_packet(32)
        self.node.receive_packet(32)
        
        self.assertEqual(self.node.energy_level, old_energy)
        self.assertEqual(self.node.total_consumed_energy, old_consumed)
    
    def test_neighbor_management(self):
        """이웃 노드 관리 테스트"""
        # 초기에는 이웃이 없어야 함
        self.assertEqual(len(self.node.neighbor_nodes), 0)
        
        # 이웃 추가
        neighbor_ids = [2, 3, 4]
        for neighbor_id in neighbor_ids:
            self.node.add_neighbor(neighbor_id)
        
        # 이웃 확인
        self.assertEqual(len(self.node.neighbor_nodes), len(neighbor_ids))
        for neighbor_id in neighbor_ids:
            self.assertIn(neighbor_id, self.node.neighbor_nodes)
        
        # 이웃 제거
        self.node.remove_neighbor(3)
        self.assertEqual(len(self.node.neighbor_nodes), len(neighbor_ids) - 1)
        self.assertNotIn(3, self.node.neighbor_nodes)
        
        # 존재하지 않는 이웃 제거 시도
        original_neighbors = self.node.neighbor_nodes.copy()
        self.node.remove_neighbor(99)
        self.assertEqual(self.node.neighbor_nodes, original_neighbors)
    
    def test_get_energy_info(self):
        """에너지 정보 확인 테스트"""
        # 기본 에너지 정보 확인
        energy_info = self.node.get_energy_info()
        
        self.assertIn('current_energy', energy_info)
        self.assertIn('energy_percentage', energy_info)
        self.assertIn('tx_power', energy_info)
        self.assertIn('rx_power', energy_info)
        
        # 값 정확성 확인
        self.assertEqual(energy_info['current_energy'], self.node.energy_level)
        self.assertEqual(energy_info['energy_percentage'], 100.0)  # 초기 상태는 100%
        self.assertEqual(energy_info['tx_power'], self.node.tx_power)
        self.assertEqual(energy_info['rx_power'], self.node.rx_power)
        
        # 에너지 소비 후 정보 변화 확인
        self.node.transmit_packet(32)
        updated_info = self.node.get_energy_info()
        
        self.assertLess(updated_info['current_energy'], self.node.initial_energy)
        self.assertLess(updated_info['energy_percentage'], 100.0)
    
    def test_get_node_state_dict(self):
        """노드 상태 딕셔너리 확인 테스트"""
        # 초기 상태 확인
        state_dict = self.node.get_node_state_dict()
        
        # 필수 키 확인
        expected_keys = [
            'node_id', 'pos_x', 'pos_y', 'status', 'node_type',
            'energy_level', 'initial_energy', 'energy_percentage',
            'consumed_energy_tx', 'consumed_energy_rx', 'total_consumed_energy',
            'tx_count', 'rx_count', 'tx_power', 'rx_power',
            'hop_count', 'node_type'
        ]
        
        for key in expected_keys:
            self.assertIn(key, state_dict)
        
        # 값 일치 확인
        self.assertEqual(state_dict['node_id'], self.node_id)
        self.assertEqual(state_dict['pos_x'], self.pos_x)
        self.assertEqual(state_dict['pos_y'], self.pos_y)
        self.assertEqual(state_dict['status'], "active")
        self.assertEqual(state_dict['energy_level'], self.node.energy_level)
        self.assertEqual(state_dict['tx_count'], 0)
        self.assertEqual(state_dict['rx_count'], 0)

# if __name__ == '__main__':
#     unittest.main()