import matplotlib.pyplot as plt
import numpy as np

from Field import Field

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
    
    # 일반 노드 그리기
    node_x = [node.pos_x for node in wsn_field.nodes.values()]
    node_y = [node.pos_y for node in wsn_field.nodes.values()]
    plt.scatter(node_x, node_y, c='blue', marker='o', s=50, label='Sensor Nodes')
    
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
    np.random.seed(42)  # 42는 임의의 고정된 시드값입니다. 원하는 값으로 변경 가능

    # Field 생성 (2km x 2km)
    wsn_field = Field(2000, 2000)
    
    # 노드 1000개 배치
    wsn_field.deploy_nodes(1000)
    
    # 베이스 스테이션 설정 (중앙에 위치)
    wsn_field.set_base_station(1000, 1000)
    
    # 각 노드의 이웃 노드 탐색
    wsn_field.find_neighbors()
    
    # 최단 경로 라우팅 설정
    wsn_field.setup_shortest_path_routing()
    
    # 라우팅 경로 확인을 위한 출력
    # print("\nRouting Information:")
    # for node_id, node in list(wsn_field.nodes.items())[:5]:  # 처음 5개 노드만 출력
    #     print(f"Node {node_id} -> Next Hop: {node.next_hop}")

    # 연결되지 않은 노드 확인
    unconnected_nodes = wsn_field.find_unconnected_nodes()
    if unconnected_nodes:
        print("\nUnconnected Nodes Information:")
        print(f"Total unconnected nodes: {len(unconnected_nodes)}")
        print("\nDetails of unconnected nodes:")
        for node in unconnected_nodes:
            print(f"Node {node['node_id']}:")
            print(f"  Position: ({node['position'][0]:.2f}, {node['position'][1]:.2f})")
            print(f"  Number of neighbors: {node['neighbor_count']}")
    else:
        print("\nAll nodes are connected!")
    
    # 네트워크 시각화
    visualize_network(wsn_field)

if __name__ == "__main__":
    main()