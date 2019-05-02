from __future__ import absolute_import
from django.test.runner import DiscoverRunner
from .test_runner import CodewarsTestRunner


class CodewarsDjangoRunner(DiscoverRunner):
    def run_suite(self, suite, **kwargs):
        return CodewarsTestRunner().run(suite)
