# Python based WSN Simulators

이 디렉토리는 WSN(무선 센서 네트워크) 시뮬레이터의 테스트 코드를 포함하고 있습니다.

## 디렉토리 구조

```
test/
├── __pycache__/          # Python 캐시 파일
├── test_results/         # 테스트 결과 저장 디렉토리
├── test_core/           # 핵심 컴포넌트 테스트
│   ├── test_Field.py    # Field 클래스 테스트
│   ├── test_MicazMotes.py  # MicazMotes 클래스 테스트
│   └── test_DijkstraRouting.py  # DijkstraRouting 클래스 테스트
├── test_attacks/        # 네트워크 공격 관련 테스트
│   └── test_Sinkhole.py  # Sinkhole 공격 테스트
├── test_main/          # 메인 애플리케이션 테스트
│   └── test_Main.py    # 메인 애플리케이션 테스트
├── test_config.py      # 테스트 설정 파일
└── test_all.py         # 전체 테스트 실행 스크립트
```

## 테스트 구성

### 1. 핵심 컴포넌트 테스트 (test_core/)

#### test_Field.py
- 네트워크 필드 관리 기능 테스트
  - 노드 배치 및 초기화
  - 베이스 스테이션 설정
  - 이웃 노드 탐색
  - 네트워크 통계 수집

#### test_MicazMotes.py
- MicaZ 모트 노드 기능 테스트
  - 노드 초기화 및 기본 속성
  - 전력 계산 (전압, 전류 기반)
  - 패킷 전송/수신 기능
  - 에너지 소비 모델링
  - 이웃 노드 관리
  - 노드 상태 정보 관리

#### test_DijkstraRouting.py
- Dijkstra 라우팅 알고리즘 테스트
  - 최단 경로 계산
  - 라우팅 테이블 업데이트
  - BS와의 직접 연결 처리
  - 경로 변경 추적

### 2. 공격 테스트 (test_attacks/)

#### test_Sinkhole.py
- Sinkhole 공격 시나리오 테스트
  - 공격자 노드 배치
  - 라우팅 정보 조작
  - 영향받는 노드 식별
  - 공격 효과 측정
  - 네트워크 통계 분석

### 3. 메인 애플리케이션 테스트 (test_main/)

#### test_Main.py
- 전체 시뮬레이션 기능 테스트
  - 시뮬레이션 초기화
  - 노드 배치 및 설정
  - 라우팅 설정
  - 공격 시나리오 실행
  - 결과 시각화
  - 데이터 저장 및 로드

## 테스트 실행 방법

### 1. 전체 테스트 실행
```bash
python test_all.py
```

### 2. 특정 테스트 모듈 실행
```bash
# 핵심 컴포넌트 테스트
python -m unittest test_core/test_Field.py
python -m unittest test_core/test_MicazMotes.py
python -m unittest test_core/test_DijkstraRouting.py

# 공격 테스트
python -m unittest test_attacks/test_Sinkhole.py

# 메인 애플리케이션 테스트
python -m unittest test_main/test_Main.py
```

### 3. 특정 테스트 케이스 실행
```bash
# 특정 테스트 클래스 실행
python -m unittest test_core.test_MicazMotes.test_MicazMotes

# 특정 테스트 메서드 실행
python -m unittest test_core.test_MicazMotes.test_MicazMotes.test_power_calculation
```

## 테스트 결과

테스트 실행 결과는 `test_results/` 디렉토리에 저장됩니다. 각 테스트 실행마다 다음 정보가 기록됩니다:
- 테스트 실행 시간
- 성공/실패한 테스트 케이스 수
- 상세한 오류 메시지 (실패한 경우)

## 테스트 파일 유지보수 가이드라인

### 1. 새로운 클래스 추가 시 테스트 파일 생성 규칙
- `core/nodes/`에 새 클래스 추가 시 → `test_core/test_[ClassName].py` 생성
- `core/routing/`에 새 클래스 추가 시 → `test_core/test_[ClassName].py` 생성
- `attacks/`에 새 클래스 추가 시 → `test_attacks/test_[ClassName].py` 생성

### 2. 테스트 파일 작성 규칙
- 테스트 클래스 이름은 `test_[ClassName]` 형식으로 작성
- 각 테스트 메서드는 `test_[method_name]` 형식으로 작성
- 모든 public 메서드에 대한 테스트 케이스 작성
- 예외 처리 및 경계 조건 테스트 포함
- 실제 하드웨어 사양을 반영한 값 사용

### 3. 테스트 커버리지
- 모든 public 메서드에 대한 테스트 케이스 작성
- 일반적인 사용 사례와 예외 상황 모두 테스트
- 에너지 소비, 통신 범위 등 실제 하드웨어 제약 조건 반영

## 주의사항

1. 테스트 실행 전 프로젝트 루트 디렉토리가 Python 경로에 포함되어 있는지 확인하세요.
2. 일부 테스트는 실제 하드웨어 사양을 기반으로 하므로, 값이 정확한지 확인하세요.
3. 테스트 실행 시 충분한 시스템 리소스가 필요할 수 있습니다.
4. 새로운 클래스를 추가할 때는 반드시 해당하는 테스트 파일도 함께 생성하세요.
5. 테스트 코드는 실제 코드와 동일한 수준의 품질을 유지해야 합니다. 