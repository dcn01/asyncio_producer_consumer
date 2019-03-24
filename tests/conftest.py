from queue import Queue
import pytest


@pytest.fixture()
def event_loop_with_handler_async_exception_to_pyfail(event_loop):
    def handle_async_exception(_, ctx):
        pytest.fail(f"Exception in async task: {ctx['exception']}")

    event_loop.set_exception_handler(handle_async_exception)

    return event_loop


@pytest.fixture()
def event_loop_with_handler_async_exception_to_queue(event_loop):
    # Thread-safe queue
    queue_exceptions = Queue()

    def handle_async_exception(_, ctx):
        queue_exceptions.put(ctx['exception'])

    event_loop.set_exception_handler(handle_async_exception)

    return event_loop, queue_exceptions
