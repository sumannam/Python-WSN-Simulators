import heapq
import numpy as np

from MicazMotes import MicazMotes

class Field:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.nodes = {}  # Dictionary to store nodes: {node_id: node_object}
        self.base_station = None

    def deploy_nodes(self, num_nodes: int):
        """균등 분포로 노드 배치"""
        # Calculate grid size for uniform distribution
        for node_id in range(1, num_nodes + 1):
            x = np.random.uniform(0, self.width)
            y = np.random.uniform(0, self.height)
            new_node = MicazMotes(node_id, x, y)
            self.nodes[node_id] = new_node

    def set_base_station(self, x: float, y: float):
        """베이스 스테이션 설정"""
        self.base_station = {"x": x, "y": y}
        
        # Update distances to base station for all nodes
        for node in self.nodes.values():
            node.calculate_distance_to_bs(x, y)

    def find_neighbors(self):
        """각 노드의 이웃 노드 찾기"""
        for node_id, node in self.nodes.items():
            for other_id, other_node in self.nodes.items():
                if node_id != other_id:
                    # Calculate distance between nodes
                    distance = np.sqrt(
                        (node.pos_x - other_node.pos_x)**2 + 
                        (node.pos_y - other_node.pos_y)**2
                    )
                    # If within communication range, add as neighbor
                    if distance <= node.comm_range:
                        node.add_neighbor(other_id)

    def setup_shortest_path_routing(self):
        """BS까지의 최단 경로 설정"""
        if not self.base_station:
            print("Base station not set. Cannot setup routing.")
            return

        bs_x = self.base_station['x']
        bs_y = self.base_station['y']

        # 모든 노드의 초기 상태를 미연결로 설정
        unconnected_nodes = set(self.nodes.keys())
        connected_nodes = set()

        # BS와 직접 연결 가능한 노드들 먼저 처리
        for node_id in list(unconnected_nodes):
            node = self.nodes[node_id]
            dist_to_bs = ((node.pos_x - bs_x)**2 + (node.pos_y - bs_y)**2)**0.5
            
            if dist_to_bs <= node.comm_range:
                node.next_hop = "BS"
                unconnected_nodes.remove(node_id)
                connected_nodes.add(node_id)

        # 나머지 노드들 처리
        while unconnected_nodes:
            nodes_connected_this_round = set()
            
            for node_id in unconnected_nodes:
                node = self.nodes[node_id]
                best_next_hop = None
                min_dist_to_bs = float('inf')

                # 연결된 이웃 노드들 중에서 최적의 next hop 찾기
                for neighbor_id in node.neighbor_nodes:
                    if neighbor_id in connected_nodes:
                        neighbor = self.nodes[neighbor_id]
                        dist_to_bs = ((neighbor.pos_x - bs_x)**2 + (neighbor.pos_y - bs_y)**2)**0.5
                        
                        if dist_to_bs < min_dist_to_bs:
                            min_dist_to_bs = dist_to_bs
                            best_next_hop = neighbor_id

                # next hop을 찾았다면 노드 연결
                if best_next_hop is not None:
                    node.next_hop = best_next_hop
                    nodes_connected_this_round.add(node_id)

            # 이번 라운드에서 연결된 노드들 업데이트
            if not nodes_connected_this_round:
                # 더 이상 연결할 수 있는 노드가 없으면
                # 통신 범위를 일시적으로 늘려서 재시도
                self.extend_communication_range()
                continue
                
            unconnected_nodes -= nodes_connected_this_round
            connected_nodes |= nodes_connected_this_round

        # 연결되지 않은 노드 확인
        if unconnected_nodes:
            print(f"Warning: {len(unconnected_nodes)} nodes remain unconnected")


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

            
    def extend_communication_range(self):
        """통신 범위 확장을 통한 이웃 노드 재탐색"""
        extended_range = self.nodes[next(iter(self.nodes))].comm_range * 1.2
        
        for node in self.nodes.values():
            node.comm_range = extended_range
        
        self.find_neighbors()  # 이웃 노드 재탐색

    def get_path_to_bs(self, node_id):
        """특정 노드에서 BS까지의 경로 반환"""
        path = []
        current_node_id = node_id
        
        while current_node_id is not None:
            path.append(current_node_id)
            if current_node_id in self.nodes:
                current_node_id = self.nodes[current_node_id].next_hop
            else:
                break
                
        return path
    

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
        