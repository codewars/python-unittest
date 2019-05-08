import sys
import inspect
import unittest

# Use timeit.default_timer for Python 2 compatibility.
# default_timer is time.perf_counter on 3.3+
from timeit import default_timer as perf_counter

from .test_result import CodewarsTestResult


class CodewarsTestRunner(object):
    def __init__(self, stream=None, group_by_module=False):
        if stream is None:
            stream = sys.stdout
        self.stream = _WritelnDecorator(stream)
        self.result = CodewarsTestResult(self.stream)
        self.group_by_module = group_by_module

    def run(self, test):
        if isinstance(test, unittest.TestSuite):
            self._run_each_test_cases(test)
            return self.result
        else:
            return self._run_case(test)

    def _run_each_test_cases(self, suite):
        if not isinstance(suite, unittest.TestSuite):
            return

        for test in suite:
            if _is_test_module(test):
                name = ""
                if self.group_by_module:
                    case = _get_test_case(test)
                    name = _get_module_name(case)
                    if name:
                        self.stream.writeln(_group(name))

                startTime = perf_counter()
                for cases in test:
                    self._run_cases(cases)

                if name:
                    self.stream.writeln(_completedin(startTime, perf_counter()))
            else:
                self._run_each_test_cases(test)

    def _run_cases(self, test):
        case = next(iter(test), None)
        if not case:
            return self.result

        self.stream.writeln(_group(_get_class_name(case)))
        startTime = perf_counter()
        try:
            test(self.result)
        finally:
            pass
        self.stream.writeln(_completedin(startTime, perf_counter()))
        return self.result

    def _run_case(self, test):
        try:
            test(self.result)
        finally:
            pass
        return self.result


def _group(name):
    return "\n<DESCRIBE::>{}".format(name)


def _completedin(start, end):
    return "\n<COMPLETEDIN::>{:.4f}".format(1000 * (end - start))


# True if test suite directly contains a test case
def _is_test_cases(suite):
    return isinstance(suite, unittest.TestSuite) and any(
        isinstance(t, unittest.TestCase) for t in suite
    )


# True if test suite directly contains test cases
def _is_test_module(suite):
    return isinstance(suite, unittest.TestSuite) and any(
        _is_test_cases(t) for t in suite
    )


# Get first test case from a TestSuite created from a test module to find module name
def _get_test_case(suite):
    if not isinstance(suite, unittest.TestSuite):
        return None
    for test in suite:
        if not isinstance(test, unittest.TestSuite):
            continue
        for t in test:
            if isinstance(t, unittest.TestCase):
                return t
    return None


def _get_class_name(x):
    cls = x if inspect.isclass(x) else x.__class__
    return cls.__name__


def _get_module_name(x):
    cls = x if inspect.isclass(x) else x.__class__
    mod = cls.__module__
    if mod is None or mod == str.__class__.__module__:
        return ""
    return mod


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ("stream", "__getstate__"):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write("\n")  # text-mode streams translate to \r\n if needed
