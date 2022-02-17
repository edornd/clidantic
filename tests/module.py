from functools import partial


class TestClass:
    def __init__(self, arg: int) -> None:
        self.arg = arg


partial_class = partial(TestClass, arg=1)
test_instance = TestClass(arg=1)
