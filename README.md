# Modbus 로거

이 프로젝트는 Modbus TCP 장비를 위한 Python 기반 데이터 로거입니다. 여러 장비에 동시에 연결하여 레지스터 데이터를 읽고 CSV 파일에 기록할 수 있습니다. 또한, 매일 로그 파일을 압축하고 오래된 파일을 자동으로 정리하는 등 로그 파일 관리 기능을 제공합니다.

## 주요 기능

- **동시 로깅:** 스레드 풀을 사용하여 여러 Modbus TCP 장비에 동시에 연결하고 데이터를 기록합니다.
- **자동 압축:** 매일 생성된 로그 파일을 ZIP 파일로 자동 압축합니다.
- **로그 관리:** 설정된 보관 기간이 지난 오래된 로그 아카이브를 자동으로 삭제하여 디스크 공간을 관리합니다.

## 설치 및 실행 방법 (Windows/Linux/Raspberry Pi)

이 섹션에서는 Python과 Git만 설치된 새로운 환경에서 Modbus 로거를 설치하고 실행하는 방법을 단계별로 안내합니다.

### 1. Git 설치 확인

먼저, `git`이 설치되어 있는지 확인해야 합니다. 터미널(Windows에서는 `cmd` 또는 `PowerShell`)을 열고 다음 명령어를 입력하세요.

```bash
git --version
```

만약 버전 정보가 표시되지 않는다면, [Git 공식 웹사이트](https://git-scm.com/downloads)에서 Git을 다운로드하여 설치해야 합니다.

### 2. 프로젝트 다운로드 (Git Clone)

사용자가 원하는 경로로 이동한 후, 다음 명령어를 사용하여 GitHub에서 프로젝트를 다운로드합니다.

```bash
git clone https://github.com/H2-wsong/Modbus_Logger.git
```

다운로드가 완료되면 `Modbus_Logger`라는 이름의 폴더가 생성됩니다. 다음 명령어로 폴더에 들어갑니다.

```bash
cd Modbus_Logger
```

### 3. 필요 라이브러리 설치

프로젝트 실행에 필요한 라이브러리들을 `requirements.txt` 파일을 이용하여 한 번에 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. 로거 설정

`Source/config.py` 파일을 열어 로깅 설정을 수정합니다. 텍스트 편집기(예: `nano`, `vim`, `notepad++` 등)를 사용하여 파일을 수정할 수 있습니다.

- `ip_addresses`: 연결할 Modbus TCP 장비의 IP 주소 목록입니다.
- `port`: Modbus TCP 포트 번호입니다. (기본값: 502)
- `max_concurrent_threads`: 동시에 로깅할 최대 장비 수입니다.
- `input_register`: 읽어올 입력 레지스터의 시작 주소와 개수입니다.
- `holding_register`: 읽어올 홀딩 레지스터의 시작 주소와 개수입니다.
- `log_path`: 로그 파일이 저장될 디렉토리입니다.
- `log_interval_seconds`: 데이터를 로깅할 주기(초)입니다.
- `max_zip_archives`: 보관할 일일 ZIP 아카이브의 최대 개수입니다.

### 5. 로거 실행

모든 설정이 완료되면, 다음 명령어를 사용하여 로거를 시작합니다.

```bash
python main.py
```

로거가 실행되면 터미널에 로그가 출력되기 시작합니다. 로거를 종료하려면 터미널에서 `Ctrl+C`를 누르세요.

## 로그 파일 구조

- 로그 파일은 `log_path` 폴더 안에 각 장비의 IP 주소별로 생성된 폴더 내에 저장됩니다.
- 파일 이름은 `YYYYMMDD_Input.csv`, `YYYYMMDD_Holding.csv` 형식으로 매일 하나의 파일에 데이터가 누적 기록됩니다.
- 매일 자정이 되면, 전날의 CSV 로그 파일들은 `YYYYMMDD_IP주소_logs.zip` 형태의 압축 파일로 변환되어 `log_path` 폴더에 저장되고, 원본 CSV 파일은 삭제됩니다.