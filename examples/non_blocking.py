#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from operator import add

import add_package_path

import sys
from twisted.internet import defer
from twisted.internet.task import react
from twisted.python import log

from cooperative import batch_accumulate


def expensive(number):
    log.msg("starting {}".format(number))
    for value in range(100000):
        if 25000 == value:
            log.msg("tttttttt1/4 for {}".format(number))
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
    Perform one expensive computation cooperatively with any
     other iterator passed into twisted's cooperate, then
     use it's result to pass into the second computation.

    :param number:
    :return:
    """
    result = yield batch_accumulate(1000, expensive(number))
    total = reduce(add, result, 0)
    log.msg("first for {}: {}".format(number, total))

    result = yield batch_accumulate(1000, expensive2(int(total/1e9)))
    total = reduce(add, result, 0)
    log.msg("second for {}: {}".format(number, total))
    defer.returnValue(total)


@defer.inlineCallbacks
def do_less_expensive_things(number):
    """
    Perform one expensive computation cooperatively with any
     other iterator passed into twisted's cooperate, then
     use it's result to pass into the second computation.

    :param number:
    :return:
    """
    result = yield batch_accumulate(1000, expensive(number))
    total = reduce(add, result, 0)
    log.msg("only for {}: {}".format(number, total))
    defer.returnValue(total)


def main(reactor):
    d1 = do_some_expensive_things(54.0)
    d2 = do_some_expensive_things(42)
    d3 = do_some_expensive_things(10)
    d4 = do_some_expensive_things(34)

    # Enqueue events to simulate handling external events
    d5 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.3, d5.callback, "########## simulated request 1 ############")

    d6 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.5, d6.callback, "########## sim request 2 ############")

    d7 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(1.0, d7.callback, "########## simulated request 3 ############")

    # simulate an external event triggering an expensive computation while
    # other expensive computations are happening.
    d8 = defer.Deferred()
    d8.addCallback(do_less_expensive_things)
    reactor.callLater(0.3, d8.callback, 20001)

    return defer.gatherResults([d1, d2, d3, d4, d5, d6, d7, d8]).addCallback(log.msg)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    react(main, [])
