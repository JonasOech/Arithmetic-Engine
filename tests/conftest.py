import pytest
from parser import Parser


@pytest.fixture
def parser():
    return Parser()
