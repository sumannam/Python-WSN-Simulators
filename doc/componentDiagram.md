flowchart TD
    subgraph "Python-WSN-Simulators"
        main[main.py]
        
        subgraph "core 모듈"
            core_field[Field]
            core_sensor[Sensors]
            core_routing[ShortestPathRouting]
            core_sensor --> core_field
            core_routing --> core_field
        end
        
        subgraph "attacks 모듈"
            attack_base[NetworkAttackBase]
            attack_sinkhole[SinkholeAttack]
            attack_base --> attack_sinkhole
        end
        
        subgraph "utils 모듈"
            utils_viz[visualize_network]
            utils_log[Logger]
        end
        
        subgraph "test 모듈"
            test_sim[Simulation Tests]
            test_attack[Attack Tests]
        end
        
        %% 메인에서의 컴포넌트 활용
        main --> core_field
        main --> core_routing
        main --> attack_sinkhole
        main --> utils_viz
        main --> utils_log
        
        %% 모듈 간 상호작용
        attack_sinkhole --> core_field
        utils_viz --> core_field
        test_sim --> core_field
        test_sim --> core_routing
        test_attack --> attack_sinkhole
        
        %% 데이터 흐름
        core_field -- "네트워크 상태" --> utils_viz
        attack_sinkhole -- "공격 영향" --> core_field
        core_routing -- "라우팅 정보" --> core_field
    end
    
    %% 컴포넌트 설명
    classDef main fill:#f96,stroke:#333,stroke-width:2px
    classDef core fill:#bbf,stroke:#333
    classDef attack fill:#f66,stroke:#333
    classDef utils fill:#bfb,stroke:#333
    classDef test fill:#fcf,stroke:#333
    
    class main main
    class core_field,core_sensor,core_routing core
    class attack_base,attack_sinkhole attack
    class utils_viz,utils_log utils
    class test_sim,test_attack test