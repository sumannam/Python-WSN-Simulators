import os
import csv
import numpy as np

class BaseRoutingProtocol:
    def __init__(self, field):
        self.field = field

    def setup_routing(self):
        """라우팅 설정 - 자식 클래스에서 구현해야 함"""
        raise NotImplementedError("이 메서드는 자식 클래스에서 구현되어야 합니다")

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

    def process_single_report(self, report_id, source_node=None):
        """단일 보고서 처리"""
        packet_size = 32
        
        # 소스 노드 선택 (지정된 소스 노드가 없으면 랜덤 선택)
        if source_node is None:
            available_nodes = list(self.field.nodes.keys())
            source_node_id = np.random.choice(available_nodes)
        else:
            source_node_id = source_node
        
        # 경로 추적
        path = self.get_path_to_bs(source_node_id)
        
        # 경로를 따라 패킷 전송 시뮬레이션
        for j in range(len(path)-1):
            current_id = int(path[j])
            current_node = self.field.nodes[current_id]
            
            # 현재 노드의 패킷 전송
            current_node.transmit_packet(packet_size)
            
            # 다음 노드의 패킷 수신
            next_id = path[j+1]
            if next_id == "BS":
                # BS에 도달한 경우
                continue
            else:
                next_id = int(next_id)
                next_node = self.field.nodes[next_id]
                next_node.receive_packet(packet_size)
        
        return {
            'report_id': report_id + 1,
            'source_node': source_node_id,
            'path': path,
            'source_energy': self.field.nodes[source_node_id].energy_level
        }

    def simulate_reports(self, num_reports, source_node=None):
        """순차적으로 여러 보고서 전송 시뮬레이션"""
        reports = []
        
        # 각 보고서를 순차적으로 처리
        for i in range(num_reports):
            report = self.process_single_report(i, source_node)
            reports.append(report)
        
        return reports

    def _extend_communication_range(self):
        """통신 범위 확장"""
        extended_range = self.field.nodes[next(iter(self.field.nodes))].comm_range * 1.2
        for node in self.field.nodes.values():
            node.comm_range = extended_range
        self.field.find_neighbors()