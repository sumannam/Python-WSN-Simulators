import os
import sys

if 'win' in sys.platform:  # Windows
    sys.path.append('D:\\Git\\Python-WSN-Simulators')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\test')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\attacks')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core\\nodes')
    sys.path.append('D:\\Git\\Python-WSN-Simulators\\core\\routing')
    # sys.path.append('D:\\Git\\Python-WSN-Simulators\\utils')
else:  # Linux, Unix, MacOS
    sys.path.append('.')
    
    
"""
WSN Simulation Configuration Parameters
"""

# Simulation Parameters
RANDOM_SEED = 42          # 랜덤 시드
FIELD_SIZE = 2000         # 필드 크기 (m)
NUM_NODES = 1000          # 센서 노드 수
BS_POSITION = (1000, 1000)  # 베이스 스테이션 위치 (x, y)

# Routing Parameters
ROUTING_PROTOCOL = "dijkstra"  # 라우팅 프로토콜 타입 ("dijkstra", "LEACH")

# Attack Parameters
ATTACK_TYPE = "outside"   # 공격 타입 ("outside" or "inside")
NUM_ATTACKERS = 1         # 공격자 수
ATTACK_PROBABILITY = 50   # 각 보고서마다 공격이 발생할 확률 (0 ~ 100)
ATTACK_TIMING = "0"      # 공격 시점 (보고서 발생 기준 "0", "30", "50", "70", "90")
ATTACK_RANGE = 150        # 공격 영향 범위 (m)

# Report Parameters
NUM_REPORTS = 100         # 생성할 보고서 수

# Save Parameters
SAVE_FILE_NAME = 'final_nodes_state.csv'  # 결과 저장 파일명

# 디버깅 모드 (True일 경우 상세 로그 출력)
DEBUG_MODE = False