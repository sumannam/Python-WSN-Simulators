import os
import matplotlib.pyplot as plt
import logging
from config import DEBUG_MODE

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
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

logger = logging.getLogger('wsn_simulation')

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

def plot_wsn_network(wsn_field, classified_nodes, attack_range):
    """WSN 노드 배치 시각화"""
    # next_hop이 없는 노드 출력
    disconnected_nodes = [node_id for node_id, node in wsn_field.nodes.items() if not node.next_hop]
    if disconnected_nodes:
        print(f"[경고] next_hop이 없는 노드: {disconnected_nodes}")
    else:
        print("모든 노드가 next_hop을 가지고 있습니다.")
    
    # disconnected_nodes의 좌표 추출
    disconnected_x = []
    disconnected_y = []
    for node_id in disconnected_nodes:
        node = wsn_field.nodes[node_id]
        disconnected_x.append(node.pos_x)
        disconnected_y.append(node.pos_y)
    
    # 창 크기를 70% 줄임 (12 -> 8.4)
    plt.figure(figsize=(8.4, 8.4))
    
    # 창 위치를 모니터 좌상단(0,0)으로 이동
    mngr = plt.get_current_fig_manager()
    # 백엔드가 TkAgg인 경우
    try:
        mngr.window.wm_geometry("+0+0")
    except:
        try:
            # Qt 백엔드인 경우
            mngr.window.setGeometry(0, 0, 850, 850)
        except:
            try:
                # WX 백엔드인 경우
                mngr.window.SetPosition((0, 0))
            except:
                logger.warning("Window position could not be set for this backend")
    
    # 필드 경계 설정
    plt.xlim(0, wsn_field.width)
    plt.ylim(0, wsn_field.height)
    
    # 공격 범위 원 그리기
    for node in wsn_field.nodes.values():
        if node.node_type in ["malicious_outside", "malicious_inside"]:
            attack_range_circle = plt.Circle((node.pos_x, node.pos_y), 
                                    attack_range, 
                                    color='red', 
                                    fill=False, 
                                    linestyle='--', 
                                    alpha=0.5)
            plt.gca().add_patch(attack_range_circle)
    
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
                        alpha=0.8 if is_affected else 0.5,
                        linewidth=3 if is_affected else 2)
            elif node.next_hop in wsn_field.nodes:
                next_node = wsn_field.nodes[node.next_hop]
                plt.plot([node.pos_x, next_node.pos_x],
                        [node.pos_y, next_node.pos_y],
                        'r-' if is_affected else 'gray',
                        alpha=0.8 if is_affected else 0.5,
                        linewidth=3 if is_affected else 2)
    
    # 노드 그리기 및 노드 ID 표시
    normal_x, normal_y, normal_colors = classified_nodes['normal']
    # disconnected_nodes를 normal에서 제외
    filtered_normal = [(x, y, c) for x, y, c in zip(normal_x, normal_y, normal_colors)
                       if (x, y) not in zip(disconnected_x, disconnected_y)]
    if filtered_normal:
        fx, fy, fc = zip(*filtered_normal)
        plt.scatter(fx, fy, c=fc, marker='o', s=35, label='Normal Nodes')
        # 일반 노드 ID 표시
        for i, (x, y) in enumerate(zip(fx, fy)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    # disconnected_nodes 노드 표시 (노란색)
    if disconnected_x:
        plt.scatter(disconnected_x, disconnected_y, c='yellow', marker='o', s=50, label='Disconnected Nodes', edgecolors='black', linewidths=1.5)
        for x, y in zip(disconnected_x, disconnected_y):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=1.0, color='black', weight='bold')
    
    dead_x, dead_y = classified_nodes['dead']
    if dead_x:
        plt.scatter(dead_x, dead_y, 
                   c='black', marker='o', s=35, label='Dead Nodes')
        # 죽은 노드 ID 표시
        for i, (x, y) in enumerate(zip(dead_x, dead_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    
    inside_x, inside_y = classified_nodes['inside_attack']
    if inside_x:
        plt.scatter(inside_x, inside_y, 
                   c='pink', marker='o', s=70, label='Inside Attackers')
        # 내부 공격자 노드 ID 표시
        for i, (x, y) in enumerate(zip(inside_x, inside_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    
    outside_x, outside_y = classified_nodes['outside_attack']
    if outside_x:
        plt.scatter(outside_x, outside_y, 
                   c='red', marker='o', s=70, label='Outside Attackers')
        # 외부 공격자 노드 ID 표시
        for i, (x, y) in enumerate(zip(outside_x, outside_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    
    affected_x, affected_y = classified_nodes['affected']
    if affected_x:
        plt.scatter(affected_x, affected_y, 
                   c='orange', marker='o', s=35, label='Affected Nodes')
        # 영향받은 노드 ID 표시
        for i, (x, y) in enumerate(zip(affected_x, affected_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    
    # BS 그리기
    plt.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
               c='red', marker='^', s=140, label='Base Station')
    plt.annotate('BS', (wsn_field.base_station['x'], wsn_field.base_station['y']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8, weight='bold')
    
    plt.title('WSN Node Deployment with Sinkhole Attacks')
    plt.xlabel('Field Width (m)')
    plt.ylabel('Field Height (m)')
    
    # 범례를 오른쪽 하단에 위치시키고 속성 조정
    plt.legend(loc='lower right', framealpha=0.9, frameon=True, 
              fontsize='small', markerscale=0.8,
              bbox_to_anchor=(0.99, 0.01))
    
    plt.grid(True)
    plt.axis('equal')
    
    # 그래프 저장
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plot_folder = os.path.join(script_dir, 'results')
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)
    plt.savefig(os.path.join(plot_folder, 'network_deployment.png'), 
               bbox_inches='tight', dpi=300)
    
    plt.show()