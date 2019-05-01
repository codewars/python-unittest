# Use timeit.default_timer for Python 2 compatibility.
# default_timer is time.perf_counter on 3.3+
from timeit import default_timer as perf_counter

from .test_result import CodewarsTestResult


class CodewarsTestRunner(object):
    def __init__(self):
        pass

    def run(self, test):
        r = CodewarsTestResult()
        s = perf_counter()
        print("\n<DESCRIBE::>Tests")
        try:
            test(r)
        finally:
            pass
        print("\n<COMPLETEDIN::>{:.4f}".format(1000 * (perf_counter() - s)))
        return r
