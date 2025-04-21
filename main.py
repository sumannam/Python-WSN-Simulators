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
    
    # 노드 그리기 및 노드 ID 표시
    normal_x, normal_y, normal_colors = classified_nodes['normal']
    if normal_x:
        plt.scatter(normal_x, normal_y, 
                   c=normal_colors, marker='o', s=50, label='Normal Nodes')
        # 일반 노드 ID 표시
        for i, (x, y) in enumerate(zip(normal_x, normal_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    dead_x, dead_y = classified_nodes['dead']
    if dead_x:
        plt.scatter(dead_x, dead_y, 
                   c='black', marker='o', s=50, label='Dead Nodes')
        # 죽은 노드 ID 표시
        for i, (x, y) in enumerate(zip(dead_x, dead_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    inside_x, inside_y = classified_nodes['inside_attack']
    if inside_x:
        plt.scatter(inside_x, inside_y, 
                   c='pink', marker='o', s=100, label='Inside Attackers')
        # 내부 공격자 노드 ID 표시
        for i, (x, y) in enumerate(zip(inside_x, inside_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    outside_x, outside_y = classified_nodes['outside_attack']
    if outside_x:
        plt.scatter(outside_x, outside_y, 
                   c='red', marker='o', s=100, label='Outside Attackers')
        # 외부 공격자 노드 ID 표시
        for i, (x, y) in enumerate(zip(outside_x, outside_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    affected_x, affected_y = classified_nodes['affected']
    if affected_x:
        plt.scatter(affected_x, affected_y, 
                   c='orange', marker='o', s=50, label='Affected Nodes')
        # 영향받은 노드 ID 표시
        for i, (x, y) in enumerate(zip(affected_x, affected_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
    
    # BS 그리기
    plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
               c='red', marker='^', s=200, label='Base Station')
    plt.annotate('BS', (wsn_field.base_station['x'], wsn_field.base_station['y']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=10, weight='bold')
    
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

    def get_affected_and_neighbor_nodes():
        """affected 노드와 그 이웃 노드들의 목록을 반환"""
        affected_nodes = set()
        neighbor_nodes = set()
        
        # affected 노드 찾기
        for node_id, node in wsn_field.nodes.items():
            if node.node_type == "affected":
                affected_nodes.add(node_id)
                # affected 노드의 이웃 노드들 추가
                for neighbor_id in node.neighbor_nodes:
                    if wsn_field.nodes[neighbor_id].node_type == "normal":
                        neighbor_nodes.add(neighbor_id)
        
        return list(affected_nodes), list(neighbor_nodes)

    def get_malicious_node_path(source_node_id):
        """소스 노드에서 가장 가까운 malicious 노드로의 경로 생성"""
        path = [source_node_id]
        current_id = source_node_id
        
        while True:
            current_node = wsn_field.nodes[current_id]
            # 현재 노드의 이웃 중 malicious 노드 찾기
            malicious_neighbors = [n_id for n_id in current_node.neighbor_nodes 
                                if wsn_field.nodes[n_id].node_type in ["malicious_inside", "malicious_outside"]]
            
            if malicious_neighbors:
                # malicious 노드를 찾았으면 경로에 추가하고 종료
                path.append(malicious_neighbors[0])
                break
            
            # malicious 노드 방향으로 이동
            min_distance = float('inf')
            next_hop = None
            
            for neighbor_id in current_node.neighbor_nodes:
                neighbor = wsn_field.nodes[neighbor_id]
                if neighbor_id not in path:  # 순환 방지
                    for mal_id, mal_node in wsn_field.nodes.items():
                        if mal_node.node_type in ["malicious_inside", "malicious_outside"]:
                            distance = ((neighbor.pos_x - mal_node.pos_x)**2 + 
                                     (neighbor.pos_y - mal_node.pos_y)**2)**0.5
                            if distance < min_distance:
                                min_distance = distance
                                next_hop = neighbor_id
            
            if next_hop is None:
                # malicious 노드로 가는 경로를 찾지 못함
                return None
            
            path.append(next_hop)
            current_id = next_hop
        
        return path

    # 초기 공격 실행
    malicious_nodes = attack.execute_attack(num_attackers=NUM_ATTACKERS)
    logger.info(f"\nInitial Sinkhole Attack Executed:")
    logger.info(f"Number of malicious nodes: {len(malicious_nodes)}")
    logger.info(f"Malicious node IDs: {malicious_nodes}")

    # 보고서 전송 시뮬레이션
    for i in range(num_reports):
        # 공격 확률에 따라 소스 노드 선택
        if np.random.randint(1, 101) <= ATTACK_PROBABILITY:
            # affected 노드나 그 이웃 노드에서 보고서 생성
            affected_nodes, neighbor_nodes = get_affected_and_neighbor_nodes()
            candidate_nodes = affected_nodes + neighbor_nodes
            
            if candidate_nodes:
                source_node = np.random.choice(candidate_nodes)
                # malicious 노드로 향하는 경로 생성
                path = get_malicious_node_path(source_node)
                
                if path:
                    result = {
                        'report_id': i + 1,
                        'source_node': source_node,
                        'path': path,
                        'source_energy': wsn_field.nodes[source_node].energy_level
                    }
                    results.append(result)
                    
                    # 경로를 따라 패킷 전송 시뮬레이션
                    for j in range(len(path)-1):
                        current_id = path[j]
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
                        results.append(result)
            else:
                # affected 노드나 이웃이 없는 경우 일반 전송
                result = routing.simulate_reports(1)[0]
                if validate_path(result['path']):
                    results.append(result)
        else:
            # 일반 전송 (랜덤한 노드에서 BS로)
            available_nodes = [node_id for node_id, node in wsn_field.nodes.items() 
                             if node.node_type == "normal"]
            if available_nodes:
                source_node = np.random.choice(available_nodes)
                result = routing.simulate_reports(1, source_node=source_node)[0]
                if validate_path(result['path']):
                    results.append(result)

        # 보고서 경로 정보 출력
        if DEBUG_MODE and len(results) > 0:
            latest_result = results[-1]
            path_str = " -> ".join(map(str, latest_result['path']))
            logger.debug(f"Report #{i+1}: Source Node {latest_result['source_node']}, Path: {path_str}")

        # 진행상황 출력 (10% 단위)
        if i % (num_reports // 10) == 0:
            progress = (i / num_reports) * 100
            logger.info(f"Simulation Progress: {progress:.1f}%")

    end_time = time.time()
    elapsed_time = end_time - start_time

    logger.info(f"\nSimulation Time Information:")
    logger.info(f"Total time elapsed: {elapsed_time:.4f} seconds")
    logger.info(f"Average time per report: {elapsed_time/num_reports:.4f} seconds")
    logger.info(f"Total valid reports generated: {len(results)}")

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

def animate_report_transmission(wsn_field, results, classified_nodes):
    """보고서 전송 과정을 애니메이션으로 시각화"""
    if not ENABLE_ANIMATION:
        logger.info("Animation is disabled in config.py")
        return
        
    if not LIVE_ANIMATION and not SAVE_ANIMATION:
        logger.info("Both live animation and save animation are disabled")
        return
        
    if not results:
        logger.warning("No results to animate")
        return

    # 유효한 경로만 필터링
    valid_results = []
    for result in results:
        if not isinstance(result, dict) or 'path' not in result:
            continue
        path = result['path']
        if not isinstance(path, (list, tuple)) or len(path) < 2:
            continue
            
        is_valid = True
        for node_id in path[:-1]:
            if isinstance(node_id, str):
                if not node_id.isdigit():
                    is_valid = False
                    break
                node_id = int(node_id)
            if not isinstance(node_id, (int, str)) or node_id not in wsn_field.nodes:
                is_valid = False
                break
        if is_valid and path[-1] == "BS":
            valid_results.append(result)
    
    if not valid_results:
        logger.warning("No valid paths to animate")
        return
        
    logger.info(f"Starting animation with {len(valid_results)} valid paths")
    
    # 실시간 디스플레이를 위한 설정
    plt.ion() if LIVE_ANIMATION else plt.ioff()
    
    # Figure 및 Axes 설정
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    fig.canvas.manager.set_window_title('WSN Report Transmission Animation')
    
    # 필드 경계 설정
    ax.set_xlim(0, wsn_field.width)
    ax.set_ylim(0, wsn_field.height)
    
    def interpolate_position(start_pos, end_pos, ratio):
        """두 점 사이의 중간 위치를 계산"""
        return (
            start_pos[0] + (end_pos[0] - start_pos[0]) * ratio,
            start_pos[1] + (end_pos[1] - start_pos[1]) * ratio
        )
    
    # 기본 네트워크 구조 그리기
    def draw_base_network():
        ax.clear()
        # 공격 범위 원 그리기
        for node in wsn_field.nodes.values():
            if node.node_type in ["malicious_outside", "malicious_inside"]:
                attack_range = plt.Circle((node.pos_x, node.pos_y), 
                                        ATTACK_RANGE, 
                                        color='red', 
                                        fill=False, 
                                        linestyle='--', 
                                        alpha=0.5)
                ax.add_patch(attack_range)
        
        # 노드 그리기
        normal_x, normal_y, normal_colors = classified_nodes['normal']
        if normal_x:
            ax.scatter(normal_x, normal_y, c=normal_colors, marker='o', s=50, label='Normal Nodes')
        
        dead_x, dead_y = classified_nodes['dead']
        if dead_x:
            ax.scatter(dead_x, dead_y, c='black', marker='o', s=50, label='Dead Nodes')
        
        inside_x, inside_y = classified_nodes['inside_attack']
        if inside_x:
            ax.scatter(inside_x, inside_y, c='pink', marker='o', s=100, label='Inside Attackers')
        
        outside_x, outside_y = classified_nodes['outside_attack']
        if outside_x:
            ax.scatter(outside_x, outside_y, c='red', marker='o', s=100, label='Outside Attackers')
        
        affected_x, affected_y = classified_nodes['affected']
        if affected_x:
            ax.scatter(affected_x, affected_y, c='orange', marker='o', s=50, label='Affected Nodes')
        
        # BS 그리기
        ax.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
                  c='red', marker='^', s=200, label='Base Station')
        
        ax.grid(True)
        ax.set_xlabel('Field Width (m)')
        ax.set_ylabel('Field Height (m)')
        ax.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02))
    
    # 초기 네트워크 그리기
    draw_base_network()
    plt.draw()
    
    # 실시간 애니메이션
    if LIVE_ANIMATION:
        logger.info("Starting live animation...")
        for frame in range(len(valid_results)):
            try:
                result = valid_results[frame]
                path = result.get('path', [])
                
                if len(path) < 2:
                    continue
                
                # 전체 경로 그리기 (회색으로)
                for i in range(len(path)-1):
                    if path[i] not in wsn_field.nodes:
                        continue
                        
                    current = wsn_field.nodes[path[i]]
                    if path[i+1] == "BS":
                        next_x = wsn_field.base_station['x']
                        next_y = wsn_field.base_station['y']
                    else:
                        if path[i+1] not in wsn_field.nodes:
                            continue
                        next_node = wsn_field.nodes[path[i+1]]
                        next_x = next_node.pos_x
                        next_y = next_node.pos_y
                    
                    ax.plot([current.pos_x, next_x],
                           [current.pos_y, next_y],
                           'gray', linestyle='--', alpha=0.5)
                
                # 각 세그먼트를 따라 패킷 이동
                for i in range(len(path)-1):
                    if path[i] not in wsn_field.nodes:
                        continue
                        
                    current = wsn_field.nodes[path[i]]
                    current_pos = (current.pos_x, current.pos_y)
                    
                    if path[i+1] == "BS":
                        next_pos = (wsn_field.base_station['x'], wsn_field.base_station['y'])
                    else:
                        if path[i+1] not in wsn_field.nodes:
                            continue
                        next_node = wsn_field.nodes[path[i+1]]
                        next_pos = (next_node.pos_x, next_node.pos_y)
                    
                    # 현재 활성화된 노드 강조
                    ax.scatter(current_pos[0], current_pos[1],
                             c='yellow', marker='o', s=100,
                             edgecolor='red', linewidth=2)
                    
                    # 패킷 이동 애니메이션
                    for step in range(STEPS_PER_PATH + 1):
                        ratio = step / STEPS_PER_PATH
                        packet_pos = interpolate_position(current_pos, next_pos, ratio)
                        
                        # 이전 패킷 제거
                        for collection in ax.collections[:]:
                            if hasattr(collection, 'is_packet') and collection.is_packet:
                                collection.remove()
                        
                        # 현재 활성화된 경로 표시
                        ax.plot([current_pos[0], next_pos[0]],
                               [current_pos[1], next_pos[1]],
                               'r-', linewidth=2, alpha=0.8)
                        
                        # 패킷 그리기
                        packet = ax.scatter(packet_pos[0], packet_pos[1],
                                          c='white', marker='o', s=PACKET_SIZE,
                                          edgecolor='red', linewidth=2)
                        packet.is_packet = True  # 패킷 식별을 위한 속성 추가
                        
                        # 진행 상황 업데이트
                        ax.set_title(f'Report {frame+1}/{len(valid_results)}: Node {path[i]} → {path[i+1]}')
                        
                        # 화면 업데이트
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        plt.pause(ANIMATION_INTERVAL / (1000.0 * STEPS_PER_PATH))
                
            except Exception as e:
                logger.error(f"Error in frame {frame}: {str(e)}")
                continue
    
    # GIF 저장
    if SAVE_ANIMATION:
        logger.info("Creating animation for saving...")
        plt.ioff()
        anim = FuncAnimation(fig, update, frames=len(valid_results),
                           interval=ANIMATION_INTERVAL, repeat=False)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        anim_folder = os.path.join(script_dir, 'results')
        if not os.path.exists(anim_folder):
            os.makedirs(anim_folder)
        
        logger.info("Saving animation as GIF...")
        anim.save(os.path.join(anim_folder, 'report_transmission.gif'),
                 writer='pillow', fps=ANIMATION_FPS)
        logger.info("Animation saved successfully")
    
    if LIVE_ANIMATION:
        plt.show(block=True)  # 창이 닫힐 때까지 대기
    
    plt.close('all')

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
    
    # 5. 노드 분류
    classified_nodes = classify_wsn_nodes(wsn_field)
    
    # 6. 정적 네트워크 시각화
    plot_wsn_network(wsn_field, classified_nodes)
    
    # 7. 보고서 전송 애니메이션
    animate_report_transmission(wsn_field, transmission_results, classified_nodes)
    
    logger.info("==== WSN Simulation End ====")

if __name__ == "__main__":
    main()