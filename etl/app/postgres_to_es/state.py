import json
import os.path
from typing import Any


class StateService:
    def __init__(self, file_name:str)-> None:
        self.file_name = file_name
        self.params = {}
        self.retrieve_state()

    def retrieve_state(self) -> None:
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as f:
                json.dump({}, f)
        with open(self.file_name, 'r') as f:
            state = json.load(f)
        self.params = state

    def save_state(self) -> None:
        with open(self.file_name, 'w') as f:
            json.dump(self.params, f)

    def get_value(self, key:str) -> None:
        return self.params.get(key, None)

    def set_value(self, key:str, value:Any) -> None:
        self.params[key] = value
        self.save_state()
