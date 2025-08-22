# Modbus 로거

이 프로젝트는 Modbus TCP 장비를 위한 Python 기반 데이터 로거입니다. 여러 장비에 동시에 연결하여 레지스터 데이터를 읽고 CSV 파일에 기록할 수 있습니다. 또한, 매일 로그 파일을 압축하고 오래된 파일을 자동으로 정리하는 등 로그 파일 관리 기능을 제공합니다.

## 주요 기능

- **동시 로깅:** 스레드 풀을 사용하여 여러 Modbus TCP 장비에 동시에 연결하고 데이터를 기록합니다.
- **자동 압축:** 매일 생성된 로그 파일을 ZIP 파일로 자동 압축합니다.
- **로그 관리:** 설정된 보관 기간이 지난 오래된 로그 아카이브를 자동으로 삭제하여 디스크 공간을 관리합니다.

## 설치 방법

1.  이 저장소를 로컬 컴퓨터 또는 라즈베리 파이에 복제합니다:
    ```bash
    git clone https://github.com/your-username/MBMS_Logger.git
    cd MBMS_Logger
    ```

2.  pip를 사용하여 필요한 Python 라이브러리를 설치합니다:
    ```bash
    pip install -r requirements.txt
    ```

## 설정 방법

모든 설정은 `Source/config.py` 파일에서 할 수 있습니다. 이 파일을 열고 `CONFIG` 딕셔너리의 값을 사용 환경에 맞게 수정하십시오.

- `ip_addresses`: 연결할 Modbus TCP 장비의 IP 주소 목록입니다.
- `port`: Modbus TCP 포트 번호입니다. (기본값: 502)
- `max_concurrent_threads`: 동시에 로깅할 최대 장비 수입니다.
- `input_register`: 읽어올 입력 레지스터의 시작 주소와 개수입니다.
- `holding_register`: 읽어올 홀딩 레지스터의 시작 주소와 개수입니다.
- `log_path`: 로그 파일이 저장될 디렉토리입니다.
- `log_interval_seconds`: 데이터를 로깅할 주기(초)입니다.
- `max_zip_archives`: 보관할 일일 ZIP 아카이브의 최대 개수입니다.

## 사용 방법

로거를 시작하려면 `main.py` 스크립트를 실행하십시오:

```bash
python main.py
```

로거가 백그라운드에서 실행되며 설정된 장비의 데이터를 계속 기록합니다. 로거를 중지하려면 `Ctrl+C`를 누르십시오.

## 로그 파일 구조

로거는 매일 각 장비에 대해 새로운 CSV 파일을 생성합니다. 파일 이름은 다음 형식을 따릅니다:

`YYYYMMDD_HHMMSS_<IP_Address>_Input.csv`
`YYYYMMDD_HHMMSS_<IP_Address>_Holding.csv`

- `YYYYMMDD`: 로그가 생성된 연도, 월, 일입니다.
- `HHMMSS`: 로그가 생성된 시, 분, 초입니다.
- `<IP_Address>`: Modbus 장비의 IP 주소입니다.

매일 자정이 되면, 로거는 그날 생성된 모든 CSV 파일을 `YYYYMMDD_logs.zip`이라는 단일 ZIP 파일로 압축합니다.
