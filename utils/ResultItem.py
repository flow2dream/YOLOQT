from logging import getLogger

logger = getLogger(__name__)

class ResultItem:

    file_name:str = None
    item_num: int = None
    bow_head:int = None
    turn_head:int = None
    discuss:int = None
    talk:int = None
    hand_raise:int = None
    write:int = None
    use_phone:int = None
    read:int = None
    lean_table:int = None
    stand:int = None


    def __init__(self, cls_dict:dict) -> None:
        self.set_result(cls_dict)
    
    def set_result(self, result:dict) -> None:
        path = result.get('path')
        self.item_num = result.get('item_num', 0)
        result = result.get('result')
        if not result:
            return
        self.file_name = path
        self.bow_head = result.get('bow head', 0)
        self.turn_head = result.get('turn head', 0)
        self.discuss = result.get('discuss', 0)
        self.talk = result.get('talk', 0)
        self.hand_raise = result.get('hand-raise', 0)
        self.write = result.get('write', 0)
        self.use_phone = result.get('use phone', 0)
        self.read = result.get('read', 0)
        self.lean_table = result.get('lean table', 0)
        self.stand = result.get('stand', 0)
        


    def get_result(self) -> dict:
        return {
            "file_name": self.file_name,
            "item_num": self.item_num,
            "result": {
                "bow head": self.bow_head,
                "turn head": self.turn_head,
                "discuss": self.discuss,
                "talk": self.talk,
                "hand-raise": self.hand_raise,
                "write": self.write,
                "use phone": self.use_phone,
                "read": self.read,
                "lean table": self.lean_table,
                "stand": self.stand
            }
        }