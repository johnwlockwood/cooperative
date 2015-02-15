# _*_ coding: utf-8 _*_
# -*- test-case-name: cooperative.tests.test_cooperative -*-

from cooperative import _meta

__version__ = _meta.version
__version_info__ = _meta.version_info


from twisted.internet.task import cooperate

from stream_tap import Bucket
from stream_tap import stream_tap
from iter_karld_tools import i_batch


def accumulation_handler(stopped_generator, spigot):
    """
    Drain the contents of the bucket from the spigot.

    :param stopped_generator: Generator which as stopped
    :param spigot: a Bucket.
    :return: The contents of the bucket.
    """
    return spigot.drain_contents()


def accumulate(a_generator):
    """
    Start a Deferred whose callBack arg is a deque of the accumulation
    of the values yielded from a_generator.

    :param a_generator: An iterator which yields some not None values.
    :return: A Deferred to which the next callback will be called with
     the yielded contents of the generator function.
    """

    spigot = Bucket(lambda x: x)
    items = stream_tap((spigot,), a_generator)
    d = cooperate(items).whenDone()
    d.addCallback(accumulation_handler, spigot)
    return d


def batch_accumulate(max_batch_size, a_generator):
    """
    Start a Deferred whose callBack arg is a deque of the accumulation
    of the values yielded from a_generator which is iterated over
    in batches the size of max_batch_size.

    It should be more efficient to iterate over the generator in
     batches and still provide enough speed for non-blocking execution.

    :param max_batch_size: The number of iterations of the generator
     to consume at a time.
    :param a_generator: An iterator which yields some not None values.
    :return: A Deferred to which the next callback will be called with
     the yielded contents of the generator function.
    """
    from twisted.internet.task import cooperate
    spigot = Bucket(lambda x: x)
    items = stream_tap((spigot,), a_generator)

    d = cooperate(i_batch(max_batch_size, items)).whenDone()
    d.addCallback(accumulation_handler, spigot)
    return d
