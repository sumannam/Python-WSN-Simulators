import os
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger('wsn_simulation')

def plot_wsn_network(wsn_field, classified_nodes, attack_range):
    """WSN 노드 배치 시각화"""
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
                   c=normal_colors, marker='o', s=35, label='Normal Nodes')
        # 일반 노드 ID 표시
        for i, (x, y) in enumerate(zip(normal_x, normal_y)):
            for node_id, node in wsn_field.nodes.items():
                if node.pos_x == x and node.pos_y == y:
                    plt.annotate(str(node_id), (x, y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=6, alpha=0.7)
    
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

def animate_report_transmission(wsn_field, results, classified_nodes, animation_config):
    """보고서 전송 과정을 애니메이션으로 시각화"""
    if not animation_config['ENABLE_ANIMATION']:
        logger.info("Animation is disabled in config.py")
        return
        
    if not animation_config['LIVE_ANIMATION'] and not animation_config['SAVE_ANIMATION']:
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
    plt.ion() if animation_config['LIVE_ANIMATION'] else plt.ioff()
    
    # Figure 및 Axes 설정
    fig = plt.figure(figsize=(8.4, 8.4))  # 70% 크기로 조정
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
                                        animation_config['ATTACK_RANGE'], 
                                        color='red', 
                                        fill=False, 
                                        linestyle='--', 
                                        alpha=0.5)
                ax.add_patch(attack_range)
        
        # 노드 그리기
        normal_x, normal_y, normal_colors = classified_nodes['normal']
        if normal_x:
            ax.scatter(normal_x, normal_y, c=normal_colors, marker='o', s=35, label='Normal Nodes')
        
        dead_x, dead_y = classified_nodes['dead']
        if dead_x:
            ax.scatter(dead_x, dead_y, c='black', marker='o', s=35, label='Dead Nodes')
        
        inside_x, inside_y = classified_nodes['inside_attack']
        if inside_x:
            ax.scatter(inside_x, inside_y, c='pink', marker='o', s=70, label='Inside Attackers')
        
        outside_x, outside_y = classified_nodes['outside_attack']
        if outside_x:
            ax.scatter(outside_x, outside_y, c='red', marker='o', s=70, label='Outside Attackers')
        
        affected_x, affected_y = classified_nodes['affected']
        if affected_x:
            ax.scatter(affected_x, affected_y, c='orange', marker='o', s=35, label='Affected Nodes')
        
        # BS 그리기
        ax.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
                  c='red', marker='^', s=140, label='Base Station')
        
        ax.grid(True)
        ax.set_xlabel('Field Width (m)')
        ax.set_ylabel('Field Height (m)')
        ax.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02))
    
    # 초기 네트워크 그리기
    draw_base_network()
    plt.draw()
    
    # 실시간 애니메이션
    if animation_config['LIVE_ANIMATION']:
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
                             c='yellow', marker='o', s=70,
                             edgecolor='red', linewidth=2)
                    
                    # 패킷 이동 애니메이션
                    for step in range(animation_config['STEPS_PER_PATH'] + 1):
                        ratio = step / animation_config['STEPS_PER_PATH']
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
                                          c='white', marker='o', s=animation_config['PACKET_SIZE'],
                                          edgecolor='red', linewidth=2)
                        packet.is_packet = True  # 패킷 식별을 위한 속성 추가
                        
                        # 진행 상황 업데이트
                        ax.set_title(f'Report {frame+1}/{len(valid_results)}: Node {path[i]} → {path[i+1]}')
                        
                        # 화면 업데이트
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        plt.pause(animation_config['ANIMATION_INTERVAL'] / (1000.0 * animation_config['STEPS_PER_PATH']))
                
            except Exception as e:
                logger.error(f"Error in frame {frame}: {str(e)}")
                continue
    
    # GIF 저장
    if animation_config['SAVE_ANIMATION']:
        logger.info("Creating animation for saving...")
        plt.ioff()
        anim = FuncAnimation(fig, update, frames=len(valid_results),
                           interval=animation_config['ANIMATION_INTERVAL'], repeat=False)
        
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        anim_folder = os.path.join(script_dir, 'results')
        if not os.path.exists(anim_folder):
            os.makedirs(anim_folder)
        
        logger.info("Saving animation as GIF...")
        anim.save(os.path.join(anim_folder, 'report_transmission.gif'),
                 writer='pillow', fps=animation_config['ANIMATION_FPS'])
        logger.info("Animation saved successfully")
    
    if animation_config['LIVE_ANIMATION']:
        plt.show(block=True)  # 창이 닫힐 때까지 대기
    
    plt.close('all')