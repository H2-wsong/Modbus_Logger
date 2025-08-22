import logging
from Source.config import CONFIG
from Source.data_logger import ModbusDataLogger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    
    logger = ModbusDataLogger(CONFIG)
    
    try:
        logger.start()
    except KeyboardInterrupt:
        logging.info("사용자의 요청으로 프로그램을 중단합니다.")
    except Exception as e:
        logging.critical(f"치명적인 오류로 인해 프로그램을 종료합니다: {e}")