import os

project_path = os.path.abspath(os.path.dirname(__file__))

bat_content = f"""@echo off
cd "{project_path}"
pythonw.exe main.py
"""

bat_file_path = os.path.join(project_path, "run_logger.bat")

try:
    with open(bat_file_path, "w") as f:
        f.write(bat_content)
    print(f"'{bat_file_path}' 파일이 성공적으로 생성되었습니다.")
    print("이제 Windows 작업 스케줄러에서 이 .bat 파일을 등록하여 컴퓨터 시작 시 자동으로 로거를 실행할 수 있습니다.")
except Exception as e:
    print(f"파일 생성 중 오류가 발생했습니다: {e}")
