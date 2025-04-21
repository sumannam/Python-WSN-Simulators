"""
WSN Simulation Configuration Parameters
"""

# Simulation Parameters
RANDOM_SEED = 42          # 랜덤 시드
FIELD_SIZE = 1000         # 필드 크기 (m)
NUM_NODES = 500          # 센서 노드 수
BS_POSITION = (500, 500)  # 베이스 스테이션 위치 (x, y)

# Routing Parameters
ROUTING_PROTOCOL = "dijkstra"  # 라우팅 프로토콜 타입 ("dijkstra", "LEACH")

# Attack Parameters
ATTACK_TYPE = "outside"   # 공격 타입 ("outside" or "inside")
NUM_ATTACKERS = 1         # 공격자 수
ATTACK_PROBABILITY = 100   # 각 보고서마다 공격이 발생할 확률 (0 ~ 100)
ATTACK_TIMING = "0"      # 공격 시점 (보고서 발생 기준 "0", "30", "50", "70", "90")
ATTACK_RANGE = 150        # 공격 영향 범위 (m)

# Report Parameters
NUM_REPORTS = 1000         # 생성할 보고서 수

# Save Parameters
SAVE_FILE_NAME = 'final_nodes_state.csv'  # 결과 저장 파일명

# Animation Parameters
ENABLE_ANIMATION = True    # 애니메이션 활성화 여부
ANIMATION_INTERVAL = 200   # 애니메이션 프레임 간격 (ms)
ANIMATION_FPS = 1         # 애니메이션 FPS (GIF 저장용)
SAVE_ANIMATION = False    # 애니메이션 GIF 저장 여부
LIVE_ANIMATION = True     # 실시간 애니메이션 표시 여부
STEPS_PER_PATH = 10      # 각 경로 세그먼트당 애니메이션 단계 수
PACKET_SIZE = 1000        # 패킷 표시 크기

# 디버깅 모드 (True일 경우 상세 로그 출력)
DEBUG_MODE = False