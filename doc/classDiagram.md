classDiagram
    %% attacks 모듈
    class NetworkAttackBase {
        <<abstract>>
        +field: Field
        +attack_type: string
        +attack_range: int
        +malicious_nodes: list
        +__init__(field, attack_type, attack_range)
        +execute_attack(num_attackers): list
        +add_malicious_node(node_id): void
        +is_node_in_range(node_id, attacker_id): bool
        +modify_routing_info(): void
    }
    
    class Sinkhole {
        +grid_size: int
        +affected_nodes_count: int
        +__init__(field, attack_type, attack_range)
        +calculate_node_density(): dict
        +affect_nodes_in_range(attacker_id): int
        +execute_attack(num_attackers): list
        +launch_outside_attack(num_attackers): void
        +launch_inside_attack(num_attackers): void
        +modify_routing_info(): void
    }
    
    NetworkAttackBase <|-- Sinkhole
    
    %% core/nodes 모듈
    class Sensors {
        +node_id: int
        +pos_x: float
        +pos_y: float
        +status: string
        +node_type: string
        +neighbors: list
        +neighbor_nodes: list
        +next_hop: int
        +hop_count: float
        +route_changes: int
        +distance_to_bs: float
        +tx_count: int
        +rx_count: int
        +__init__(node_id, pos_x, pos_y)
        +get_location(): tuple
        +calculate_distance_to_bs(bs_x, bs_y): float
        +get_node_info(): dict
        +get_node_state_dict(): dict
    }
    
    class MicazMotes {
        +comm_range: float
        +data_rate: int
        +voltage: float
        +tx_current: float
        +rx_current: float
        +sleep_current: float
        +tx_power: float
        +rx_power: float
        +sleep_power: float
        +initial_energy: float
        +energy_level: float
        +consumed_energy_tx: float
        +consumed_energy_rx: float
        +total_consumed_energy: float
        +__init__(node_id, pos_x, pos_y)
        +add_neighbor(neighbor_id): void
        +remove_neighbor(neighbor_id): void
        #_calculate_power_consumption(): void
        +calculate_packet_time(packet_size_bytes): float
        +transmit_packet(packet_size_bytes): float
        +receive_packet(packet_size_bytes): float
        +get_energy_info(): dict
        +get_node_state_dict(): dict
    }
    
    %% 라우팅 관련 클래스
    class BaseRoutingProtocol {
        <<abstract>>
        +field: Field
        +__init__(field)
        +setup_routing(): void
        +get_path_to_bs(node_id): list
        +process_single_report(report_id): dict
        +simulate_reports(num_reports): list
        #_extend_communication_range(): void
    }
    
    class DijkstraRouting {
        +__init__(field)
        +setup_routing(): void
        #_connect_direct_to_bs(): void
        #_apply_dijkstra_routing(): void
        #_connect_nodes_iteratively(unconnected_nodes, connected_nodes): void
        #_connect_nodes_one_round(unconnected_nodes, connected_nodes): set
        #_find_best_next_hop(node, connected_nodes): int
    }
    
    class Field {
        +width: float
        +height: float
        +nodes: dict
        +base_station: dict
        +__init__(width, height)
        +deploy_nodes(num_nodes): void
        +set_base_station(x, y): void
        +find_neighbors(): void
        +find_unconnected_nodes(): list
        +get_network_stats(): dict
        +create_node(node_id, pos_x, pos_y): MicazMotes
    }
    
    Sensors <|-- MicazMotes
    Field *-- MicazMotes
    BaseRoutingProtocol <|-- DijkstraRouting
    BaseRoutingProtocol --* Field
    NetworkAttackBase --* Field
    
    %% utils 모듈
    class visualize_network {
        +draw(field): void
    }
    visualize_network ..> Field
    
    %% logging 모듈
    class Logger {
        +setup_logging(): Logger
    }
    
    %% 시뮬레이션 모듈
    class WsnSimulation {
        +logger: Logger
        +simulate_with_attack(field, routing, attack_timing, num_reports): list
        +plot_wsn_network(field, classified_nodes): void
        +get_routing_protocol(protocol_name, field): BaseRoutingProtocol
    }
    
    WsnSimulation ..> Field
    WsnSimulation ..> BaseRoutingProtocol
    WsnSimulation ..> DijkstraRouting
    WsnSimulation ..> Sinkhole
    WsnSimulation ..> visualize_network
    WsnSimulation ..> Logger