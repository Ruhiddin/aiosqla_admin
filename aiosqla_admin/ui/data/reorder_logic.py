from typing import Dict, Literal, Optional


class ReorderLogic:
    def __init__(
        self,
        move_id_first: bool = True,
        move_timestamps_last: bool = True,
        alphabetical: Optional[Literal["asc", "desc"]] = None,
        timestamps: tuple = ("updated_at", "created_at"),
    ):
        self.move_id_first = move_id_first
        self.move_timestamps_last = move_timestamps_last
        self.alphabetical = alphabetical
        self.timestamps = timestamps

    def apply(self, data: Dict) -> Dict:
        """
        Reorders the data dictionary based on the rules:
        - Moves 'id' first
        - Sorts fields alphabetically if enabled otherwise leaves as default as order of fields defined in sqla Model (optional)
        - Moves timestamps last
        """
        working = dict(data)

        id_value = working.pop("id", None) if self.move_id_first else None
        timestamp_values = {
            key: working.pop(key) for key in self.timestamps if key in working
        } if self.move_timestamps_last else {}

        # Sort the middle section alphabetically
        if self.alphabetical is not None:
            if self.alphabetical:
                reverse = self.alphabetical == "desc"
                middle_keys = sorted(working.keys(), reverse=reverse)
            else:
                middle_keys = list(working.keys())

        reordered = {}

        if self.move_id_first and id_value is not None:
            reordered["id"] = id_value

        for key in middle_keys:
            reordered[key] = working[key]

        if self.move_timestamps_last:
            for key in self.timestamps:
                if key in timestamp_values:
                    reordered[key] = timestamp_values[key]

        return reordered
