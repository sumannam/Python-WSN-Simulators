from Sensors import Sensors

class MicazMotes(Sensors):
    def __init__(self, node_id: int, pos_x: float, pos_y: float):
        super().__init__(node_id, pos_x, pos_y)
        
        # 하드웨어 특성
        self.comm_range = 100  # 실외환경 기준 (50m)
        self.data_rate = 250000  # 250kbps
        
        # 전원 특성
        self.voltage = 3.0  # 2.7V ~ 3.3V 중간값
        self.tx_current = 0.0174  # 17.4mA
        self.rx_current = 0.0197  # 19.7mA
        self.sleep_current = 0.000001  # 1μA
        
        # 전력 계산
        self._calculate_power_consumption()
        
        # 에너지 관리
        self.initial_energy = 18720  # 2 * 2.6Wh * 3600s
        self.energy_level = self.initial_energy
        
        # 이웃 노드 관리
        self.neighbor_nodes = []

    def add_neighbor(self, neighbor_id: int):
        """이웃 노드 추가"""
        if neighbor_id not in self.neighbor_nodes:
            self.neighbor_nodes.append(neighbor_id)
            
    def remove_neighbor(self, neighbor_id: int):
        """이웃 노드 제거"""
        if neighbor_id in self.neighbor_nodes:
            self.neighbor_nodes.remove(neighbor_id)

    def _calculate_power_consumption(self):
        """전력 소비량 계산"""
        self.tx_power = self.voltage * self.tx_current
        self.rx_power = self.voltage * self.rx_current
        self.sleep_power = self.voltage * self.sleep_current

    def calculate_packet_time(self, packet_size_bytes: int) -> float:
        """패킷 전송 시간 계산"""
        return (packet_size_bytes * 8) / self.data_rate

    def transmit_packet(self, packet_size_bytes: int = 32) -> float:
        """패킷 전송 및 에너지 소비 계산"""
        if self.status == "inactive":
            return 0
            
        packet_time = self.calculate_packet_time(packet_size_bytes)
        energy_consumed = self.tx_power * packet_time
        
        self.energy_level -= energy_consumed
        self.tx_count += 1
        
        if self.energy_level <= 0:
            self.status = "inactive"
            
        return energy_consumed

    def receive_packet(self, packet_size_bytes: int = 32) -> float:
        """패킷 수신 및 에너지 소비 계산"""
        if self.status == "inactive":
            return 0
            
        packet_time = self.calculate_packet_time(packet_size_bytes)
        energy_consumed = self.rx_power * packet_time
        
        self.energy_level -= energy_consumed
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