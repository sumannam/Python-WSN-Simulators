import os
import csv
import time

import matplotlib.pyplot as plt
import numpy as np

from Field import Field
from ShortestPathRouting import ShortestPathRouting

def save_nodes_state(wsn_field, filename='nodes_state.csv'):
        """전체 네트워크의 노드 상태를 CSV로 저장"""
        folder_path = 'Sinkhole-WSN'
        file_path = os.path.join(folder_path, filename)

        first_node = next(iter(wsn_field.nodes.values()))
        fieldnames = list(first_node.get_node_state_dict().keys())
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for node in wsn_field.nodes.values():
                writer.writerow(node.get_node_state_dict())

# def save_network_state(wsn_field, filename='nodes_state.csv'):
#     """전체 네트워크의 노드 상태를 CSV로 저장"""
#     first_node = next(iter(wsn_field.nodes.values()))
#     fieldnames = list(first_node.get_node_state_dict().keys())
    
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
        
#         for node in wsn_field.nodes.values():
#             writer.writerow(node.get_node_state_dict())

def visualize_network(wsn_field):
    """WSN 노드 배치 시각화"""
    plt.figure(figsize=(12, 12))
    
    # 필드 경계 설정
    plt.xlim(0, wsn_field.width)
    plt.ylim(0, wsn_field.height)
    
    # next_hop 연결선 그리기 (라우팅 경로)
    for node_id, node in wsn_field.nodes.items():
        if node.next_hop:
            if node.next_hop == "BS":
                # BS로의 직접 연결 (빨간색 선)
                plt.plot([node.pos_x, wsn_field.base_station['x']],
                        [node.pos_y, wsn_field.base_station['y']],
                        'r-', alpha=0.8, linewidth=1.5)
            elif node.next_hop in wsn_field.nodes:
                # 다른 노드로의 연결 (녹색 선)
                next_node = wsn_field.nodes[node.next_hop]
                plt.plot([node.pos_x, next_node.pos_x],
                        [node.pos_y, next_node.pos_y],
                        'g-', alpha=0.8, linewidth=1)
        else:
            print(f"Warning: Node {node_id} has no next_hop")
    
    # 노드 위치와 색상 데이터 준비
    node_x = []
    node_y = []
    node_colors = []
    dead_nodes_x = []
    dead_nodes_y = []
    
    for node in wsn_field.nodes.values():
        if node.status == "inactive":  # 죽은 노드
            dead_nodes_x.append(node.pos_x)
            dead_nodes_y.append(node.pos_y)
        else:  # 활성 노드
            node_x.append(node.pos_x)
            node_y.append(node.pos_y)
            # 에너지 레벨에 따른 색상 강도 계산 (100% -> 1.0, 0% -> 0.2)
            energy_ratio = node.energy_level / node.initial_energy
            color_intensity = max(0.2, energy_ratio)  # 최소 0.2의 진하기 유지
            node_colors.append((0, 0, color_intensity))  # 파란색 계열
    
    # 활성 노드 그리기 (에너지 레벨에 따른 색상)
    if node_x:  # 활성 노드가 있는 경우
        plt.scatter(node_x, node_y, c=node_colors, marker='o', s=50, label='Active Nodes')
    
    # 죽은 노드 그리기 (회색)
    if dead_nodes_x:  # 죽은 노드가 있는 경우
        plt.scatter(dead_nodes_x, dead_nodes_y, c='gray', marker='o', s=50, label='Dead Nodes')
    
    # 베이스 스테이션 그리기
    if wsn_field.base_station:
        plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'], 
                   c='red', marker='^', s=200, label='Base Station')
    
    plt.title('WSN Node Deployment with Routing Paths')
    plt.xlabel('Field Width (m)')
    plt.ylabel('Field Height (m)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()


def main():
    # 재현성을 위한 랜덤 시드 설정
    np.random.seed(42)

    # 1. Field 설정
    wsn_field = Field(2000, 2000)
    wsn_field.deploy_nodes(1000)
    wsn_field.set_base_station(1000, 1000)
    wsn_field.find_neighbors()

    # 2. 라우팅 설정
    routing = ShortestPathRouting(wsn_field)
    routing.setup_routing()

    # 3. 연결되지 않은 노드 확인
    unconnected_nodes = wsn_field.find_unconnected_nodes()
    if unconnected_nodes:
        print("\nUnconnected Nodes Information:")
        print(f"Total unconnected nodes: {len(unconnected_nodes)}")
    else:
        print("\nAll nodes are connected!")
    
    # 4. 보고서 전송 시뮬레이션 (시간 측정 추가)
    num_reports = 99999  # 원하는 보고서 수 설정
    
    print(f"\nSimulating {num_reports} Report Transmissions:")
    print("-" * 50)
    
    # 시작 시간 기록
    start_time = time.time()
    
    transmission_results = routing.simulate_reports(num_reports)
    
    # 종료 시간 기록
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 전송 결과 출력
    for report in transmission_results:
        source_node = wsn_field.nodes[report['source_node']]
        # print(f"\nReport {report['report_id']}:")
        # print(f"Source Node ID: {source_node.node_id}")
        # print(f"Position: ({source_node.pos_x:.2f}, {source_node.pos_y:.2f})")
        # print(f"Distance to BS: {source_node.distance_to_bs:.2f}m")
        # print(f"Path to BS: {' -> '.join(report['path'])}")
        # print(f"Number of hops: {len(report['path']) - 1}")

    # 시간 정보 출력
    print(f"\nSimulation Time Information:")
    print(f"Total time elapsed: {elapsed_time:.4f} seconds")
    print(f"Average time per report: {elapsed_time/num_reports:.4f} seconds")

    # 5. 시뮬레이션 후 노드 상태 저장
    save_nodes_state(wsn_field, 'final_nodes_state.csv')
    print("\nAll nodes state has been saved to 'final_nodes_state.csv'")
    
    # 6. 네트워크 시각화
    visualize_network(wsn_field)

if __name__ == "__main__":
    main()