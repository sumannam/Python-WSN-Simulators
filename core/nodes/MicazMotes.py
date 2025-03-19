from core.nodes.Sensors import Sensors

class MicazMotes(Sensors):
   def __init__(self, node_id: int, pos_x: float, pos_y: float):
       super().__init__(node_id, pos_x, pos_y)
       
       # 하드웨어 특성
       self.comm_range = 100  # 실외환경 기준 (100m)
       self.data_rate = 250000  # 250kbps
       
       # 전원 특성 (V, A 단위)
       self.voltage = 3.0  # 2.7V ~ 3.3V 중간값
       self.tx_current = 0.0174  # 17.4mA = 0.0174A
       self.rx_current = 0.0197  # 19.7mA = 0.0197A
       self.sleep_current = 0.000001  # 1μA = 0.000001A
       
       # 전력 계산 (W = V * A)
       self._calculate_power_consumption()
       
       # 에너지 관리 (Joule = Wh * 3600)
       battery_wh = 2 * 2.6  # 2개의 AA 배터리, 각 2.6Wh
    #    self.initial_energy = battery_wh * 3600  # 변환: Wh -> Joules
       self.initial_energy = 1 # 1 Joule
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

   def _calculate_power_consumption(self):
       """전력 소비량 계산 (Watts = V * A)"""
       self.tx_power = self.voltage * self.tx_current  # W
       self.rx_power = self.voltage * self.rx_current  # W
       self.sleep_power = self.voltage * self.sleep_current  # W

   def calculate_packet_time(self, packet_size_bytes: int) -> float:
       """패킷 전송 시간 계산 (seconds)"""
       return (packet_size_bytes * 8) / self.data_rate

   def transmit_packet(self, packet_size_bytes: int = 32) -> float:
       """패킷 전송 및 에너지 소비 계산 (Joules = W * s)"""
       if self.status == "inactive":
           return 0
           
       packet_time = self.calculate_packet_time(packet_size_bytes)
       energy_consumed = self.tx_power * packet_time  # Joules
       
       self.energy_level -= energy_consumed
       self.consumed_energy_tx += energy_consumed
       self.total_consumed_energy += energy_consumed
       self.tx_count += 1
       
       if self.energy_level <= 0:
           self.status = "inactive"
           
       return energy_consumed

   def receive_packet(self, packet_size_bytes: int = 32) -> float:
       """패킷 수신 및 에너지 소비 계산 (Joules = W * s)"""
       if self.status == "inactive":
           return 0
           
       packet_time = self.calculate_packet_time(packet_size_bytes)
       energy_consumed = self.rx_power * packet_time  # Joules
       
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
           "tx_power": self.tx_power,
           "rx_power": self.rx_power,
           "sleep_power": self.sleep_power
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
        'tx_power': energy_info['tx_power'],
        'rx_power': energy_info['rx_power'],
        'hop_count': self.hop_count,  # hop_count 추가
        'node_type': self.node_type   # node_type 추가
    })
    
    return base_info