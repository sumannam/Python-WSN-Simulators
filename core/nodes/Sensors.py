class Sensors:
    """Sensors의 기본 노드 특성을 정의하는 기본 클래스"""
    def __init__(self, node_id: int, pos_x: float, pos_y: float):
        # 노드 기본 설정
        self.node_id = node_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        # 기본 설정
        self.status = "active"  # active/inactive
        self.node_type = "normal"  # normal/malicious_inside/malicious_outside/affected
        
        # 통신 속성
        self.neighbors = []  # 이웃 노드 ID 리스트
        self.neighbor_nodes = []  # 이웃 노드 ID 리스트 (backward compatibility)
        self.next_hop = None  # 다음 홉 (라우팅)
        self.hop_count = float('inf')  # 베이스스테이션까지의 홉 수
        self.route_changes = 0  # 라우팅 경로 변경 횟수
        self.distance_to_bs = 0  # 베이스스테이션까지의 거리        
        
        # 패킷 카운터 초기화 - 모든 노드가 기본적으로 이 속성을 가지도록 함
        self.tx_count = 0  # 전송 패킷 카운터
        self.rx_count = 0  # 수신 패킷 카운터
        
        
    def get_location(self) -> tuple:
        """노드의 위치 반환"""
        return (self.pos_x, self.pos_y)


    def calculate_distance_to_bs(self, bs_x: float, bs_y: float) -> float:
        """베이스스테이션까지의 거리 계산"""
        from math import sqrt
        self.distance_to_bs = sqrt((self.pos_x - bs_x)**2 + (self.pos_y - bs_y)**2)
        return self.distance_to_bs

    def get_node_info(self) -> dict:
        """노드의 기본 정보 반환"""
        return {
            "node_id": self.node_id,
            "location": self.get_location(),
            "status": self.status,
            "node_type": self.node_type,
            "network_info": self.get_network_info()
        }

    def get_node_state_dict(self) -> dict:
        """노드의 기본 정보 반환"""
        return {
            'node_id': self.node_id,
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'status': self.status,
            'node_type': self.node_type,
            'hop_count': self.hop_count,
            'next_hop': self.next_hop,
            'neighbor_nodes': len(self.neighbor_nodes),
            'route_changes': self.route_changes,
            'distance_to_bs': self.distance_to_bs,
            'tx_count': self.tx_count,
            'rx_count': self.rx_count            
        }