import os
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
import logging  # 로깅 모듈 추가

from core.Field import Field

from core.routing.BaseRoutingProtocol import BaseRoutingProtocol
from core.routing.DijkstraRouting import DijkstraRouting

from attacks.Sinkhole import Sinkhole
from config import *


# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    
    # 로거 설정
    logger = logging.getLogger('wsn_simulation')
    logger.setLevel(log_level)
    
    # 이미 핸들러가 있으면 제거
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 파일 핸들러 (results 폴더에 저장)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_folder = os.path.join(script_dir, 'results')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    file_handler = logging.FileHandler(os.path.join(log_folder, 'simulation.log'))
    file_handler.setLevel(log_level)
    
    # 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def save_nodes_state(wsn_field, filename='nodes_state.csv'):
    """전체 네트워크의 노드 상태를 CSV로 저장"""
    # 현재 스크립트 파일의 디렉토리 경로 가져오기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # results 폴더 경로 생성
    folder_path = os.path.join(script_dir, 'results')
    
    # 폴더가 없으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, filename)

    first_node = next(iter(wsn_field.nodes.values()))
    fieldnames = list(first_node.get_node_state_dict().keys())
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for node in wsn_field.nodes.values():
                writer.writerow(node.get_node_state_dict())
        
        logger.info(f"파일이 성공적으로 저장되었습니다: {file_path}")
    except Exception as e:
        logger.error(f"파일 저장 중 오류 발생: {e}")
        logger.error(f"시도한 경로: {file_path}")

def classify_wsn_nodes(wsn_field):
    """WSN 노드들을 타입별로 분류"""
    # 노드 분류를 위한 리스트 초기화
    normal_nodes_x = []
    normal_nodes_y = []
    normal_colors = []
    dead_nodes_x = []
    dead_nodes_y = []
    inside_attack_x = []
    inside_attack_y = []
    outside_attack_x = []
    outside_attack_y = []
    affected_nodes_x = []
    affected_nodes_y = []
    
    # 노드 데이터 분류
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
        elif node.node_type == "affected":
            affected_nodes_x.append(node.pos_x)
            affected_nodes_y.append(node.pos_y)
        else:
            normal_nodes_x.append(node.pos_x)
            normal_nodes_y.append(node.pos_y)
            energy_ratio = node.energy_level / node.initial_energy
            color_intensity = max(0.2, energy_ratio)
            normal_colors.append((0, 0, color_intensity))
    
    return {
        'normal': (normal_nodes_x, normal_nodes_y, normal_colors),
        'dead': (dead_nodes_x, dead_nodes_y),
        'inside_attack': (inside_attack_x, inside_attack_y),
        'outside_attack': (outside_attack_x, outside_attack_y),
        'affected': (affected_nodes_x, affected_nodes_y)
    }

def plot_wsn_network(wsn_field, classified_nodes):
    """WSN 노드 배치 시각화"""
    plt.figure(figsize=(12, 12))
    
    # 필드 경계 설정
    plt.xlim(0, wsn_field.width)
    plt.ylim(0, wsn_field.height)
    
    # 공격 범위 원 그리기
    for node in wsn_field.nodes.values():
        if node.node_type in ["malicious_outside", "malicious_inside"]:
            attack_range = plt.Circle((node.pos_x, node.pos_y), 
                                    ATTACK_RANGE, 
                                    color='red', 
                                    fill=False, 
                                    linestyle='--', 
                                    alpha=0.5)
            plt.gca().add_patch(attack_range)
    
    # 라우팅 경로 그리기
    for node_id, node in wsn_field.nodes.items():
        if node.next_hop:
            # 공격자 노드는 BS와 연결선을 그리지 않음
            if node.node_type in ["malicious_inside", "malicious_outside"] and node.next_hop == "BS":
                continue

            # 현재 노드가 영향을 받은 노드인지 확인
            is_affected = (node.node_type in ["malicious_inside", "malicious_outside", "affected"])
            
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
    
    # 노드 그리기
    normal_x, normal_y, normal_colors = classified_nodes['normal']
    if normal_x:
        plt.scatter(normal_x, normal_y, 
                   c=normal_colors, marker='o', s=50, label='Normal Nodes')
    
    dead_x, dead_y = classified_nodes['dead']
    if dead_x:
        plt.scatter(dead_x, dead_y, 
                   c='black', marker='o', s=50, label='Dead Nodes')
    
    inside_x, inside_y = classified_nodes['inside_attack']
    if inside_x:
        plt.scatter(inside_x, inside_y, 
                   c='pink', marker='o', s=100, label='Inside Attackers')
    
    outside_x, outside_y = classified_nodes['outside_attack']
    if outside_x:
        plt.scatter(outside_x, outside_y, 
                   c='red', marker='o', s=100, label='Outside Attackers')
    
    affected_x, affected_y = classified_nodes['affected']
    if affected_x:
        plt.scatter(affected_x, affected_y, 
                   c='orange', marker='o', s=50, label='Affected Nodes')
    
    # BS 그리기
    plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
               c='red', marker='^', s=200, label='Base Station')
    
    plt.title('WSN Node Deployment with Sinkhole Attacks')
    plt.xlabel('Field Width (m)')
    plt.ylabel('Field Height (m)')
    
    # 범례를 오른쪽 하단에 위치시키고 속성 조정
    plt.legend(loc='lower right', framealpha=0.9, frameon=True, 
              fontsize='medium', markerscale=0.8, 
              bbox_to_anchor=(0.99, 0.01))
    
    plt.grid(True)
    plt.axis('equal')
    
    # 그래프 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_folder = os.path.join(script_dir, 'results')
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)
    plt.savefig(os.path.join(plot_folder, 'network_deployment.png'), 
               bbox_inches='tight', dpi=300)
    
    plt.show()

