class Enum(object):
    last_id = -1

    @staticmethod
    def auto():
        Enum.last_id += 1
        return Enum.last_id
