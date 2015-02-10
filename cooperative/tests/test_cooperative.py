# _*_ coding: utf-8 _*_
from collections import deque
from itertools import chain

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks
from twisted.python import log
from twisted.trial import unittest

from karld.tap import Bucket

from cooperative import accumulation_handler
from cooperative import accumulate
from cooperative import batch_accumulate


class TestHandler(unittest.TestCase):
    def test_accumulation_handler(self):
        """
        Ensure the return value of accumulation_handler
        is the contents of a Bucket instance with it's contents
        drained.

        :return:
        """
        spigot = Bucket(unicode)
        spigot(1)
        spigot(2)

        result = accumulation_handler(None, spigot)
        self.assertEqual(result, deque([u"1", u"2"]))
        self.assertEqual(spigot.contents(), deque([]))


def i_get_tenth_11(value):
    """
    Yield the tenth and eleventh item of value.

    :param value:
    :return:
    """
    yield value[10]
    yield value[11]


@inlineCallbacks
def run_some_with_error(value):
    """
    Cooperatively iterator over two iterators consecutively, but
     the second one will always raise an IndexError, which is caught,
     logged and a message is returned.

    :return:
    """
    #  first deferred
    result = yield accumulate(i_get_tenth_11(value))

    try:
        result2 = yield accumulate(i_get_tenth_11(result))
        defer.returnValue(result2)
    except IndexError, e:
        log.err(e)
        defer.returnValue("Couldn't get second result, "
                          "but the first result is {}".format(result))


@inlineCallbacks
def run_some_without_error(value):
    """
    Cooperatively iterator over two iterators consecutively and the
    result of the final one is returned.

    :param value: Any sequence.
    :return:
    """
    #  first deferred
    result = yield accumulate(i_get_tenth_11(range(110, 150)))

    log.msg("accumulated {}".format(result))
    result = yield accumulate(i_get_tenth_11(value))
    defer.returnValue(result)