def simulate_with_attack(wsn_field, routing, attack_timing, num_reports):
    """공격 시점을 고려한 시뮬레이션 실행"""
    results = []
    
    # 공격 객체 준비
    attack = Sinkhole(wsn_field, attack_type=ATTACK_TYPE, attack_range=ATTACK_RANGE)
    malicious_nodes = None  # 공격자 노드 추적

    logger.info(f"\nSimulating {NUM_REPORTS} Report Transmissions:")
    logger.info("-" * 50)
    logger.info(f"Attack probability: {ATTACK_PROBABILITY}% per report")
    
    start_time = time.time()

    def find_nodes_in_affected_paths(wsn_field):
        """affected 노드의 경로상에 있는 노드들을 찾는 함수"""
        path_nodes = set()
        affected_nodes = set()
        
        # affected 노드와 경로상의 노드들 찾기
        for node_id, node in wsn_field.nodes.items():
            if node.node_type == "affected":
                affected_nodes.add(node_id)
                current = node
                while current.next_hop and current.next_hop != "BS":
                    path_nodes.add(current.next_hop)
                    current = wsn_field.nodes[current.next_hop]
                    
        return list(path_nodes), list(affected_nodes)

    def get_farthest_node(wsn_field, candidate_nodes):
        """BS로부터 가장 먼 노드를 선택하는 함수"""
        max_distance = -1
        farthest_node = None
        bs_x, bs_y = wsn_field.base_station['x'], wsn_field.base_station['y']
        
        for node_id in candidate_nodes:
            node = wsn_field.nodes[node_id]
            distance = ((node.pos_x - bs_x) ** 2 + (node.pos_y - bs_y) ** 2) ** 0.5
            if distance > max_distance:
                max_distance = distance
                farthest_node = node_id
                
        return farthest_node

    # 초기 공격 실행
    malicious_nodes = attack.execute_attack(num_attackers=NUM_ATTACKERS)
    logger.info(f"\nInitial Sinkhole Attack Executed:")
    logger.info(f"Number of malicious nodes: {len(malicious_nodes)}")
    logger.info(f"Malicious node IDs: {malicious_nodes}")

    # 보고서 전송 시뮬레이션
    for i in range(num_reports):
        # 확률적으로 공격 실행 (0~100 사이의 정수로 비교)
        if np.random.randint(1, 101) <= ATTACK_PROBABILITY:
            # affected 노드의 경로상에 있는 노드들과 affected 노드들 찾기
            path_nodes, affected_nodes = find_nodes_in_affected_paths(wsn_field)
            
            if path_nodes:  # 경로상의 노드가 있는 경우
                # BS에서 가장 먼 노드 선택
                source_node = get_farthest_node(wsn_field, path_nodes)
                
                if source_node:
                    # 보고서 전송 시뮬레이션 (affected 노드를 통과하도록)
                    result = routing.simulate_reports(1, source_node=source_node)[0]
                    results.append(result)
                    
                    # 경로에 affected 노드가 포함되어 있는지 확인
                    path = result['path']
                    affected_in_path = any(node_id in affected_nodes for node_id in path)
                    
                    if affected_in_path:
                        logger.info(f"\nReport #{i+1}: Sinkhole attack occurred")
                        logger.info(f"Source Node: {source_node}")
                        logger.info(f"Path: {' -> '.join(map(str, path))}")
                else:
                    # 적절한 소스 노드를 찾지 못한 경우 일반 시뮬레이션
                    result = routing.simulate_reports(1)[0]
                    results.append(result)
            else:
                # 경로상의 노드가 없는 경우 일반 시뮬레이션
                result = routing.simulate_reports(1)[0]
                results.append(result)
        else:
            # 공격이 발생하지 않는 경우 일반 시뮬레이션
            result = routing.simulate_reports(1)[0]
            results.append(result)
        
        # 디버깅 모드일 경우 각 보고서 정보 출력
        if DEBUG_MODE:
            logger.debug(f"Report #{i+1}: Source Node {result['source_node']}, Path: {' -> '.join(map(str, result['path']))}")

        # 진행상황 출력 (10% 단위)
        if i % (num_reports // 10) == 0:
            progress = (i / num_reports) * 100
            logger.info(f"Simulation Progress: {progress:.1f}%")

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"\nSimulation Time Information:")
    logger.info(f"Total time elapsed: {elapsed_time:.4f} seconds")
    logger.info(f"Average time per report: {elapsed_time/num_reports:.4f} seconds")

    # 추가: 에너지 소비 및 패킷 전송/수신 통계
    analyze_network_statistics(wsn_field)

    return results

