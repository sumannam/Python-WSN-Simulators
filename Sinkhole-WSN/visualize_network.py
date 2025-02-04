# def visualize_network(wsn_field):
#     """WSN 노드 배치 시각화"""
#     plt.figure(figsize=(12, 12))
    
#     # 필드 경계 설정
#     plt.xlim(0, wsn_field.width)
#     plt.ylim(0, wsn_field.height)
    
#     # next_hop 연결선 그리기 (라우팅 경로)
#     for node_id, node in wsn_field.nodes.items():
#         if node.next_hop:
#             if node.next_hop == "BS":
#                 # BS로의 직접 연결 (빨간색 선)
#                 plt.plot([node.pos_x, wsn_field.base_station['x']],
#                         [node.pos_y, wsn_field.base_station['y']],
#                         'r-', alpha=0.8, linewidth=1.5)
#             elif node.next_hop in wsn_field.nodes:
#                 # 다른 노드로의 연결 (녹색 선)
#                 next_node = wsn_field.nodes[node.next_hop]
#                 plt.plot([node.pos_x, next_node.pos_x],
#                         [node.pos_y, next_node.pos_y],
#                         'g-', alpha=0.8, linewidth=1)
#         else:
#             print(f"Warning: Node {node_id} has no next_hop")
    
#     # 일반 노드 그리기
#     node_x = [node.pos_x for node in wsn_field.nodes.values()]
#     node_y = [node.pos_y for node in wsn_field.nodes.values()]
#     plt.scatter(node_x, node_y, c='blue', marker='o', s=50, label='Sensor Nodes')
    
#     # 베이스 스테이션 그리기
#     if wsn_field.base_station:
#         plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'], 
#                    c='red', marker='^', s=200, label='Base Station')
    
#     plt.title('WSN Node Deployment with Routing Paths')
#     plt.xlabel('Field Width (m)')
#     plt.ylabel('Field Height (m)')
#     plt.legend()
#     plt.grid(True)
#     plt.axis('equal')
#     plt.show()