# pip install -r requirements.txt

import os
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
import logging  # 로깅 모듈 추가
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation

try:
    import seaborn as sns
    plt.style.use('seaborn')
except ImportError:
    plt.style.use('default')  # matplotlib 기본 스타일 사용

from core.Field import Field

from core.routing.BaseRoutingProtocol import BaseRoutingProtocol
from core.routing.routing_factory import get_routing_protocol

from attacks.Sinkhole import Sinkhole
from utils.visualize_network import plot_wsn_network, classify_wsn_nodes, setup_logging
from utils.animation import animate_report_transmission
from utils.data_handler import save_nodes_state, save_simulation_results
from config import *


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

    def validate_path(path):
        """경로의 유효성을 검증하는 함수"""
        if not path:
            return False
        
        for node_id in path:
            if node_id == "BS":
                continue
            if not isinstance(node_id, (int, str)):
                return False
            if isinstance(node_id, str) and not node_id.isdigit():
                return False
            node_id = int(node_id)
            if node_id not in wsn_field.nodes:
                return False
        return True

    # 초기 공격 실행
    malicious_nodes = attack.execute_attack(num_attackers=NUM_ATTACKERS)
    logger.info(f"\nInitial Sinkhole Attack Executed:")
    logger.info(f"Number of malicious nodes: {len(malicious_nodes)}")
    logger.info(f"Malicious node IDs: {malicious_nodes}")

    # 보고서 전송 시뮬레이션
    for report_id in range(1, num_reports + 1):
        # 공격 확률에 따라 소스 노드 선택
        if np.random.randint(1, 101) <= ATTACK_PROBABILITY:
            # affected 노드나 그 이웃 노드에서 보고서 생성
            affected_nodes, neighbor_nodes = attack.get_affected_and_neighbor_nodes()
            candidate_nodes = list(affected_nodes) + list(neighbor_nodes)
            
            if candidate_nodes:
                source_node = np.random.choice(candidate_nodes)
                # malicious 노드로 향하는 경로 생성
                path = attack.get_malicious_node_path(source_node)
                
                if path:
                    result = {
                        'report_id': report_id,
                        'source_node': source_node,
                        'path': path,
                        'source_energy': wsn_field.nodes[source_node].energy_level
                    }
                    results.append(result)
                    
                    # 경로를 따라 패킷 전송 시뮬레이션
                    for j in range(len(path)-1):
                        current_id = path[j]
                        if current_id == "BS":
                            continue
                        current_node = wsn_field.nodes[current_id]
                        current_node.transmit_packet(32)  # 패킷 전송
                        
                        next_id = path[j+1]
                        if next_id != "BS":
                            next_node = wsn_field.nodes[next_id]
                            next_node.receive_packet(32)  # 패킷 수신
                else:
                    # malicious 노드로 가는 경로를 찾지 못한 경우 일반 전송
                    result = routing.simulate_reports(1)[0]
                    if validate_path(result['path']):
                        result['report_id'] = report_id
                        results.append(result)
            else:
                # affected 노드나 이웃이 없는 경우 일반 전송
                result = routing.simulate_reports(1)[0]
                if validate_path(result['path']):
                    result['report_id'] = report_id
                    results.append(result)
        else:
            # 일반 전송 (랜덤한 노드에서 BS로)
            available_nodes = [node_id for node_id, node in wsn_field.nodes.items() 
                             if node.node_type == "normal"]
            if available_nodes:
                source_node = np.random.choice(available_nodes)
                result = routing.simulate_reports(1, source_node=source_node)[0]
                if validate_path(result['path']):
                    result['report_id'] = report_id
                    results.append(result)

        # 보고서 경로 정보 출력
        if DEBUG_MODE and len(results) > 0:
            latest_result = results[-1]
            path_str = ""
            for i, node_id in enumerate(latest_result['path']):
                if i > 0:
                    path_str += " -> "
                # 노드 ID가 'BS'인 경우
                if node_id == "BS":
                    path_str += "BS"
                    continue
                
                # 노드가 존재하는지 확인
                try:
                    node = wsn_field.nodes[int(node_id)]

                    if node.node_type == "affected":
                        path_str += f"{node_id}(+)"
                    elif node.node_type in ["malicious_inside", "malicious_outside"]:
                        path_str += f"{node_id}(*)"
                    else:
                        path_str += str(node_id)
                    
                except:
                    path_str += f"{node_id}(?)"  # 에러 발생 시 (?)로 표시
                    continue
                    
            logger.debug(f"Report #{latest_result['report_id']}: Source Node {latest_result['source_node']}, Path: {path_str}")

        # 진행상황 출력 (10% 단위)
        if report_id % (num_reports // 10) == 0:
            progress = (report_id / num_reports) * 100
            logger.info(f"Simulation Progress: {progress:.1f}%")

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"\nSimulation Time Information:")
    logger.info(f"Total time elapsed: {elapsed_time:.4f} seconds")
    logger.info(f"Average time per report: {elapsed_time/num_reports:.4f} seconds")
    logger.info(f"Total valid reports generated: {len(results)}")

    # 추가: 에너지 소비 및 패킷 전송/수신 통계
    attack.analyze_network_statistics()

    return results

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
    save_simulation_results(transmission_results, 'simulation_results.csv')
    logger.info(f"All nodes state has been saved to '{SAVE_FILE_NAME}'")
    
    # 5. 노드 분류
    classified_nodes = classify_wsn_nodes(wsn_field)
    
    # 6. 정적 네트워크 시각화
    plot_wsn_network(wsn_field, classified_nodes, ATTACK_RANGE)
    
    # 7. 보고서 전송 애니메이션
    animation_config = {
        'ENABLE_ANIMATION': ENABLE_ANIMATION,
        'ANIMATION_INTERVAL': ANIMATION_INTERVAL,
        'ANIMATION_FPS': ANIMATION_FPS,
        'SAVE_ANIMATION': SAVE_ANIMATION,
        'LIVE_ANIMATION': LIVE_ANIMATION,
        'STEPS_PER_PATH': STEPS_PER_PATH,
        'PACKET_SIZE': PACKET_SIZE,
        'ATTACK_RANGE': ATTACK_RANGE
    }
    animate_report_transmission(wsn_field, transmission_results, classified_nodes, animation_config)
    
    logger.info("==== WSN Simulation End ====")

if __name__ == "__main__":
    main()