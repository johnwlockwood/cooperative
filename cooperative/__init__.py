# _*_ coding: utf-8 _*_
# -*- test-case-name: cooperative.tests.test_cooperative -*-
from collections import deque

from cooperative import _meta

__version__ = _meta.version
__version_info__ = _meta.version_info


from twisted.internet.task import cooperate

from stream_tap import stream_tap
from iter_karld_tools import i_batch


class ValueBucket(object):
    """
    Produces a callable that accumulates all non-None values
    it is called with in order.

    The contents may be accessed or collected and drained,
    to make room for new content.
    """
    def __init__(self):
        self._contents = deque()

    def __call__(self, value):
        if value is not None:
            self._contents.append(value)

    def contents(self):
        """
        :returns: contents
        """
        return self._contents

    def drain_contents(self):
        """
        Starts a new collection to accumulate future contents
        and returns all of existing contents.
        """
        existing_contents = self._contents
        self._contents = deque()
        return existing_contents


def accumulation_handler(stopped_generator, spigot):
    """
    Drain the contents of the bucket from the spigot.

    :param stopped_generator: Generator which as stopped
    :param spigot: a Bucket.
    :return: The contents of the bucket.
    """
    return spigot.drain_contents()


def accumulate(a_generator, cooperator=None):
    """
    Start a Deferred whose callBack arg is a deque of the accumulation
    of the values yielded from a_generator.

    :param a_generator: An iterator which yields some not None values.
    :return: A Deferred to which the next callback will be called with
     the yielded contents of the generator function.
    """
    if cooperator:
        own_cooperate = cooperator.cooperate
    else:
        own_cooperate = cooperate

    spigot = ValueBucket()
    items = stream_tap((spigot,), a_generator)
    d = own_cooperate(items).whenDone()
    d.addCallback(accumulation_handler, spigot)
    return d


def batch_accumulate(max_batch_size, a_generator, cooperator=None):
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
    if cooperator:
        own_cooperate = cooperator.cooperate
    else:
        own_cooperate = cooperate

    spigot = ValueBucket()
    items = stream_tap((spigot,), a_generator)

    d = own_cooperate(i_batch(max_batch_size, items)).whenDone()
    d.addCallback(accumulation_handler, spigot)
    return d
