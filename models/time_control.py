from typing import Union


class TimeControl:
    def __init__(self, time_control_header):
        self._base_time_control = time_control_header
        if "+" in time_control_header.strip():
            self.base = int(time_control_header.split("+")[0])
            self.increment = int(time_control_header.split("+")[1])
        elif time_control_header.strip() == "-":  # Correspondence
            self.base = float('inf')
            self.increment = None

    def in_between(self, min_time: int, min_increment: int, max_time: Union[int, float], max_increment: Union[int, float]):
        return min_time <= self.base <= max_time and (
            min_increment <= self.increment <= max_increment if self.increment is not None else True
        )

    def __repr__(self):
        if self._base_time_control == "-":
            return "Correspondence"
        if self.base % 60 == 0:
            base = self.base // 60
        else:
            base = self.base / 60
        return f"{base}+{self.increment}"

    def __eq__(self, other):
        return self._base_time_control == other._base_time_control

    def __hash__(self):
        return hash(repr(self))
