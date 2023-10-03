import asyncio
import pytest_asyncio


# This is somehow necessary to make it possible to run all the async tests.
# From: https://stackoverflow.com/questions/66054356/multiple-async-unit-tests-fail-but-running-them-one-by-one-will-pass


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for the whole session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
