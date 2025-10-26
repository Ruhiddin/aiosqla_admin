class BaseDialog:
    def bind(self, dash: "Dashboard"): # type: ignore  # noqa: F821
        self.dash = dash