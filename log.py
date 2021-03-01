class Log:
    @staticmethod
    def log_error(err):
        print('[ERROR]', err)

    @staticmethod
    def log_warning(warning):
        print('[WARNING]', warning)

    @staticmethod
    def log_info(info):
        print('[INFO]', info)