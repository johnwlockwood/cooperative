# _*_ coding: utf-8 _*_
# -*- test-case-name: cooperative.tests.test_cooperative -*-

import sys
from cooperative import _meta

__version__ = _meta.version
__version_info__ = _meta.version_info


from twisted.internet.task import cooperate

from karld.tap import Bucket
from karld.tap import stream_tap
from karld.iter_utils import i_batch


def cooperative_accumulation_handler(stopped_generator, spigot):
    """
    Drain the contents of the bucket from the spigot.

    :param stopped_generator: Generator which as stopped
    :param spigot: a Bucket.
    :return: The contents of the bucket.
    """
    return spigot.drain_contents()


def cooperative_accumulate(a_generator_func):
    """
    Start a Deferred whose callBack arg is a deque of the accumulation
    of the values yielded from a_generator_func.

    :param a_generator_func: A function which returns a generator.
    :return: A Deferred to which the next callback will be called with
     the yielded contents of the generator function.
    """

    spigot = Bucket(lambda x: x)
    items = stream_tap((spigot,), a_generator_func())
    d = cooperate(items).whenDone()
    d.addCallback(cooperative_accumulation_handler, spigot)
    return d


def cooperative_accumulate_batched(max_batch_size, a_generator_func):
    """
    Start a Deferred whose callBack arg is a deque of the accumulation
    of the values yielded from a_generator_func which is iterated over
    in batches the size of max_batch_size.

    It should be more efficient to iterate over the generator in
     batches and still provide enough speed for non-blocking execution.

    :param max_batch_size: The number of iterations of the generator
     to consume at a time.
    :param a_generator_func: A function which returns a generator.
    :return: A Deferred to which the next callback will be called with
     the yielded contents of the generator function.
    """
    from twisted.internet.task import cooperate
    spigot = Bucket(lambda x: x)
    items = stream_tap((spigot,), a_generator_func())

    d = cooperate(i_batch(max_batch_size, items)).whenDone()
    d.addCallback(cooperative_accumulation_handler, spigot)
    return d
