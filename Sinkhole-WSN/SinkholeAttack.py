import numpy as np

class SinkholeAttack:
    def __init__(self, field, attack_type="outside"):
        self.field = field
        self.attack_type = attack_type
        self.malicious_nodes = []
        self.grid_size = 100
        self.attack_range = 200  # 공격 영향 범위 (m)

    def calculate_node_density(self):
        """필드를 그리드로 나누어 각 영역의 노드 밀도 계산"""
        density_map = {}
        
        # 그리드별 노드 수 계산
        for node in self.field.nodes.values():
            grid_x = int(node.pos_x / self.grid_size)
            grid_y = int(node.pos_y / self.grid_size)
            grid_key = (grid_x, grid_y)
            
            if grid_key not in density_map:
                density_map[grid_key] = []
            density_map[grid_key].append(node.node_id)
        
        # 노드 수가 가장 많은 그리드 찾기
        dense_grids = sorted(density_map.items(), 
                           key=lambda x: len(x[1]), 
                           reverse=True)
        return dense_grids

    def affect_nodes_in_range(self, attacker_id):
        """공격 노드 주변의 노드들이 영향을 받도록 처리"""
        attacker = self.field.nodes[attacker_id]
        affected_nodes = 0  # 영향받은 노드 수 카운트
        
        for node_id, node in self.field.nodes.items():
            if node_id != attacker_id and node.node_type == "normal":  # 일반 노드만 영향을 받음
                # 노드와 공격자 사이의 거리 계산
                distance = np.sqrt(
                    (node.pos_x - attacker.pos_x)**2 + 
                    (node.pos_y - attacker.pos_y)**2
                )
                
                # 영향 범위 내에 있는 노드는 공격자를 next_hop으로 설정
                if distance <= self.attack_range:
                    affected_nodes += 1
                    node.next_hop = attacker_id
                    node.hop_count = 2  # 공격자를 통해 BS까지 2홉으로 설정
        
        print(f"Attacker {attacker_id} affected {affected_nodes} nodes within {self.attack_range}m range")

    def launch_outside_attack(self, num_attackers=1):
        """노드 밀도가 높은 지역에 외부 공격자 배치"""
        dense_grids = self.calculate_node_density()
        
        for i in range(min(num_attackers, len(dense_grids))):
            grid_pos = dense_grids[i][0]
            # 선택된 그리드 내의 랜덤한 위치 선정
            x = (grid_pos[0] * self.grid_size) + np.random.uniform(0, self.grid_size)
            y = (grid_pos[1] * self.grid_size) + np.random.uniform(0, self.grid_size)
            
            # 공격자 노드 생성
            attacker_id = max(self.field.nodes.keys()) + 1
            from MicazMotes import MicazMotes
            attacker = MicazMotes(attacker_id, x, y)
            attacker.node_type = "malicious_outside"
            attacker.energy_level = attacker.initial_energy
            attacker.next_hop = "BS"
            attacker.hop_count = 1
            
            self.field.nodes[attacker_id] = attacker
            self.malicious_nodes.append(attacker_id)
            
            # 주변 노드들에 영향 주기
            self.affect_nodes_in_range(attacker_id)
        
        # 이웃 노드 재탐색
        self.field.find_neighbors()

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
            node = self.field.nodes[node_id]
            node.node_type = "malicious_inside"
            node.energy_level = node.initial_energy
            node.next_hop = "BS"
            node.hop_count = 1
            self.malicious_nodes.append(node_id)

    def modify_routing_info(self):
        """공격자 노드의 라우팅 정보 조작 및 주변 노드 영향"""
        for attacker_id in self.malicious_nodes:
            # 공격자 노드 설정
            attacker = self.field.nodes[attacker_id]
            attacker.hop_count = 1
            attacker.next_hop = "BS"
            
            # 외부 공격의 경우 주변 노드들에 대한 영향 갱신
            if attacker.node_type == "malicious_outside":
                self.affect_nodes_in_range(attacker_id)
        
        # 이웃 노드 재탐색
        self.field.find_neighbors()

    def execute_attack(self, num_attackers=1):
        """싱크홀 공격 실행"""
        if self.attack_type == "outside":
            self.launch_outside_attack(num_attackers)
        else:
            self.launch_inside_attack(num_attackers)
            
        self.modify_routing_info()  # 라우팅 정보 조작
        return self.malicious_nodes