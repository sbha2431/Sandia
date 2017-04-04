from enum import Enum

class Visgame(object):
    
    __slots__ = ["_state", "_table"]
    
    def __init__(self):
        self._state = 0
    
    _table = [
        {   0: (1, 0),
            2: (2, 0),
            1: (3, 0),
            3: (4, 0),
        },
        {   0: (1, 0),
            2: (2, 0),
            1: (3, 0),
            3: (4, 0),
        },
        {
        },
        {   0: (1, 0),
            2: (2, 0),
            1: (3, 0),
            3: (4, 0),
        },
        {   0: (1, 0),
            2: (2, 0),
            1: (3, 0),
            3: (4, 0),
        },
        ]
    
    def move(self, y):
        try:
            table = self._table[self._state]
            newState,res = table[y]
            self._state = newState
            return res
        
        except IndexError:
            raise Exception("Unrecognized internal state: " + str(self._state))
        
        except Exception:
            self._error(y)
    
    def _error(self, y):
        raise ValueError("Unrecognized input: " + (
            "y = {y}; ").format( y=y))