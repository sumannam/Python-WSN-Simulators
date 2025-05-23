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
        from nodes.MicazMotes import MicazMotes
        return MicazMotes(node_id, pos_x, pos_y)

    def find_path(self, source_id, target_id):
        """두 노드 사이의 최단 경로를 찾는 메소드"""
        if source_id not in self.nodes or (target_id != "BS" and target_id not in self.nodes):
            return None
            
        # BFS를 사용하여 최단 경로 찾기
        queue = [(source_id, [source_id])]
        visited = set([source_id])
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == target_id:
                return path
                
            current_node = self.nodes[current_id]
            for neighbor_id in current_node.neighbors:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
                    
        return None

    def calculate_distance(self, node1_id, node2_id):
        """두 노드 사이의 거리를 계산하는 메소드"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return float('inf')
            
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        
        return ((node1.pos_x - node2.pos_x)**2 + (node1.pos_y - node2.pos_y)**2)**0.5