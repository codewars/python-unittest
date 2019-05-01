import unittest
import traceback

# Use timeit.default_timer for Python 2 compatibility.
# default_timer is time.perf_counter on 3.3+
from timeit import default_timer as perf_counter

__unittest = True


class CodewarsTestResult(unittest.TestResult):
    def __init__(self):
        # Note that we need to avoid super() and use
        # super(CodewarsTestResult, self) for Python 2 compatibility
        super(CodewarsTestResult, self).__init__()
        self.start = 0.0

    def startTest(self, test):
        desc = test.shortDescription()
        if desc is None:
            desc = test._testMethodName
        print("\n<IT::>" + desc)
        super(CodewarsTestResult, self).startTest(test)
        self.start = perf_counter()

    def stopTest(self, test):
        print("\n<COMPLETEDIN::>{:.4f}".format(1000 * (perf_counter() - self.start)))
        super(CodewarsTestResult, self).stopTest(test)

    def addSuccess(self, test):
        print("\n<PASSED::>Test Passed")
        super(CodewarsTestResult, self).addSuccess(test)

    def addError(self, test, err):
        print("\n<ERROR::>Unhandled Exception")
        print(
            "\n<LOG:ESC:Error>"
            + esc("".join(traceback.format_exception_only(err[0], err[1])))
        )
        print("\n<LOG:ESC:Traceback>" + esc(self._exc_info_to_string(err, test)))
        super(CodewarsTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        print("\n<FAILED::>Test Failed")
        print(
            "\n<LOG:ESC:Failure>"
            + esc("".join(traceback.format_exception_only(err[0], err[1])))
        )
        super(CodewarsTestResult, self).addFailure(test, err)

    # from unittest/result.py
    def _exc_info_to_string(self, err, test):
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        if exctype is test.failureException:
            length = self._count_relevant_tb_levels(
                tb
            )  # Skip assert*() traceback levels
        else:
            length = None
        return "".join(traceback.format_tb(tb, limit=length))

    def _is_relevant_tb_level(self, tb):
        return "__unittest" in tb.tb_frame.f_globals

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length


def esc(s):
    return s.replace("\n", "<:LF:>")
