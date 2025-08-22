CONFIG = {
    # 데이터를 수집할 Modbus TCP 서버(장비)의 IP 주소 목록입니다.
    # 여러 대의 장비를 추가하려면 쉼표로 구분하여 문자열을 추가합니다.
    # 예 ["192.168.0.100", "192.168.0.101", "192.168.0.102"]
    "ip_addresses": 
    [
        "192.168.0.110",
        "192.168.0.180",
    ],

    # Modbus TCP 통신 포트 번호입니다.
    "port": 502,

    # 동시에 로깅을 시도할 최대 장비(스레드)의 개수입니다.
    # 라즈베리파이의 성능이나 네트워크 부하를 고려하여 적절한 값으로 설정합니다.
    # 예를 들어 IP가 10개이고 이 값을 5으로 설정하면, 한 번에 5개씩 작업을 처리합니다.
    "max_concurrent_threads": 10,

    # 읽어올 Input Register의 범위를 지정합니다.
    # start_address 에는 시작 주소 값, count에는 읽어올 주소 갯수
    "input_register": {
        "start_address": 0,
        "count": 120
    },

    # 읽어올 Holding Register의 범위를 지정합니다.
    # start_address 에는 시작 주소 값, count에는 읽어올 주소 갯수
    "holding_register": {
        "start_address": 0,
        "count": 120
    },

    # 로그 파일이 저장될 폴더의 경로입니다.
    "log_path": "./modbus_logs",

    # 데이터를 수집하고 파일에 저장하는 주기입니다. (단위: 초)
    "log_interval_seconds": 5,

    # 로그 폴더 안에 보관할 최대 압축 파일(.zip) 개수입니다.
    # 이 개수를 초과하면 가장 오래된 압축 파일부터 자동으로 삭제됩니다.
    "max_zip_archives": 365
}