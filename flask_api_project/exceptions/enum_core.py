from enum import Enum


class BaseEnum(Enum):

    def get_code(self):
        """
        return code
        """
        return list(self.value.keys())[0]

    def get_msg(self):
        """
        return msg
        """
        return list(self.value.values())[0]
