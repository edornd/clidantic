import pytest

from clidantic.testing import CliRunner


@pytest.fixture(scope="function")
def runner(request):
    return CliRunner()
