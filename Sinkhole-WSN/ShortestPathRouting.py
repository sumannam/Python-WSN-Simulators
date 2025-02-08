import os
import csv
import numpy as np

class ShortestPathRouting:
    def __init__(self, field):
        self.field = field

    def setup_routing(self):
        """BS까지의 최단 경로 설정"""
        if not self.field.base_station:
            print("Base station not set. Cannot setup routing.")
            return

        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']

        # 모든 노드의 초기 상태를 미연결로 설정
        unconnected_nodes = set(self.field.nodes.keys())
        connected_nodes = set()

        self._connect_direct_to_bs(unconnected_nodes, connected_nodes)
        self._connect_remaining_nodes(unconnected_nodes, connected_nodes)

    def _connect_direct_to_bs(self, unconnected_nodes, connected_nodes):
        """BS와 직접 연결 가능한 노드들 처리"""
        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']
        
        for node_id in list(unconnected_nodes):
            node = self.field.nodes[node_id]
            dist_to_bs = ((node.pos_x - bs_x)**2 + (node.pos_y - bs_y)**2)**0.5
            
            if dist_to_bs <= node.comm_range:
                node.next_hop = "BS"
                unconnected_nodes.remove(node_id)
                connected_nodes.add(node_id)

    def _connect_remaining_nodes(self, unconnected_nodes, connected_nodes):
        """나머지 노드들 처리"""
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

    def _extend_communication_range(self):
        """통신 범위 확장"""
        extended_range = self.field.nodes[next(iter(self.field.nodes))].comm_range * 1.2
        for node in self.field.nodes.values():
            node.comm_range = extended_range
        self.field.find_neighbors()

    def get_path_to_bs(self, node_id):
        """특정 노드에서 BS까지의 경로 추적"""
        path = []
        current_id = node_id
        
        while current_id is not None:
            path.append(str(current_id))
            if current_id not in self.field.nodes:
                break
            current_node = self.field.nodes[current_id]
            current_id = current_node.next_hop
            if current_id == "BS":
                path.append("BS")
                break
                
        return path
    

    def simulate_reports(self, num_reports):
        """여러 개의 보고서 전송 시뮬레이션"""
        reports = []
        used_sources = set()  # 이미 사용된 소스 노드 추적
        packet_size = 32  # 기본 패킷 크기 (bytes)

        for i in range(num_reports):
            # 사용되지 않은 노드 중에서 랜덤 선택
            available_nodes = list(set(self.field.nodes.keys()) - used_sources)
            if not available_nodes:  # 모든 노드가 사용됐다면 초기화
                used_sources.clear()
                available_nodes = list(self.field.nodes.keys())
            
            source_node_id = np.random.choice(available_nodes)
            used_sources.add(source_node_id)
            
            # 경로 추적 및 패킷 전송
            path = self.get_path_to_bs(source_node_id)
            
            # 경로를 따라 패킷 전송 시뮬레이션
            for j in range(len(path)-1):
                current_id = int(path[j])  # 문자열을 정수로 변환
                current_node = self.field.nodes[current_id]
                current_node.transmit_packet(packet_size)  # 패킷 전송
                
                if path[j+1] != "BS":
                    next_id = int(path[j+1])  # 문자열을 정수로 변환
                    next_node = self.field.nodes[next_id]
                    next_node.receive_packet(packet_size)  # 패킷 수신
            
            reports.append({
                'report_id': i + 1,
                'source_node': source_node_id,
                'path': path,
                'source_energy': self.field.nodes[source_node_id].energy_level
            })
            
        return reports