def analyze_network_statistics(wsn_field):
    """네트워크 통계 분석 및 출력"""
    total_energy = 0
    total_tx = 0
    total_rx = 0
    active_nodes = 0
    
    # 에너지와 패킷 전송/수신 통계
    nodes_with_energy = []
    nodes_with_tx = []
    nodes_with_rx = []
    
    for node_id, node in wsn_field.nodes.items():
        if node.status == "active":
            active_nodes += 1
            
        # 에너지 소비 확인
        node_energy = getattr(node, 'total_consumed_energy', 0)
        total_energy += node_energy
        
        # 디버깅을 위한 속성 출력
        if DEBUG_MODE and node_id < 5:  # 처음 5개 노드만 출력
            logger.debug(f"노드 {node_id}의 속성: {dir(node)}")
        
        # tx_count와 rx_count 직접 확인 (안전하게 접근)
        tx_count = 0
        rx_count = 0
        
        # hasattr로 속성 존재 여부 확인 후 접근
        if hasattr(node, 'tx_count'):
            tx_count = node.tx_count
        elif hasattr(node, 'transmit_count'):  # 다른 가능한 이름
            tx_count = node.transmit_count
            
        if hasattr(node, 'rx_count'):
            rx_count = node.rx_count
        elif hasattr(node, 'receive_count'):  # 다른 가능한 이름
            rx_count = node.receive_count
        
        # 총계에 더하기
        total_tx += tx_count
        total_rx += rx_count
        
        # 통계를 위한 노드 추적
        if node_energy > 0:
            nodes_with_energy.append(node_id)
        if tx_count > 0:
            nodes_with_tx.append(node_id)
        if rx_count > 0:
            nodes_with_rx.append(node_id)
    
    # 통계 출력
    logger.info("\n===== Network Statistics =====")
    logger.info(f"Active Nodes: {active_nodes}/{len(wsn_field.nodes)}")
    logger.info(f"Total Energy Consumed: {total_energy:.6f} Joules")
    logger.info(f"Total TX Count: {total_tx}")
    logger.info(f"Total RX Count: {total_rx}")
    logger.info(f"Nodes with Energy Consumption: {len(nodes_with_energy)}/{len(wsn_field.nodes)} ({len(nodes_with_energy)/len(wsn_field.nodes)*100:.1f}%)")
    logger.info(f"Nodes with TX: {len(nodes_with_tx)}/{len(wsn_field.nodes)} ({len(nodes_with_tx)/len(wsn_field.nodes)*100:.1f}%)")
    logger.info(f"Nodes with RX: {len(nodes_with_rx)}/{len(wsn_field.nodes)} ({len(nodes_with_rx)/len(wsn_field.nodes)*100:.1f}%)")
    
    # 디버깅 모드일 경우 패킷 전송/수신 정보가 있는 노드 목록 출력
    if DEBUG_MODE:
        logger.debug("\n----- 패킷 전송 정보가 있는 노드 -----")
        tx_nodes_found = 0
        for node_id in nodes_with_tx[:10]:  # 처음 10개만 출력
            node = wsn_field.nodes[node_id]
            tx_count = getattr(node, 'tx_count', 0)
            logger.debug(f"Node {node_id}: TX={tx_count}")
            tx_nodes_found += 1
            
        if tx_nodes_found == 0:
            logger.debug("패킷 전송 정보가 있는 노드가 없습니다.")
            
        logger.debug("\n----- 패킷 수신 정보가 있는 노드 -----")
        rx_nodes_found = 0
        for node_id in nodes_with_rx[:10]:  # 처음 10개만 출력
            node = wsn_field.nodes[node_id]
            rx_count = getattr(node, 'rx_count', 0)
            logger.debug(f"Node {node_id}: RX={rx_count}")
            rx_nodes_found += 1
            
        if rx_nodes_found == 0:
            logger.debug("패킷 수신 정보가 있는 노드가 없습니다.")
        
        logger.debug("\n----- 에너지 소비가 있는 노드 -----")
        for node_id in nodes_with_energy[:10]:  # 처음 10개만 출력
            node = wsn_field.nodes[node_id]
            energy = getattr(node, 'total_consumed_energy', 0)
            tx = getattr(node, 'tx_count', 0)
            rx = getattr(node, 'rx_count', 0)
            logger.debug(f"Node {node_id}: Energy={energy:.8f}J, TX={tx}, RX={rx}")
        
        if len(nodes_with_energy) > 10:
            logger.debug(f"... and {len(nodes_with_energy) - 10} more nodes")

