"""
https://asyncio.readthedocs.io/en/latest/producer_consumer.html
"""
import asyncio
from asyncio import wait_for, QueueEmpty
from itertools import tee
import pytest

from yoyonel.async_producer_consumer.async_producer_consumer import (
    ASyncProducerConsumer, do_shutdown, generic_consumer
)

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_async_producer_consumer(
        event_loop_with_handler_async_exception_to_pyfail
):
    event_loop = event_loop_with_handler_async_exception_to_pyfail

    raw_inputs_for_processing, raw_inputs_for_tests = tee(map(str, range(100)))

    producers_consumers = ASyncProducerConsumer()

    queue_strings = asyncio.Queue()
    queue_integers = asyncio.Queue()
    queue_results = asyncio.Queue()

    async def _consume_string_and_cast_to_int():
        await generic_consumer(queue_strings, queue_integers,
                               lambda i: (i, int(i)))

    async def _consume_ints_and_multiply_by_2():
        def func_apply_on_item(i):
            return i[0], i[1] * 2

        await generic_consumer(queue_integers, queue_results,
                               func_apply_on_item)

    producers_consumers.add('convert_to_int',
                            queue_strings, _consume_string_and_cast_to_int)
    producers_consumers.add('multiply_by_2',
                            queue_integers, _consume_ints_and_multiply_by_2)

    async def _produce_strings():
        for string in raw_inputs_for_processing:
            await queue_strings.put(string)

    # create a future on task that ending "quickly"
    future_task = event_loop.create_task(_produce_strings())

    # wait until the consumer has processed all items
    await producers_consumers.join()

    inputs_from_processing = []

    while future_task.done() is False or not queue_results.empty():
        raw_input, input_processed = await wait_for(queue_results.get(),
                                                    timeout=1.0)
        inputs_from_processing.append(raw_input)
        assert (int(raw_input) * 2) == input_processed

    #
    await do_shutdown(loop=event_loop)
    #
    assert sorted(inputs_from_processing) == sorted(raw_inputs_for_tests)


async def test_async_producer_consumer_exception(
        event_loop_with_handler_async_exception_to_queue
):
    (event_loop,
     queue_exceptions) = event_loop_with_handler_async_exception_to_queue

    raw_inputs_for_processing, raw_inputs_for_tests = tee(map(str, range(100)))

    producers_consumers = ASyncProducerConsumer()

    queue_strings = asyncio.Queue()
    queue_integers = asyncio.Queue()
    queue_results = asyncio.Queue()

    async def _consume_string_and_cast_to_int():
        def func_apply_on_item(i):
            return i, int(i)

        await generic_consumer(queue_strings, queue_integers,
                               func_apply_on_item)

    async def _consume_ints_and_multiply_by_2():
        def func_apply_on_item(_):
            # here: raise exception: DivisionByZero at runtime (in consumer)
            raise ZeroDivisionError

        await generic_consumer(queue_integers, queue_results,
                               func_apply_on_item)

    producers_consumers.add('convert_to_int',
                            queue_strings, _consume_string_and_cast_to_int)
    producers_consumers.add('multiply_by_2',
                            queue_integers, _consume_ints_and_multiply_by_2)

    async def _produce_strings():
        for string in raw_inputs_for_processing:
            await queue_strings.put(string)

    # create a future on task that ending "quickly"
    future_task = event_loop.create_task(_produce_strings())

    # wait until the consumer has processed all items
    await producers_consumers.join()

    inputs_from_processing = []

    with pytest.raises(ZeroDivisionError):
        while future_task.done() is False or not queue_results.empty():
            try:
                raw_input, input_processed = await wait_for(
                    queue_results.get(), timeout=0.01)
            except asyncio.TimeoutError:
                try:
                    exception = queue_exceptions.get()
                    raise exception
                except QueueEmpty:
                    continue

            inputs_from_processing.append(raw_input)
            assert (int(raw_input) * 2) == input_processed

    #
    await do_shutdown(loop=event_loop)
