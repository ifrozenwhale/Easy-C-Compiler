import logging


class Log:
    def __init__(self, save_path):
        self.path = save_path
        file_handler = logging.FileHandler(
            self.path, 'w', 'utf8')  # or whatever
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s  %(filename)s : [%(levelname)s]  %(message)s', datefmt='%Y-%m-%d %A %H:%M:%S'))  # or whatever
        file_handler.setLevel(logging.DEBUG)
        # Define a Handler and set a format which output to console
        console = logging.StreamHandler()  # 定义console handler
        console.setLevel(logging.INFO)  # 定义该handler级别
        formatter = logging.Formatter(
            '\n%(asctime)s  %(filename)s : [%(levelname)s]  %(message)s')  # 定义该handler格式
        console.setFormatter(formatter)
        # Create an instance
        logging.getLogger().addHandler(console)  # 实例化添加handler
        logging.getLogger().addHandler(file_handler)  # 实例化添加handler

    def error(self, info):
        logging.error(info)

    def waring(self, info):
        logging.warning(info)

    def info(self, info):
        logging.info(info)

    def debug(self, info):
        logging.info(info)


if __name__ == '__main__':
    log = Log("./test_log.txt")