class TestAccumulate(unittest.TestCase):
    @inlineCallbacks
    def test_accumulate(self):
        """
        Ensure that within an inline callback function,
        a accumulate wrapped generator
        yields the result of the output of the generator.

        :return:
        """
        result = yield accumulate(i_get_tenth_11(range(110, 150)))
        self.assertEqual(result, deque([120, 121]))


    @inlineCallbacks
    def test_failure(self):
        """
        Ensure that within an inline callback function,
        a accumulate based function
        yields the result if it's cooperative generator.

        Since and_the_winner_is is designed to always
        log and error, Ensure one IndexError is logged.

        :return:
        """
        result = yield run_some_with_error(range(15))
        self.assertEqual(result, "Couldn't get second result, "
                                 "but the first result is deque([10, 11])")

        # failure expected
        index_errors = self.flushLoggedErrors(IndexError)
        self.assertEqual(len(index_errors), 1)

    @inlineCallbacks
    def test_multi_winner(self):
        """
        Ensure multiple inline callback functions will run cooperatively.

        :return:
        """
        d1 = run_some_without_error(range(15))
        d2 = run_some_without_error(range(15, 100))
        result = yield defer.gatherResults([d1, d2])

        self.assertEqual(result, [deque([10, 11]), deque([25, 26])])

    @inlineCallbacks
    def test_trice_winner(self):
        """
        Ensure multiple inline callback functions will run cooperatively.

        :return:
        """
        d1 = run_some_without_error(range(15))
        d2 = run_some_without_error(range(15, 100))
        d3 = accumulate(i_get_tenth_11(range(4, 50)))
        result = yield defer.gatherResults([d1, d2, d3])

        self.assertEqual(result, [deque([10, 11]),
                                  deque([25, 26]),
                                  deque([14, 15])])

    @inlineCallbacks
    def test_multi_winner_chain(self):
        """
        Ensure multiple inline callback functions will run cooperatively.

        Ensure the result of gatherResults can be chained together
        in order.

        :return:
        """
        called = []

        def watcher(value):
            """
            A pass through generator for i_get_tenth_11 that
            captures the value in a list, which can show the
            order of the generator iteration.

            :param value:
            :return:
            """
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item

        result = yield defer.gatherResults([
            accumulate(watcher(range(0, 15))),
            accumulate(watcher(range(15, 100))),
            accumulate(watcher(range(98, 200))),
            accumulate(watcher(range(145, 189)))
        ])

        final_result = list(chain.from_iterable(result))

        self.assertEqual(final_result, [10, 11, 25, 26, 108, 109, 155, 156])
        self.assertEqual(set(called), set(final_result))
        self.assertNotEqual(called, final_result)
        #  The iteration is shown to alternate between generators passed
        #   to cooperate.
        self.assertEqual(called, [10, 25, 108, 155, 11, 26, 109, 156])

    @inlineCallbacks
    def test_multi_deux_chain(self):
        """
        Ensure multiple inline callback functions will run cooperatively.

        Ensure the result of gatherResults can be chained together
        in order.

        Ensure cooperatively run generators will complete
        no matter the length.

        Ensure the longest one will continue to iterate after the
        others run out of iterations.

        :return:
        """
        called = []

        def watcher(value):
            """
            A pass through generator for i_get_tenth_11 that
            captures the value in a list, which can show the
            order of the generator iteration.

            :param value:
            :return:
            """
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item

        def deux_watcher(value):
            """
            A pass through generator for i_get_tenth_11 that
            captures the value in a list, which can show the
            order of the generator iteration.

            :param value:
            :return:
            """
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item

        result = yield defer.gatherResults([
            accumulate(watcher(range(0, 15))),
            accumulate(watcher(range(15, 100))),
            accumulate(deux_watcher(range(1098, 10200))),
            accumulate(watcher(range(145, 189)))
        ])

        final_result = list(chain.from_iterable(result))

        self.assertEqual(final_result,
                         [10, 11, 25, 26, 1108, 1109, 1108, 1109, 155, 156])
        self.assertEqual(set(called), set(final_result))
        self.assertNotEqual(called, final_result)
        #  The iteration is shown to alternate between generators passed
        #   to cooperate.
        self.assertEqual(called,
                         [10, 25, 1108, 155, 11, 26, 1109, 156, 1108, 1109])

    @inlineCallbacks
    def test_multi_deux_batched(self):
        """
        Ensure multiple inline callback functions will run cooperatively.

        Ensure the result of gatherResults can be chained together
        in order.

        Ensure cooperatively run generators will complete
        no matter the length.

        Ensure the longest one will continue to iterate after the
        others run out of iterations.

        Ensure those called with batch_accumulate will
        iterate over the generator in batches the size of max_size.

        :return:
        """
        called = []

        def watcher(value):
            """
            A pass through generator for i_get_tenth_11 that
            captures the value in a list, which can show the
            order of the generator iteration.

            :param value:
            :return:
            """
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item

        def deux_watcher(value):
            """
            A pass through generator for i_get_tenth_11 that
            captures the value in a list, which can show the
            order of the generator iteration.

            :param value:
            :return:
            """
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item
            for item in i_get_tenth_11(value):
                called.append(item)
                yield item

        result = yield defer.gatherResults([
            accumulate(watcher(range(0, 15))),
            accumulate(watcher(range(15, 100))),
            batch_accumulate(3, deux_watcher(range(1098, 10200))),
            accumulate(watcher(range(145, 189)))
        ])

        final_result = list(chain.from_iterable(result))

        self.assertEqual(final_result,
                         [10, 11, 25, 26, 1108, 1109, 1108, 1109, 155, 156])
        self.assertEqual(set(called), set(final_result))
        self.assertNotEqual(called, final_result)
        #  The iteration is shown to alternate between generators passed
        #   to cooperate, except the batched one does three at a time
        #   when it is it's turn.
        self.assertEqual(called,
                         [10, 25, 1108, 1109, 1108, 155, 11, 26, 1109, 156])
