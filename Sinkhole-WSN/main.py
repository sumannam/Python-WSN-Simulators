import os
import csv
import time
import matplotlib.pyplot as plt
import numpy as np

from Field import Field
from ShortestPathRouting import ShortestPathRouting
from SinkholeAttack import SinkholeAttack

# Simulation Parameters
RANDOM_SEED = 42          # 랜덤 시드
FIELD_SIZE = 2000         # 필드 크기 (m)
NUM_NODES = 1000          # 센서 노드 수
BS_POSITION = (1000, 1000)  # 베이스 스테이션 위치 (x, y)

# Attack Parameters
ATTACK_TYPE = "outside"   # 공격 타입 ("outside" or "inside")
NUM_ATTACKERS = 1         # 공격자 수
ATTACK_TIMING = "50"      # 공격 시점 (보고서 발생 기준 "0", "30", "50", "70", "90")

# Report Parameters
NUM_REPORTS = 10         # 생성할 보고서 수

# Save Parameters
SAVE_FILE_NAME = 'final_nodes_state.csv'  # 결과 저장 파일명

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

def visualize_network(wsn_field):
    """WSN 노드 배치 시각화"""
    plt.figure(figsize=(12, 12))
    
    # 필드 경계 설정
    plt.xlim(0, wsn_field.width)
    plt.ylim(0, wsn_field.height)
    
    # 먼저 악성 노드 ID 목록 생성
    malicious_ids = {node_id for node_id, node in wsn_field.nodes.items() 
                    if node.node_type in ["malicious_inside", "malicious_outside"]}
    
    # 라우팅 경로 그리기
    for node_id, node in wsn_field.nodes.items():
        if node.next_hop:
            # 현재 노드나 다음 노드가 악성이거나, 다음 홉이 악성 노드인 경우 빨간색으로 표시
            is_affected = (node_id in malicious_ids or 
                         (node.next_hop in malicious_ids) or 
                         (node.next_hop == "BS" and node_id in malicious_ids))
            
            if node.next_hop == "BS":
                plt.plot([node.pos_x, wsn_field.base_station['x']],
                        [node.pos_y, wsn_field.base_station['y']],
                        'r-' if is_affected else 'gray', 
                        alpha=0.8 if is_affected else 0.3,
                        linewidth=2 if is_affected else 1)
            elif node.next_hop in wsn_field.nodes:
                next_node = wsn_field.nodes[node.next_hop]
                plt.plot([node.pos_x, next_node.pos_x],
                        [node.pos_y, next_node.pos_y],
                        'r-' if is_affected else 'gray',
                        alpha=0.8 if is_affected else 0.3,
                        linewidth=2 if is_affected else 1)
    
    # 노드 분류 및 그리기
    normal_nodes_x = []
    normal_nodes_y = []
    normal_colors = []
    dead_nodes_x = []
    dead_nodes_y = []
    inside_attack_x = []
    inside_attack_y = []
    outside_attack_x = []
    outside_attack_y = []
    
    for node in wsn_field.nodes.values():
        if node.status == "inactive":
            dead_nodes_x.append(node.pos_x)
            dead_nodes_y.append(node.pos_y)
        elif node.node_type == "malicious_inside":
            inside_attack_x.append(node.pos_x)
            inside_attack_y.append(node.pos_y)
        elif node.node_type == "malicious_outside":
            outside_attack_x.append(node.pos_x)
            outside_attack_y.append(node.pos_y)
        else:
            normal_nodes_x.append(node.pos_x)
            normal_nodes_y.append(node.pos_y)
            energy_ratio = node.energy_level / node.initial_energy
            color_intensity = max(0.2, energy_ratio)
            normal_colors.append((0, 0, color_intensity))
    
    # 노드 그리기
    if normal_nodes_x:
        plt.scatter(normal_nodes_x, normal_nodes_y, 
                   c=normal_colors, marker='o', s=50, label='Normal Nodes')
    if dead_nodes_x:
        plt.scatter(dead_nodes_x, dead_nodes_y, 
                   c='black', marker='o', s=50, label='Dead Nodes')
    if inside_attack_x:
        plt.scatter(inside_attack_x, inside_attack_y, 
                   c='pink', marker='o', s=100, label='Inside Attackers')
    if outside_attack_x:
        plt.scatter(outside_attack_x, outside_attack_y, 
                   c='red', marker='o', s=100, label='Outside Attackers')
    
    # BS 그리기
    plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
               c='red', marker='^', s=200, label='Base Station')
    
    plt.title('WSN Node Deployment with Sinkhole Attacks')
    plt.xlabel('Field Width (m)')
    plt.ylabel('Field Height (m)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def simulate_with_attack(wsn_field, routing, attack_timing, num_reports):
    """공격 시점을 고려한 시뮬레이션 실행"""
    results = []
    
    # 공격 시점 계산 (보고서 발생 진행률 기준)
    attack_point = int(num_reports * int(attack_timing) / 100)
    
    # 공격 객체 준비
    attack = SinkholeAttack(wsn_field, attack_type=ATTACK_TYPE)

    print(f"\nSimulating {NUM_REPORTS} Report Transmissions:")
    print("-" * 50)
    print(f"Attack timing: {attack_timing}% (at report {attack_point})")
    
    start_time = time.time()

    # 보고서 전송 시뮬레이션
    for i in range(num_reports):
        # 공격 시점에 도달하면 공격 실행
        if i == attack_point:
            malicious_nodes = attack.execute_attack(num_attackers=NUM_ATTACKERS)
            print(f"\nSinkhole Attack Executed at {attack_timing}% of reports:")
            print(f"Number of malicious nodes: {len(malicious_nodes)}")
            print(f"Malicious node IDs: {malicious_nodes}")
            
            # 라우팅 재설정
            routing.setup_routing()

        # 보고서 전송
        result = routing.simulate_reports(1)[0]
        results.append(result)

        # 진행상황 출력 (10% 단위)
        if i % (num_reports // 10) == 0:
            progress = (i / num_reports) * 100
            print(f"Simulation Progress: {progress:.1f}%")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nSimulation Time Information:")
    print(f"Total time elapsed: {elapsed_time:.4f} seconds")
    print(f"Average time per report: {elapsed_time/num_reports:.4f} seconds")

    return results

def main():
    # 재현성을 위한 랜덤 시드 설정
    np.random.seed(RANDOM_SEED)

    # 1. Field 설정
    wsn_field = Field(FIELD_SIZE, FIELD_SIZE)
    wsn_field.deploy_nodes(NUM_NODES)
    wsn_field.set_base_station(BS_POSITION[0], BS_POSITION[1])
    wsn_field.find_neighbors()

    # 2. 라우팅 설정
    routing = ShortestPathRouting(wsn_field)
    routing.setup_routing()

    # 3. 시뮬레이션 실행 (공격 시점 고려)
    transmission_results = simulate_with_attack(wsn_field, routing, 
                                              ATTACK_TIMING, NUM_REPORTS)

    # 4. 결과 저장 및 시각화
    save_nodes_state(wsn_field, SAVE_FILE_NAME)
    print(f"\nAll nodes state has been saved to '{SAVE_FILE_NAME}'")
    visualize_network(wsn_field)

if __name__ == "__main__":
    main()