import pytest
import os

@pytest.fixture()
def sample_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'samples')