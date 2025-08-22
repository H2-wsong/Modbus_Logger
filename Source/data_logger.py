import os
import csv
import time
import logging
import glob
import zipfile
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date, timedelta
from pymodbus.client import ModbusTcpClient
import schedule

class ModbusDataLogger:
    def __init__(self, config):
        self.config = config
        self.log_path = self.config["log_path"]
        os.makedirs(self.log_path, exist_ok=True)

        self.current_date = date.today()
        self.current_time = datetime.now()

        self.file_handlers = {}
        self.file_handler_lock = threading.Lock()

        max_threads = self.config.get("max_concurrent_threads", 10)
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        logging.info(f"최대 동시 작업 스레드를 {max_threads}개로 설정합니다.")
        
    def _get_log_filenames(self, ip_address, log_date):
        date_str = log_date.strftime("%Y%m%d")
        safe_ip = ip_address.replace('.', '_')
        ip_log_path = os.path.join(self.log_path, safe_ip)
        os.makedirs(ip_log_path, exist_ok=True)

        base_filename = f"{date_str}"

        input_file = os.path.join(ip_log_path, f"{base_filename}_Input.csv")
        holding_file = os.path.join(ip_log_path, f"{base_filename}_Holding.csv")
        
        return input_file, holding_file

    def _prepare_log_file(self, file_path, start_address, count):
        is_new_file = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
        handler = open(file_path, 'a', newline='', encoding='utf-8-sig')
        writer = csv.writer(handler)
        if is_new_file:
            header = ["Timestamp"] + [f"주소 {start_address + i}" for i in range(count)]
            writer.writerow(header)
            handler.flush()
        return handler, writer

    def _get_or_create_file_handlers(self, ip_address):
        with self.file_handler_lock:
            if ip_address not in self.file_handlers:
                input_file, holding_file = self._get_log_filenames(ip_address, self.current_date)
                in_reg, hold_reg = self.config["input_register"], self.config["holding_register"]
                in_handler, in_writer = self._prepare_log_file(input_file, in_reg["start_address"], in_reg["count"])
                hold_handler, hold_writer = self._prepare_log_file(holding_file, hold_reg["start_address"], hold_reg["count"])
                self.file_handlers[ip_address] = {"input": (in_handler, in_writer), "holding": (hold_handler, hold_writer)}
                logging.info(f"[{ip_address}] {self.current_date.strftime('%Y-%m-%d')} 날짜의 로깅 시작 {self.current_time.strftime('%H 시 %M 분 %S 초')} 완료.")
        return self.file_handlers[ip_address]

    def _log_single_ip(self, ip, timestamp):
        client = None
        try:
            client = ModbusTcpClient(ip, port=self.config["port"], timeout=3)
            
            if not client.connect():
                logging.warning(f"[{ip}] Modbus 서버에 연결할 수 없습니다. (로그 파일 생성 안 함)")
                return

            handlers = self._get_or_create_file_handlers(ip)

            in_reg_info = self.config["input_register"]
            hold_reg_info = self.config["holding_register"]

            rr_in = client.read_input_registers(
                address=in_reg_info["start_address"], 
                count=in_reg_info["count"]
            )
            if not rr_in.isError():
                handlers["input"][1].writerow([timestamp] + rr_in.registers)
                handlers["input"][0].flush()
            else:
                logging.warning(f"[{ip}] Input Register 읽기 실패: {rr_in}")

            rr_hold = client.read_holding_registers(
                address=hold_reg_info["start_address"], 
                count=hold_reg_info["count"]
            )
            if not rr_hold.isError():
                handlers["holding"][1].writerow([timestamp] + rr_hold.registers)
                handlers["holding"][0].flush()
            else:
                logging.warning(f"[{ip}] Holding Register 읽기 실패: {rr_hold}")

        except Exception as e:
            logging.error(f"[{ip}] 로깅 작업 중 예기치 않은 오류 발생: {e}")
        finally:
            if client:
                client.close()

    def log_data_task(self):
        if date.today() != self.current_date:
            logging.info("날짜가 변경되었습니다. 일일 압축 작업을 시작합니다.")
            self.daily_maintenance()
            self.current_date = date.today()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        for ip in self.config["ip_addresses"]:
            self.executor.submit(self._log_single_ip, ip, timestamp)

    def close_all_files(self):
        if not self.file_handlers: return
        logging.info("현재 열려있는 모든 로그 파일을 닫습니다.")
        with self.file_handler_lock:
            for _, handlers in self.file_handlers.items():
                if handlers.get("input"): handlers["input"][0].close()
                if handlers.get("holding"): handlers["holding"][0].close()
            self.file_handlers.clear()

    def daily_maintenance(self):
        self.close_all_files()
        yesterday = date.today() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y%m%d")
        
        for ip_address in self.config["ip_addresses"]:
            safe_ip = ip_address.replace('.', '_')
            ip_log_path = os.path.join(self.log_path, safe_ip)
            log_files_to_zip = glob.glob(os.path.join(ip_log_path, f"{yesterday_str}_*.csv"))

            if log_files_to_zip:
                zip_filename = os.path.join(self.log_path, f"{yesterday_str}_{safe_ip}_logs.zip")
                logging.info(f"'{os.path.basename(zip_filename)}' 파일로 압축을 시작합니다.")
                try:
                    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for file in log_files_to_zip: zf.write(file, os.path.basename(file))
                    for file in log_files_to_zip: os.remove(file)
                    logging.info(f"압축 완료 후 원본 CSV 파일들을 [{safe_ip}]에서 삭제했습니다.")
                except Exception as e:
                    logging.error(f"파일 압축 또는 삭제 중 오류 발생: {e}")
        self.cleanup_old_files()

    def cleanup_old_files(self):
        max_zips = self.config.get("max_zip_archives", 365)
        zip_files = glob.glob(os.path.join(self.log_path, "*.zip"))
        if len(zip_files) > max_zips:
            zip_files.sort(key=os.path.getmtime)
            num_to_delete = len(zip_files) - max_zips
            logging.info(f"최대 압축 파일 개수({max_zips}개)를 초과하여 가장 오래된 압축 파일 {num_to_delete}개를 삭제합니다.")
            for i in range(num_to_delete):
                try:
                    file_to_delete = zip_files[i]
                    logging.info(f"삭제 대상: {os.path.basename(file_to_delete)}")
                    os.remove(file_to_delete)
                except Exception as e:
                    logging.error(f"'{file_to_delete}' 파일 삭제 중 오류 발생: {e}")

    def start(self):
        logging.info("=" * 50)
        logging.info("Modbus 데이터 로거를 시작합니다. (모드: 스레드 풀 동시 처리)")
        logging.info(f"로깅 주기: {self.config['log_interval_seconds']}초")
        logging.info(f"저장 경로: {os.path.abspath(self.log_path)}")
        logging.info("=" * 50)
        self.cleanup_old_files()
        schedule.every(self.config["log_interval_seconds"]).seconds.do(self.log_data_task)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        finally:
            logging.info("스레드 풀의 모든 작업이 완료되기를 기다리는 중...")
            self.executor.shutdown(wait=True)

            self.close_all_files()
            logging.info("로거를 안전하게 종료합니다.")