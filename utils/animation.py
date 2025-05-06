import matplotlib.pyplot as plt
import logging
from matplotlib.animation import FuncAnimation

def animate_report_transmission(wsn_field, results, classified_nodes, animation_config):
    logger = logging.getLogger('wsn_simulation')
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
    for i, result in enumerate(valid_results[:5]):
        logger.info(f"샘플 경로 {i}: {result['path']}")
    plt.ion() if animation_config['LIVE_ANIMATION'] else plt.ioff()
    fig = plt.figure(figsize=(8.4, 8.4))
    ax = fig.add_subplot(111)
    fig.canvas.manager.set_window_title('WSN Report Transmission Animation')
    ax.set_xlim(0, wsn_field.width)
    ax.set_ylim(0, wsn_field.height)
    def interpolate_position(start_pos, end_pos, ratio):
        return (
            start_pos[0] + (end_pos[0] - start_pos[0]) * ratio,
            start_pos[1] + (end_pos[1] - start_pos[1]) * ratio
        )
    def draw_base_network():
        ax.clear()
        for node in wsn_field.nodes.values():
            if node.node_type in ["malicious_outside", "malicious_inside"]:
                attack_range = plt.Circle((node.pos_x, node.pos_y), 
                                        animation_config['ATTACK_RANGE'], 
                                        color='red', 
                                        fill=False, 
                                        linestyle='--', 
                                        alpha=0.5)
                ax.add_patch(attack_range)
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
        ax.scatter(wsn_field.base_station['x'], wsn_field.base_station['y'],
                  c='red', marker='^', s=140, label='Base Station')
        ax.grid(True)
        ax.set_xlabel('Field Width (m)')
        ax.set_ylabel('Field Height (m)')
        ax.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02))
    draw_base_network()
    plt.draw()
    if animation_config['LIVE_ANIMATION']:
        logger.info("Starting live animation...")
        last_packet = None  # 패킷 추적용
        for frame in range(len(valid_results)):
            try:
                result = valid_results[frame]
                path = result.get('path', [])
                logger.info(f"[애니메이션] Report {frame+1}/{len(valid_results)}: Path = {path}")
                if len(path) < 2:
                    continue
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
                    ax.scatter(current_pos[0], current_pos[1],
                             c='yellow', marker='o', s=70,
                             edgecolor='red', linewidth=2)
                    for step in range(animation_config['STEPS_PER_PATH'] + 1):
                        ratio = step / animation_config['STEPS_PER_PATH']
                        packet_pos = interpolate_position(current_pos, next_pos, ratio)
                        if last_packet is not None:
                            last_packet.remove()
                            last_packet = None
                        ax.plot([current_pos[0], next_pos[0]],
                               [current_pos[1], next_pos[1]],
                               'r-', linewidth=2, alpha=0.8)
                        last_packet = ax.scatter(packet_pos[0], packet_pos[1],
                                              c='lime', marker='o', s=animation_config['PACKET_SIZE'],
                                              edgecolor='red', linewidth=2)
                        ax.set_title(f'Report {frame+1}/{len(valid_results)}: Node {path[i]} → {path[i+1]}')
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        plt.pause(0.15)
            except Exception as e:
                logger.error(f"Error in frame {frame}: {str(e)}")
                continue
    if animation_config['SAVE_ANIMATION']:
        logger.info("Creating animation for saving...")
        plt.ioff()
        # GIF 저장 기능은 필요시 구현
    if animation_config['LIVE_ANIMATION']:
        plt.show(block=True)
    plt.close('all') 