def get_routing_protocol(protocol_name, wsn_field):
    """선택한 라우팅 프로토콜을 반환"""
    protocol_name = protocol_name.lower()
    
    if protocol_name == "dijkstra":
        return DijkstraRouting(wsn_field)
    # 나중에 다른 프로토콜을 추가할 수 있음
    # elif protocol_name == "aodv":
    #     return AODVRouting(wsn_field)
    # elif protocol_name == "leach":
    #     return LEACHRouting(wsn_field)
    else:
        logger.warning(f"Unknown routing protocol '{protocol_name}'. Using Dijkstra as default.")
        return DijkstraRouting(wsn_field)

def main():
    # 로깅 설정
    global logger
    logger = setup_logging()
    
    logger.info("==== WSN Simulation Start ====")
    
    # 재현성을 위한 랜덤 시드 설정
    np.random.seed(RANDOM_SEED)
    logger.debug(f"Random seed set to {RANDOM_SEED}")

    # 1. Field 설정
    wsn_field = Field(FIELD_SIZE, FIELD_SIZE)
    wsn_field.deploy_nodes(NUM_NODES)
    wsn_field.set_base_station(BS_POSITION[0], BS_POSITION[1])
    wsn_field.find_neighbors()
    logger.info(f"Field created with {NUM_NODES} nodes, size {FIELD_SIZE}x{FIELD_SIZE}m")
    logger.info(f"Base station set at position {BS_POSITION}")

    # 2. 라우팅 프로토콜 선택 및 설정
    routing = get_routing_protocol(ROUTING_PROTOCOL, wsn_field)
    routing.setup_routing()
    logger.info(f"Routing setup completed using {ROUTING_PROTOCOL} protocol")

    # 3. 시뮬레이션 실행 (공격 시점 고려)
    transmission_results = simulate_with_attack(wsn_field, routing, 
                                              ATTACK_TIMING, NUM_REPORTS)

    # 4. 결과 저장 및 시각화
    save_nodes_state(wsn_field, SAVE_FILE_NAME)
    logger.info(f"All nodes state has been saved to '{SAVE_FILE_NAME}'")
    
    # 5. 노드 분류 및 시각화
    classified_nodes = classify_wsn_nodes(wsn_field)
    plot_wsn_network(wsn_field, classified_nodes)
    
    logger.info("==== WSN Simulation End ====")

if __name__ == "__main__":
    main()