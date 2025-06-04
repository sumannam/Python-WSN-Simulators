# WSN (Wireless Sensor Network) Simulator

무선 센서 네트워크 시뮬레이터는 센서 노드들의 네트워크 동작을 시뮬레이션하고 분석하는 도구입니다.
Wireless Sensor Network Simulator is a tool for simulating and analyzing the network behavior of sensor nodes.

## 주요 기능 (Main Features)

- 센서 노드 배치 및 네트워크 구성 (Sensor node deployment and network configuration)
- Dijkstra 기반 라우팅 프로토콜 구현 (Dijkstra-based routing protocol implementation)
- 에너지 소비 모델링 (전송/수신 에너지 계산) (Energy consumption modeling - transmission/reception energy calculation)
- Sinkhole 공격 시뮬레이션 (Sinkhole attack simulation)
- 네트워크 시각화 및 애니메이션 (Network visualization and animation)
- 결과 데이터 저장 및 분석 (Result data storage and analysis)

## 설치 방법 (Installation)

1. 저장소 클론 (Clone the repository)
```bash
git clone https://github.com/yourusername/Python-WSN-Simulators.git
cd Python-WSN-Simulators
```

2. 가상환경 생성 및 활성화 (선택사항) (Create and activate virtual environment (optional))
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치 (Install dependencies)
```bash
pip install -r requirements.txt
```

## 사용 방법 (Usage)

1. 설정 파일 수정 (`config.py`) (Modify configuration file)
   - 필드 크기, 노드 수, 베이스스테이션 위치 등 설정 (Set field size, number of nodes, base station position, etc.)
   - 공격 파라미터 설정 (Set attack parameters)
   - 애니메이션 옵션 설정 (Set animation options)

2. 시뮬레이션 실행 (Run simulation)
```bash
python main.py
```

3. 결과 확인 (Check results)
   - `results/` 폴더에서 생성된 결과 파일 확인 (Check generated result files in `results/` folder)
   - 시뮬레이션 로그 확인 (Check simulation logs)
   - 네트워크 시각화 결과 확인 (Check network visualization results)

## 프로젝트 구조 (Project Structure)

```
Python-WSN-Simulators/
├── core/                    # 핵심 모듈 (Core modules)
│   ├── nodes/              # 노드 관련 클래스 (Node-related classes)
│   └── routing/            # 라우팅 프로토콜 (Routing protocols)
├── attacks/                # 공격 모델 (Attack models)
├── utils/                  # 유틸리티 함수 (Utility functions)
├── test/                   # 테스트 코드 (Test code)
├── results/                # 결과 파일 (Result files)
├── config.py              # 설정 파일 (Configuration file)
├── main.py                # 메인 실행 파일 (Main execution file)
└── requirements.txt       # 의존성 목록 (Dependencies list)
```

## 에너지 모델 (Energy Model)

- 전송 에너지: 16.25 µJ/바이트 (Transmission energy: 16.25 µJ/byte)
- 수신 에너지: 12.5 µJ/바이트 (Reception energy: 12.5 µJ/byte)
- 초기 에너지: 1 Joule/노드 (Initial energy: 1 Joule/node)

## 테스트 (Testing)

테스트 실행 (Run tests):
```bash
python -m pytest test/
```

## 라이선스 (License)

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
This project is licensed under the MIT License.

## 기여 방법 (How to Contribute)

1. Fork the Project
2. GitHub Issue 생성 및 번호 확인 (Create and check GitHub Issue number)
3. 브랜치 생성 (이슈 번호에 따라) (Create branch based on issue number)
   ```bash
   # 개발 작업 (Development work)
   git checkout -b dev/Github-Issue-##
   
   # 버그 수정 작업 (Bug fix work)
   git checkout -b bug/Github-Issue-##
   
   # 테스트 작업 (Test work)
   git checkout -b test/Github-Issue-##
   
   # 문서 작업 (Documentation work)
   git checkout -b doc/Github-Issue-##
   ```
4. 변경사항 커밋 (Commit changes)
   ```bash
   git commit -m 'Resolve #XX: 작업 내용 설명'
   ```
5. 브랜치 푸시 (Push branch)
   ```bash
   git push origin 브랜치이름
   ```
6. Pull Request 생성 (Create Pull Request)
   - PR 제목: "Resolve #XX: 작업 내용" (PR title: "Resolve #XX: Work description")
   - PR 설명에 관련 이슈 번호 링크 (Link related issue number in PR description)