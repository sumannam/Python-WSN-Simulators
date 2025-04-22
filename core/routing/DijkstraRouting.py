from .BaseRoutingProtocol import BaseRoutingProtocol
import numpy as np


class DijkstraRouting(BaseRoutingProtocol):
    def __init__(self, field):
        super().__init__(field)

    def setup_routing(self):
        """BS까지의 최단 경로 설정 - Dijkstra 알고리즘 기반"""
        if not self.field.base_station:
            print("Base station not set. Cannot setup routing.")
            return

        # 모든 노드의 초기화
        for node in self.field.nodes.values():
            old_next_hop = node.next_hop  # 이전 next_hop 저장
            node.hop_count = float('inf')
            node.next_hop = None
            
            # next_hop이 변경되면 route_changes 증가
            if old_next_hop is not None and old_next_hop != node.next_hop:
                if hasattr(node, 'route_changes'):
                    node.route_changes += 1
                else:
                    node.route_changes = 1

        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']

        # BS와 직접 연결 가능한 일반 노드들 처리
        self._connect_direct_to_bs()
            
        # 나머지 노드들의 라우팅 설정 (Dijkstra 알고리즘 기반)
        self._apply_dijkstra_routing()

    def _connect_direct_to_bs(self):
        """BS와 직접 연결 가능한 노드들 처리"""
        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']
        
        for node_id, node in self.field.nodes.items():
            if node.node_type == "normal":
                dist_to_bs = ((node.pos_x - bs_x)**2 + (node.pos_y - bs_y)**2)**0.5
                if dist_to_bs <= node.comm_range:
                    old_next_hop = node.next_hop
                    node.next_hop = "BS"
                    node.hop_count = 1
                    if old_next_hop != "BS":
                        if hasattr(node, 'route_changes'):
                            node.route_changes += 1
                        else:
                            node.route_changes = 1

    def _apply_dijkstra_routing(self):
        """Dijkstra 알고리즘을 사용한 라우팅 적용"""
        changes_made = True
        while changes_made:
            changes_made = False
            for node_id, node in self.field.nodes.items():
                if node.hop_count == float('inf'):
                    # 이웃 노드들 중 최적의 next hop 찾기
                    best_next_hop = None
                    min_hop_count = float('inf')

                    for neighbor_id in node.neighbor_nodes:
                        neighbor = self.field.nodes[neighbor_id]
                        if neighbor.hop_count < min_hop_count:
                            min_hop_count = neighbor.hop_count
                            best_next_hop = neighbor_id

                    if best_next_hop is not None:
                        old_next_hop = node.next_hop
                        node.next_hop = best_next_hop
                        node.hop_count = min_hop_count + 1
                        if old_next_hop != best_next_hop:
                            if hasattr(node, 'route_changes'):
                                node.route_changes += 1
                            else:
                                node.route_changes = 1
                        changes_made = True

    def _connect_nodes_iteratively(self, unconnected_nodes, connected_nodes):
        """연결되지 않은 노드들을 반복적으로 연결하는 확장 메서드"""
        while unconnected_nodes:
            nodes_connected_this_round = self._connect_nodes_one_round(
                unconnected_nodes, connected_nodes)
            
            if not nodes_connected_this_round:
                self._extend_communication_range()
                continue
                
            unconnected_nodes -= nodes_connected_this_round
            connected_nodes |= nodes_connected_this_round

    def _connect_nodes_one_round(self, unconnected_nodes, connected_nodes):
        """한 라운드의 노드 연결 처리"""
        nodes_connected = set()
        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']

        for node_id in unconnected_nodes:
            node = self.field.nodes[node_id]
            best_next_hop = self._find_best_next_hop(node, connected_nodes)

            if best_next_hop is not None:
                node.next_hop = best_next_hop
                nodes_connected.add(node_id)

        return nodes_connected

    def _find_best_next_hop(self, node, connected_nodes):
        """최적의 next hop 찾기"""
        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']
        best_next_hop = None
        min_dist_to_bs = float('inf')

        for neighbor_id in node.neighbor_nodes:
            if neighbor_id in connected_nodes:
                neighbor = self.field.nodes[neighbor_id]
                dist_to_bs = ((neighbor.pos_x - bs_x)**2 + 
                             (neighbor.pos_y - bs_y)**2)**0.5
                
                if dist_to_bs < min_dist_to_bs:
                    min_dist_to_bs = dist_to_bs
                    best_next_hop = neighbor_id

        return best_next_hop

    def connect_nodes_directly_to_bs(self):
        """BS와 직접 연결 가능한 노드들을 연결"""
        for node_id, node in self.field.nodes.items():
            if node_id not in self.routing_table:
                # BS와의 거리 계산
                distance = np.sqrt((node.pos_x - self.field.base_station['x'])**2 + 
                                 (node.pos_y - self.field.base_station['y'])**2)
                
                # BS가 통신 범위 내에 있고, 에너지가 충분한 경우에만 연결
                if (distance <= self.field.base_station['comm_range'] and 
                    node.energy_level > self.field.base_station['energy_threshold']):
                    self.routing_table[node_id] = "BS"
                    # 에너지 소모 시뮬레이션
                    node.transmit_packet(32)  # 기본 패킷 크기로 에너지 소모 계산

    def apply_dijkstra(self):
        """Dijkstra 알고리즘 적용"""
        # 초기화
        distances = {node_id: float('inf') for node_id in self.field.nodes}
        previous = {node_id: None for node_id in self.field.nodes}
        unvisited = set(self.field.nodes.keys())
        
        # BS와 직접 연결된 노드들의 거리를 1로 설정
        for node_id in self.routing_table:
            if self.routing_table[node_id] == "BS":
                distances[node_id] = 1
                previous[node_id] = "BS"
        
        while unvisited:
            # 가장 짧은 거리를 가진 노드 선택
            current = min(unvisited, key=lambda x: distances[x])
            if distances[current] == float('inf'):
                break
                
            unvisited.remove(current)
            
            # 현재 노드의 이웃 노드들에 대해 거리 업데이트
            for neighbor_id in self.field.nodes:
                if neighbor_id != current and neighbor_id in unvisited:
                    # 이웃 노드와의 거리 계산
                    current_node = self.field.nodes[current]
                    neighbor_node = self.field.nodes[neighbor_id]
                    distance = np.sqrt((current_node.pos_x - neighbor_node.pos_x)**2 + 
                                     (current_node.pos_y - neighbor_node.pos_y)**2)
                    
                    # 통신 범위 내에 있고, 에너지가 충분한 경우에만 연결 고려
                    if (distance <= self.field.base_station['comm_range'] and 
                        neighbor_node.energy_level > self.field.base_station['energy_threshold']):
                        new_distance = distances[current] + 1
                        if new_distance < distances[neighbor_id]:
                            distances[neighbor_id] = new_distance
                            previous[neighbor_id] = current
        
        # 경로 설정
        for node_id in self.field.nodes:
            if node_id not in self.routing_table and previous[node_id] is not None:
                self.routing_table[node_id] = previous[node_id]