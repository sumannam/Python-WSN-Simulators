import logging
from .DijkstraRouting import DijkstraRouting

logger = logging.getLogger('wsn_simulation')

def get_routing_protocol(protocol_name, wsn_field):
    """선택한 라우팅 프로토콜을 반환"""
    protocol_name = protocol_name.lower()
    
    if protocol_name == "dijkstra":
        return DijkstraRouting(wsn_field)
    # 나중에 다른 프로토콜을 추가할 수 있음
    # elif protocol_name == "aodv":
    #     return AODVRouting(wsn_field)
    # elif protocol_name == "leach":
    #     return LEACHRouting(wsn_field)
    else:
        logger.warning(f"Unknown routing protocol '{protocol_name}'. Using Dijkstra as default.")
        return DijkstraRouting(wsn_field) 