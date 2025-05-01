from core.nodes.Sensors import Sensors

class MicazMotes(Sensors):
   def __init__(self, node_id: int, pos_x: float, pos_y: float):
       super().__init__(node_id, pos_x, pos_y)
       
       # 하드웨어 특성
       self.comm_range = 100  # 실외환경 기준 (100m)
       self.data_rate = 250000  # 250kbps
       
       # 에너지 소비량 (Joule 단위)
       self.tx_energy_per_byte = 16.25e-6  # 16.25 µJ per byte
       self.rx_energy_per_byte = 12.5e-6   # 12.5 µJ per byte
       
       # 에너지 관리
       self.initial_energy = 1  # 1 Joule
       self.energy_level = self.initial_energy
       self.consumed_energy_tx = 0  # Joules
       self.consumed_energy_rx = 0  # Joules
       self.total_consumed_energy = 0  # Joules

   def add_neighbor(self, neighbor_id: int):
       """이웃 노드 추가"""
       if neighbor_id not in self.neighbor_nodes:
           self.neighbor_nodes.append(neighbor_id)
           
   def remove_neighbor(self, neighbor_id: int):
       """이웃 노드 제거"""
       if neighbor_id in self.neighbor_nodes:
           self.neighbor_nodes.remove(neighbor_id)

   def calculate_packet_time(self, packet_size_bytes: int) -> float:
       """패킷 전송 시간 계산 (seconds)"""
       return (packet_size_bytes * 8) / self.data_rate

   def transmit_packet(self, packet_size_bytes: int = 32) -> float:
       """패킷 전송 및 에너지 소비 계산 (Joules)"""
       if self.status == "inactive":
           return 0
           
       energy_consumed = self.tx_energy_per_byte * packet_size_bytes  # Joules
       
       self.energy_level -= energy_consumed
       self.consumed_energy_tx += energy_consumed
       self.total_consumed_energy += energy_consumed
       self.tx_count += 1
       
       if self.energy_level <= 0:
           self.status = "inactive"
           
       return energy_consumed

   def receive_packet(self, packet_size_bytes: int = 32) -> float:
       """패킷 수신 및 에너지 소비 계산 (Joules)"""
       if self.status == "inactive":
           return 0
           
       energy_consumed = self.rx_energy_per_byte * packet_size_bytes  # Joules
       
       self.energy_level -= energy_consumed
       self.consumed_energy_rx += energy_consumed
       self.total_consumed_energy += energy_consumed
       self.rx_count += 1
       
       if self.energy_level <= 0:
           self.status = "inactive"
           
       return energy_consumed

   def get_energy_info(self) -> dict:
       """에너지 관련 정보 반환"""
       return {
           "current_energy": self.energy_level,
           "energy_percentage": (self.energy_level / self.initial_energy) * 100,
           "tx_energy_per_byte": self.tx_energy_per_byte,
           "rx_energy_per_byte": self.rx_energy_per_byte
       }
   
   def get_node_state_dict(self) -> dict:
    """노드의 현재 상태 정보를 딕셔너리로 반환"""
    base_info = super().get_node_state_dict()  # 부모 클래스의 기본 정보 가져오기
    energy_info = self.get_energy_info()
    
    # 기본 정보 업데이트 및 확장
    base_info.update({
        'energy_level': self.energy_level,
        'initial_energy': self.initial_energy,
        'energy_percentage': energy_info['energy_percentage'],
        'consumed_energy_tx': self.consumed_energy_tx,
        'consumed_energy_rx': self.consumed_energy_rx,
        'total_consumed_energy': self.total_consumed_energy,
        'tx_count': self.tx_count,
        'rx_count': self.rx_count,
        'tx_energy_per_byte': energy_info['tx_energy_per_byte'],
        'rx_energy_per_byte': energy_info['rx_energy_per_byte'],
        'hop_count': self.hop_count,
        'node_type': self.node_type
    })
    
    return base_info