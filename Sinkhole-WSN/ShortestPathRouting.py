import os
import csv
import numpy as np

import threading
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class ShortestPathRouting:
    def __init__(self, field):
        self.field = field
        self.lock = Lock()  # 스레드 동기화를 위한 락

    def setup_routing(self):
        """BS까지의 최단 경로 설정"""
        if not self.field.base_station:
            print("Base station not set. Cannot setup routing.")
            return

        # 모든 노드의 hop_count 초기화
        for node in self.field.nodes.values():
            node.hop_count = float('inf')
            node.next_hop = None

        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']

        # 모든 노드의 초기 상태를 미연결로 설정
        unconnected_nodes = set(self.field.nodes.keys())
        connected_nodes = set()

        # BS와 직접 연결 가능한 노드들 먼저 처리
        for node_id in list(unconnected_nodes):
            node = self.field.nodes[node_id]
            dist_to_bs = ((node.pos_x - bs_x)**2 + (node.pos_y - bs_y)**2)**0.5
            
            if dist_to_bs <= node.comm_range:
                node.next_hop = "BS"
                node.hop_count = 1  # BS와 직접 연결된 노드는 hop_count가 1
                unconnected_nodes.remove(node_id)
                connected_nodes.add(node_id)
                print(f"Node {node_id} directly connected to BS, hop_count: {node.hop_count}")

        # 나머지 노드들 처리
        changes_made = True
        while unconnected_nodes and changes_made:
            changes_made = False
            nodes_connected_this_round = set()
            
            for node_id in unconnected_nodes:
                node = self.field.nodes[node_id]
                best_next_hop = None
                min_hop_count = float('inf')

                # 연결된 이웃 노드들 중에서 최적의 next hop 찾기
                for neighbor_id in node.neighbor_nodes:
                    if neighbor_id in connected_nodes:
                        neighbor = self.field.nodes[neighbor_id]
                        if neighbor.hop_count < min_hop_count:
                            min_hop_count = neighbor.hop_count
                            best_next_hop = neighbor_id

                # next hop을 찾았다면 노드 연결
                if best_next_hop is not None:
                    node.next_hop = best_next_hop
                    node.hop_count = min_hop_count + 1
                    nodes_connected_this_round.add(node_id)
                    changes_made = True
                    print(f"Node {node_id} connected via {best_next_hop}, hop_count: {node.hop_count}")

            if not changes_made:
                # 더 이상 연결할 수 있는 노드가 없으면 통신 범위 확장
                old_range = self.field.nodes[next(iter(self.field.nodes))].comm_range
                self._extend_communication_range()
                new_range = self.field.nodes[next(iter(self.field.nodes))].comm_range
                print(f"Extended communication range from {old_range}m to {new_range}m")
                changes_made = True
                continue
                
            unconnected_nodes -= nodes_connected_this_round
            connected_nodes |= nodes_connected_this_round

        # 연결되지 않은 노드 확인
        if unconnected_nodes:
            print(f"Warning: {len(unconnected_nodes)} nodes remain unconnected")
        else:
            print("All nodes connected successfully")

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
    

    def process_single_report(self, report_id):
        """단일 보고서 처리 (스레드에서 실행)"""
        packet_size = 32
        
        # 소스 노드 선택
        with self.lock:  # 노드 선택 시 락 사용
            available_nodes = list(self.field.nodes.keys())
            source_node_id = np.random.choice(available_nodes)
        
        # 경로 추적
        path = self.get_path_to_bs(source_node_id)
        
        # 경로를 따라 패킷 전송 시뮬레이션
        for j in range(len(path)-1):
            current_id = int(path[j])
            with self.lock:  # 노드 상태 변경 시 락 사용
                current_node = self.field.nodes[current_id]
                current_node.transmit_packet(packet_size)
                
                if path[j+1] != "BS":
                    next_id = int(path[j+1])
                    next_node = self.field.nodes[next_id]
                    next_node.receive_packet(packet_size)
        
        return {
            'report_id': report_id + 1,
            'source_node': source_node_id,
            'path': path,
            'source_energy': self.field.nodes[source_node_id].energy_level
        }

    def simulate_reports(self, num_reports):
        """멀티스레드로 여러 보고서 전송 시뮬레이션"""
        reports = []
        max_workers = min(num_reports, os.cpu_count() * 2)  # 스레드 수 설정
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 각 보고서를 별도의 스레드에서 처리
            future_reports = [executor.submit(self.process_single_report, i) 
                            for i in range(num_reports)]
            
            # 결과 수집
            for future in future_reports:
                reports.append(future.result())
        
        # 보고서 ID 순서대로 정렬
        reports.sort(key=lambda x: x['report_id'])
        return reports