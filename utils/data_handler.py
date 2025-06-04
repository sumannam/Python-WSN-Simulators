import os
import csv
import logging

logger = logging.getLogger('wsn_simulation')

def save_nodes_state(wsn_field, filename='nodes_state.csv'):
    """전체 네트워크의 노드 상태를 CSV로 저장
    
    Parameters:
    -----------
    wsn_field : Field object
        노드 정보를 포함하고 있는 필드 객체
    filename : str
        저장할 CSV 파일 이름
    """
    # 현재 스크립트 파일의 디렉토리 경로 가져오기
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # results 폴더 경로 생성
    folder_path = os.path.join(script_dir, 'results')
    
    # 폴더가 없으면 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, filename)

    # 첫 번째 노드에서 필드명 가져오기
    first_node = next(iter(wsn_field.nodes.values()))
    fieldnames = list(first_node.get_node_state_dict().keys())
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # 각 노드의 상태 정보를 CSV에 기록
            for node in wsn_field.nodes.values():
                writer.writerow(node.get_node_state_dict())
        
        logger.info(f"파일이 성공적으로 저장되었습니다: {file_path}")
    except Exception as e:
        logger.error(f"파일 저장 중 오류 발생: {e}")
        logger.error(f"시도한 경로: {file_path}")

def load_nodes_state(filename='nodes_state.csv'):
    """CSV 파일에서 노드 상태 정보를 로드
    
    Parameters:
    -----------
    filename : str
        로드할 CSV 파일 이름
        
    Returns:
    --------
    list : 노드 상태 정보를 담은 딕셔너리 리스트
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(script_dir, 'results', filename)
    
    nodes_data = []
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 숫자형 데이터 변환
                for key, value in row.items():
                    try:
                        if '.' in value:
                            row[key] = float(value)
                        else:
                            row[key] = int(value)
                    except ValueError:
                        # 숫자로 변환할 수 없는 경우 문자열 그대로 유지
                        pass
                nodes_data.append(row)
        
        logger.info(f"파일을 성공적으로 로드했습니다: {file_path}")
        return nodes_data
    except Exception as e:
        logger.error(f"파일 로드 중 오류 발생: {e}")
        logger.error(f"시도한 경로: {file_path}")
        return []

def save_simulation_results(results, filename='simulation_results.csv'):
    """시뮬레이션 결과를 CSV 파일로 저장
    
    Parameters:
    -----------
    results : list
        시뮬레이션 결과 데이터 리스트
    filename : str
        저장할 CSV 파일 이름
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder_path = os.path.join(script_dir, 'results')
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, filename)
    
    try:
        # 결과가 비어있지 않은 경우에만 저장
        if results:
            # source_energy를 제외한 필드명만 사용
            fieldnames = ['report_id', 'source_node', 'path']
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # numpy.int64를 일반 정수로 변환하여 저장
                for result in results:
                    # source_energy를 제외한 데이터만 저장
                    filtered_result = {k: v for k, v in result.items() if k in fieldnames}
                    
                    # path 리스트의 각 요소를 정수로 변환
                    if 'path' in filtered_result:
                        path = filtered_result['path']
                        converted_path = []
                        for node in path:
                            if node == 'BS':
                                converted_path.append('BS')
                            else:
                                # numpy.int64나 다른 숫자 타입을 일반 정수로 변환
                                converted_path.append(str(int(node)))
                        filtered_result['path'] = converted_path
                    
                    writer.writerow(filtered_result)
            
            logger.info(f"시뮬레이션 결과가 저장되었습니다: {file_path}")
        else:
            logger.warning("저장할 시뮬레이션 결과가 없습니다.")
    except Exception as e:
        logger.error(f"결과 저장 중 오류 발생: {e}")
        logger.error(f"시도한 경로: {file_path}") 