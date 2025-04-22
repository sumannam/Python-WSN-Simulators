import logging

logger = logging.getLogger('wsn_simulation')

class NetworkAttackBase:
    """네트워크 공격의 기본 클래스"""
    
    def __init__(self, field, attack_type="outside", attack_range=200):
        """
        Initialize the network attack.
        
        Parameters:
        -----------
        field : Field object
            The field containing nodes to be attacked
        attack_type : str
            Type of attack ("outside" or "inside")
        attack_range : int
            Range of attack influence in meters
        """
        self.field = field
        self.attack_type = attack_type
        self.attack_range = attack_range
        self.malicious_nodes = []
    
    def analyze_network_statistics(self):
        """네트워크 통계 분석 및 출력"""
        total_energy = 0
        total_tx = 0
        total_rx = 0
        active_nodes = 0
        
        # 에너지와 패킷 전송/수신 통계
        nodes_with_energy = []
        nodes_with_tx = []
        nodes_with_rx = []
        
        for node_id, node in self.field.nodes.items():
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
        logger.info(f"Active Nodes: {active_nodes}/{len(self.field.nodes)}")
        logger.info(f"Total Energy Consumed: {total_energy:.6f} Joules")
        logger.info(f"Total TX Count: {total_tx}")
        logger.info(f"Total RX Count: {total_rx}")
        logger.info(f"Nodes with Energy Consumption: {len(nodes_with_energy)}/{len(self.field.nodes)} ({len(nodes_with_energy)/len(self.field.nodes)*100:.1f}%)")
        logger.info(f"Nodes with TX: {len(nodes_with_tx)}/{len(self.field.nodes)} ({len(nodes_with_tx)/len(self.field.nodes)*100:.1f}%)")
        logger.info(f"Nodes with RX: {len(nodes_with_rx)}/{len(self.field.nodes)} ({len(nodes_with_rx)/len(self.field.nodes)*100:.1f}%)")
        
        return {
            'active_nodes': active_nodes,
            'total_energy': total_energy,
            'total_tx': total_tx,
            'total_rx': total_rx,
            'nodes_with_energy': nodes_with_energy,
            'nodes_with_tx': nodes_with_tx,
            'nodes_with_rx': nodes_with_rx
        }
    
    def add_malicious_node(self, node_id):
        """Add a node to the list of malicious nodes"""
        if node_id not in self.malicious_nodes:
            self.malicious_nodes.append(node_id)
    
    def is_node_in_range(self, node_id, attacker_id):
        """
        Check if a node is within the attack range of an attacker.
        
        Parameters:
        -----------
        node_id : int
            ID of the node to check
        attacker_id : int
            ID of the attacker node
            
        Returns:
        --------
        bool : True if node is in range, False otherwise
        """
        node = self.field.nodes[node_id]
        attacker = self.field.nodes[attacker_id]
        
        distance = ((node.pos_x - attacker.pos_x)**2 + 
                   (node.pos_y - attacker.pos_y)**2)**0.5
                   
        return distance <= self.attack_range
    
    def execute_attack(self):
        """
        Execute the network attack.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute_attack()")

    def get_affected_and_neighbor_nodes(self):
        """affected 노드와 그 이웃 노드들의 목록을 반환"""
        affected_nodes = set()
        neighbor_nodes = set()
        
        # affected 노드 찾기
        for node_id, node in self.field.nodes.items():
            if node.node_type == "affected":
                affected_nodes.add(node_id)
                # affected 노드의 이웃 노드들 추가
                for neighbor_id in node.neighbor_nodes:
                    if self.field.nodes[neighbor_id].node_type == "normal":
                        neighbor_nodes.add(neighbor_id)
        
        return list(affected_nodes), list(neighbor_nodes)

    def get_malicious_node_path(self, source_node_id):
        """소스 노드에서 가장 가까운 malicious 노드로의 경로 생성"""
        path = [source_node_id]
        current_id = source_node_id
        
        while True:
            current_node = self.field.nodes[current_id]
            # 현재 노드의 이웃 중 malicious 노드 찾기
            malicious_neighbors = [n_id for n_id in current_node.neighbor_nodes 
                                if self.field.nodes[n_id].node_type in ["malicious_inside", "malicious_outside"]]
            
            if malicious_neighbors:
                # malicious 노드를 찾았으면 경로에 추가하고 종료
                path.append(malicious_neighbors[0])
                break
            
            # malicious 노드 방향으로 이동
            min_distance = float('inf')
            next_hop = None
            
            for neighbor_id in current_node.neighbor_nodes:
                neighbor = self.field.nodes[neighbor_id]
                if neighbor_id not in path:  # 순환 방지
                    for mal_id, mal_node in self.field.nodes.items():
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