import numpy as np
from core.nodes.MicazMotes import MicazMotes

class Field:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.nodes = {}
        self.base_station = None

    def deploy_nodes(self, num_nodes: int):
        """균등 분포로 노드 배치"""
        for node_id in range(1, num_nodes + 1):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            new_node = MicazMotes(node_id, x, y)
            self.nodes[node_id] = new_node

    def set_base_station(self, x: float, y: float):
        """베이스 스테이션 설정"""
        self.base_station = {"x": x, "y": y}
        for node in self.nodes.values():
            node.calculate_distance_to_bs(x, y)

    def find_neighbors(self):
        """각 노드의 이웃 노드 찾기"""
        for node_id, node in self.nodes.items():
            for other_id, other_node in self.nodes.items():
                if node_id != other_id:
                    distance = np.sqrt(
                        (node.pos_x - other_node.pos_x)**2 + 
                        (node.pos_y - other_node.pos_y)**2
                    )
                    if distance <= node.comm_range:
                        node.add_neighbor(other_id)

    def find_unconnected_nodes(self):
        """다음 홉이 없는 노드 찾기"""
        unconnected_nodes = []
        for node_id, node in self.nodes.items():
            if node.next_hop is None:
                unconnected_nodes.append({
                    'node_id': node_id,
                    'position': (node.pos_x, node.pos_y),
                    'neighbor_count': len(node.neighbor_nodes)
                })
        return unconnected_nodes

    def get_network_stats(self):
        """네트워크 상태 정보 반환"""
        total_nodes = len(self.nodes)
        active_nodes = sum(1 for node in self.nodes.values() if node.status == "active")
        avg_neighbors = np.mean([len(node.neighbor_nodes) for node in self.nodes.values()])
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "average_neighbors": avg_neighbors
        }
    
    def create_node(self, node_id: int, pos_x: float, pos_y: float):
        """새로운 센서 노드 생성"""
        from MicazMotes import MicazMotes
        return MicazMotes(node_id, pos_x, pos_y)