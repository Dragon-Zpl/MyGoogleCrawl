import logging.handlers
def test(data):
    logger = logging.getLogger('project')  # 不加名称设置root logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(lineno)s %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    # 使用FileHandler输出到文件
    fh = logging.handlers.TimedRotatingFileHandler('log.txt', when='D', interval=1)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    # 使用StreamHandler输出到屏幕
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    # 添加两个Handler
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger.info(data)


printf = test

try:
    sfasa

except Exception as e:
    printf(str(e))