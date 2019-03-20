from loguru import logger


# InterceptHandler for built-in logging
# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         logger_opt = logger.opt(depth=6, exception=record.exc_info)
#         logger_opt.log(record.levelno, record.getMessage())

# self-rule format
class Formatter:
    def __init__(self):
        self.padding = 0

    def format(self, record):
        prefix = "{name}:{function}:{line}".format(**record)
        self.padding = max(self.padding, len(prefix))
        prefix = "{0: <{1}}".format(prefix, self.padding)
        fmt = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | " + prefix + " | {message}\n{exception}"
        return fmt


log = logger


def init():
    # remove built-in logging output
    # logging.getLogger().addHandler(InterceptHandler())

    # Remove a previously added handler and stop sending logs to its sink
    logger.remove()

    formatter = Formatter()
    #
    info_path = './flask_api_project/logger/info_logs/info.log'
    log.add(info_path, format=formatter.format, rotation="64 MB",
            backtrace=False)

    err_path = './flask_api_project/logger/error_logs/error.log'
    log.add(err_path, format=formatter.format, rotation="64 MB",
            filter=lambda record: record["level"].no >= 40, backtrace=False)

    log.info('log module loaded')
