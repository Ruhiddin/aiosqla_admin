from .reorder_logic import ReorderLogic


class UIModelExtractor:
    def __init__(self, instance, only_field: str = None):
        self.instance = instance
        self.only_field = only_field
        self.reorder_logic = ReorderLogic(
            move_id_first=True, 
            move_timestamps_last=True, 
            alphabetical=None, 
            timestamps=('created_at', 'updated_at')
        )

    async def extract(self) -> dict:
        raise NotImplementedError
