from rich.console import Console
from rich.theme import Theme

__all__ = ["console"]

custom_theme = Theme({
    "error": "bold red",
    "warn": "bold yellow",
    "info": "dim cyan",
    "success": "bold green",
    "debug": "dim magenta",
})


class RubeculaConsole(Console):
    """
    @DynamicAttrs
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw, theme=custom_theme)
        self.loglevel = 3
        # self.loglevel = 100

        for i, level in enumerate([
            'error', 'warn', 'info', 'success', 'debug'
        ]):
            self.__setattr__(level, self.__log_with_level(level, i))

    def __log_with_level(self, level, i):
        def func(*a, **kw):
            if i > self.loglevel:
                return

            self.print(*a, **kw, style=level)

        return func


console = RubeculaConsole()

# console.error("---")
# console.warn("Welcome")
# console.info("to")
# console.success("Rubecula")
# console.debug("---")
