#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from operator import add

import sys
from twisted.internet import defer
from twisted.internet.task import react
from twisted.python import log

from cooperative import batch_accumulate


def expensive(number):
    log.msg("starting {}".format(number))
    for value in range(100000):
        if 25000 == value:
            log.msg("1/4 for {}".format(number))
        if 50000 == value:
            log.msg("1/2 for {}".format(number))
        if 75000 == value:
            log.msg("3/4 for {}".format(number))
        yield number * value / 3.0


def expensive2(number):
    log.msg("starting {}".format(number))
    total = 0
    for value in range(100000):
        if 25000 == value:
            log.msg("1/4 for {}".format(number))
        if 50000 == value:
            log.msg("1/2 for {}".format(number))
        if 75000 == value:
            log.msg("3/4 for {}".format(number))
        total += number * value / 3.0
        yield
    yield total


@defer.inlineCallbacks
def do_some_expensive_things(number):
    """

    :param number:
    :return:
    """
    result = yield batch_accumulate(1000, expensive(number))
    log.msg("first for {}: {}".format(number, reduce(add, result, 0)))
    result = yield batch_accumulate(1000, expensive2(number+1))
    log.msg("second for {}: {}".format(number, reduce(add, result, 0)))


def main(reactor):
    """


    :param reactor:
    :return:
    """
    total = 0

    d1 = do_some_expensive_things(54.0)
    d2 = do_some_expensive_things(42)
    d3 = do_some_expensive_things(10)
    d4 = do_some_expensive_things(34)

    # Enqueue events to simulate
    d5 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.3, d5.callback, "########## simulated request 1 ############")

    d6 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.5, d6.callback, "########## sim request 2 ############")

    d7 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(1.0, d7.callback, "########## simulated request 3 ############")

    return defer.gatherResults([d1, d2, d3, d4, d5, d6, d7])

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    react(main, [])
