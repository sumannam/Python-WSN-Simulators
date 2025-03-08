class Sensors:
    """Sensors의 기본 노드 특성을 정의하는 기본 클래스"""
    def __init__(self, node_id: int, pos_x: float, pos_y: float):
        # 기본 노드 속성
        self.node_id = node_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.status = "active"     # active, inactive
        
        # 네트워크 속성
        self.node_type = "normal"  # normal, malicious
        self.hop_count = 0
        self.neighbor_nodes = []   
        self.next_hop = None       
        self.route_changes = 0     
        self.distance_to_bs = 0    
        
        # 통신 카운터
        self.tx_count = 0          
        self.rx_count = 0          

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
            'distance_to_bs': self.distance_to_bs
        }