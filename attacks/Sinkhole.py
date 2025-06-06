import numpy as np
from .network_attack_base import NetworkAttackBase

class Sinkhole(NetworkAttackBase):
    """
    Sinkhole attack implementation for wireless sensor networks.
    In a sinkhole attack, malicious nodes advertise attractive routes
    to attract traffic from other nodes.
    """
    
    def __init__(self, field, attack_type="outside", attack_range=200):
        """
        Initialize the sinkhole attack.
        
        Parameters:
        -----------
        field : Field object
            The field containing nodes to be attacked
        attack_type : str
            Type of attack ("outside" or "inside")
        attack_range : int
            Range of attack influence in meters
        """
        super().__init__(field, attack_type, attack_range)
        self.grid_size = 100  # Grid size for density calculation
        self.malicious_nodes = []

    def calculate_node_density(self):
        """필드를 4개 구역으로 나누고 각 구역의 노드 밀도 계산"""
        density_map = {}
        bs_x = self.field.base_station['x']
        bs_y = self.field.base_station['y']
        
        # 필드를 4개 구역으로 나눔
        quadrants = {
            'Q1': {'x_range': (0, self.field.width/2), 'y_range': (self.field.height/2, self.field.height)},
            'Q2': {'x_range': (self.field.width/2, self.field.width), 'y_range': (self.field.height/2, self.field.height)},
            'Q3': {'x_range': (0, self.field.width/2), 'y_range': (0, self.field.height/2)},
            'Q4': {'x_range': (self.field.width/2, self.field.width), 'y_range': (0, self.field.height/2)}
        }
        
        # 각 구역별로 그리드 밀도 계산
        for quadrant, ranges in quadrants.items():
            density_map[quadrant] = {}
            
            # 구역 중심점 계산
            quadrant_center_x = (ranges['x_range'][0] + ranges['x_range'][1]) / 2
            quadrant_center_y = (ranges['y_range'][0] + ranges['y_range'][1]) / 2
            
            # 해당 구역의 노드들에 대해 그리드 밀도 계산
            for node in self.field.nodes.values():
                if (ranges['x_range'][0] <= node.pos_x < ranges['x_range'][1] and 
                    ranges['y_range'][0] <= node.pos_y < ranges['y_range'][1]):
                    
                    grid_x = int((node.pos_x - ranges['x_range'][0]) / self.grid_size)
                    grid_y = int((node.pos_y - ranges['y_range'][0]) / self.grid_size)
                    grid_key = (grid_x, grid_y)
                    
                    if grid_key not in density_map[quadrant]:
                        density_map[quadrant][grid_key] = {
                            'nodes': [],
                            'center_x': ranges['x_range'][0] + (grid_x + 0.5) * self.grid_size,
                            'center_y': ranges['y_range'][0] + (grid_y + 0.5) * self.grid_size,
                            'distance_to_center': 0
                        }
                    
                    density_map[quadrant][grid_key]['nodes'].append(node.node_id)
                    
                    # 그리드 중심점과 구역 중심점 사이의 거리 계산
                    center_x = density_map[quadrant][grid_key]['center_x']
                    center_y = density_map[quadrant][grid_key]['center_y']
                    distance_to_center = np.sqrt(
                        (center_x - quadrant_center_x)**2 + 
                        (center_y - quadrant_center_y)**2
                    )
                    density_map[quadrant][grid_key]['distance_to_center'] = distance_to_center
        
        # 각 구역에서 가장 적절한 위치 선정 
        best_locations = {}
        for quadrant in quadrants:
            if density_map[quadrant]:
                # 노드 수가 많고 중심에 가까운 그리드 선택
                grids = sorted(
                    density_map[quadrant].items(),
                    key=lambda x: (len(x[1]['nodes']) / (x[1]['distance_to_center'] + 1)),
                    reverse=True
                )
                if grids:
                    best_locations[quadrant] = (grids[0][1]['center_x'], 
                                            grids[0][1]['center_y'], 
                                            len(grids[0][1]['nodes']))
        
        return best_locations

    def affect_nodes_in_range(self, attacker_id):
        """공격 노드 주변의 노드들이 영향을 받도록 처리"""
        attacker = self.field.nodes[attacker_id]
        affected_nodes = 0
        
        # 공격자 노드의 라우팅 정보 설정
        if attacker.node_type == "malicious_outside":
            attacker.hop_count = 0  # malicious_outside는 BS와 직접 연결된다고 광고
        else:
            attacker.hop_count = 1
        attacker.next_hop = "BS"
        attacker.energy_level = attacker.initial_energy
        
        # 주변 노드들의 라우팅을 강제로 공격자 노드로 변경
        for node_id, node in self.field.nodes.items():
            if node_id != attacker_id and node.node_type == "normal":
                distance = np.sqrt(
                    (node.pos_x - attacker.pos_x)**2 + 
                    (node.pos_y - attacker.pos_y)**2
                )
                
                if distance <= self.attack_range:
                    node.next_hop = attacker_id
                    # 공격 범위 내의 모든 노드는 malicious node와 1-hop 거리로 설정
                    node.hop_count = 1
                    node.node_type = "affected"
                    # distance_to_bs를 공격자 노드까지의 거리로 업데이트
                    node.distance_to_bs = distance
                    affected_nodes += 1
        
        print(f"Attacker {attacker_id} affected {affected_nodes} nodes within {self.attack_range}m range")


    def execute_attack(self, num_attackers=1):
        if self.attack_type == "outside":
            self.launch_outside_attack(num_attackers)
        else:
            self.launch_inside_attack(num_attackers)
        
        # routing.setup_routing() 호출 제거
        return self.malicious_nodes

    def launch_outside_attack(self, num_attackers=2):
        """두 개의 구역에 공격자 배치"""
        best_locations = self.calculate_node_density()
        
        # 노드 수가 많은 순서로 구역 정렬
        sorted_quadrants = sorted(
            best_locations.items(),
            key=lambda x: x[1][2],  # x[1][2]는 노드 수
            reverse=True
        )
        
        # 상위 두 구역에 공격자 배치
        for i in range(min(num_attackers, len(sorted_quadrants))):
            quadrant = sorted_quadrants[i][0]
            x, y, node_count = sorted_quadrants[i][1]
            
            # 위치에 약간의 랜덤성 추가
            x += np.random.uniform(-50, 50)
            y += np.random.uniform(-50, 50)
            
            print(f"Placing attacker in {quadrant} at ({x:.2f}, {y:.2f}), "
                f"nearby nodes: {node_count}")
            
            # 공격자 노드 생성
            attacker_id = max(self.field.nodes.keys()) + 1
            from core.nodes.MicazMotes import MicazMotes
            attacker = MicazMotes(attacker_id, x, y)
            attacker.node_type = "malicious_outside"
            attacker.energy_level = attacker.initial_energy
            attacker.next_hop = "BS"
            attacker.hop_count = 1  # Changed from 0 to 1 to match test expectations
            
            self.field.nodes[attacker_id] = attacker
            self.malicious_nodes.append(attacker_id)
            
            # 주변 노드들에 영향 주기
            self.affect_nodes_in_range(attacker_id)

    def launch_inside_attack(self, num_attackers=1):
        """내부 노드를 공격자로 변환"""
        dense_grids = self.calculate_node_density()
        candidate_nodes = []
        
        # 밀도 높은 지역의 노드들을 후보로 선정
        for grid_pos, nodes in dense_grids:
            candidate_nodes.extend(nodes)
            if len(candidate_nodes) >= num_attackers * 3:  # 충분한 후보 확보
                break
        
        # 후보 중에서 랜덤하게 선택
        target_nodes = np.random.choice(candidate_nodes, 
                                    size=num_attackers, 
                                    replace=False)
        
        for node_id in target_nodes:
            # node_id를 정수형으로 변환
            int_node_id = int(node_id)
            node = self.field.nodes[int_node_id]
            node.node_type = "malicious_inside"
            node.energy_level = node.initial_energy
            node.next_hop = "BS"
            node.hop_count = 1
            # 저장할 때도 정수형으로 저장
            self.malicious_nodes.append(int_node_id)
            
            # 내부 공격자도 주변 노드에 영향 주기
            self.affect_nodes_in_range(int_node_id)

    def modify_routing_info(self):
        """공격자 노드의 라우팅 정보 조작 및 주변 노드 영향"""
        for attacker_id in self.malicious_nodes:
            # 공격자 노드 설정
            attacker = self.field.nodes[attacker_id]
            if attacker.node_type == "malicious_outside":
                attacker.hop_count = 0
            else:
                attacker.hop_count = 1
            attacker.next_hop = "BS"
            
            # 외부 공격의 경우 주변 노드들에 대한 영향 갱신
            if attacker.node_type == "malicious_outside":
                self.affect_nodes_in_range(attacker_id)
        
        # 이웃 노드 재탐색
        self.field.find_neighbors()

    def get_malicious_node_path(self, source_node):
        """소스 노드에서 malicious 노드로의 경로를 찾는 메소드"""
        if source_node not in self.field.nodes:
            return None
            
        # malicious 노드 찾기
        malicious_nodes = [node_id for node_id, node in self.field.nodes.items() 
                         if node.node_type in ["malicious_inside", "malicious_outside"]]
        
        if not malicious_nodes:
            return None
            
        # 가장 가까운 malicious 노드 찾기
        min_distance = float('inf')
        closest_malicious = None
        
        for malicious_id in malicious_nodes:
            distance = self.field.calculate_distance(source_node, malicious_id)
            if distance < min_distance:
                min_distance = distance
                closest_malicious = malicious_id
                
        if closest_malicious is None:
            return None
            
        # 소스 노드에서 malicious 노드까지의 경로 찾기
        path = self.field.find_path(source_node, closest_malicious)
        
        if path:
            # malicious 노드에서 BS까지의 경로 찾기
            bs_path = self.field.find_path(closest_malicious, "BS")
            if bs_path:
                # 두 경로를 합치기 (malicious 노드는 한 번만 포함)
                return path[:-1] + bs_path
                
        # 경로를 찾지 못한 경우, affected 노드의 next_hop을 따라가기
        current_node = self.field.nodes[source_node]
        path = [source_node]
        
        while current_node.next_hop is not None:
            next_hop = current_node.next_hop
            if next_hop == "BS":
                path.append("BS")
                break
                
            if next_hop in malicious_nodes:
                path.append(next_hop)
                path.append("BS")
                return path
                
            path.append(next_hop)
            current_node = self.field.nodes[next_hop]
            
        return None

    def get_affected_and_neighbor_nodes(self):
        """affected 노드와 그 이웃 노드들을 반환하는 메소드"""
        affected_nodes = set()
        neighbor_nodes = set()
        
        # affected 노드 찾기
        for node_id, node in self.field.nodes.items():
            if node.node_type == "affected":
                affected_nodes.add(node_id)
                # affected 노드의 이웃 노드들 추가
                for neighbor_id in node.neighbors:
                    if self.field.nodes[neighbor_id].node_type == "normal":
                        neighbor_nodes.add(neighbor_id)
                        
        # affected 노드가 없는 경우, malicious 노드의 이웃 노드들을 affected로 설정
        if not affected_nodes:
            for node_id, node in self.field.nodes.items():
                if node.node_type in ["malicious_inside", "malicious_outside"]:
                    for neighbor_id in node.neighbors:
                        if self.field.nodes[neighbor_id].node_type == "normal":
                            self.field.nodes[neighbor_id].node_type = "affected"
                            affected_nodes.add(neighbor_id)
                            
        return affected_nodes, neighbor_nodes