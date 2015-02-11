#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from operator import add

import sys
from twisted.internet import defer
from twisted.internet.task import react
from twisted.python import log


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


def main(reactor):

    d5 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.3, d5.callback, "########## simulated request 1 ############")

    d6 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.5, d6.callback, "########## sim request 2 ############")

    d7 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.7, d7.callback, "########## simulated request 3 ############")

    numbers = [54.0, 42, 10, 34]
    for number in numbers:
        result = list(expensive(number))
        log.msg("first for {}: {}".format(number, reduce(add, result, 0)))
        result = list(expensive(number))
        log.msg("second for {}: {}".format(number, reduce(add, result, 0)))

    return defer.gatherResults([d5, d6, d7])

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    react(main, [])
