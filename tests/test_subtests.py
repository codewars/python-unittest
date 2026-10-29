import io
import re
import unittest

from codewars_unittest import CodewarsTestRunner


class TestSubtests(unittest.TestCase):
    def run_case(self, body):
        case = type('Example', (unittest.TestCase,), {'test_example': body})
        stream = io.StringIO()
        result = CodewarsTestRunner(stream=stream).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(case))
        output = stream.getvalue()
        markers = re.findall(r'^<(PASSED|FAILED|ERROR)::>', output, re.MULTILINE)
        self.assertEqual(output.count('<IT::>'), 1)
        self.assertEqual(output.count('<COMPLETEDIN::>'), 2)
        self.assertEqual(result.testsRun, 1)
        return result, output, markers

    def test_failed_subtests_emit_failures_and_continue(self):
        def body(case):
            for number in (1, 2):
                with case.subTest(number=number):
                    case.assertEqual(number, 0)
        result, output, markers = self.run_case(body)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.failures), 2)
        self.assertEqual(markers, ['FAILED', 'FAILED'])
        self.assertIn('number=1', output)
        self.assertIn('number=2', output)
        self.assertIn('<LOG:ESC:Traceback>', output)

    def test_error_subtest_emits_error(self):
        def body(case):
            with case.subTest(name='broken'):
                raise ValueError('child error')
        result, output, markers = self.run_case(body)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(markers, ['ERROR'])
        self.assertIn('ValueError: child error', output)

    def test_successful_subtests_keep_one_parent_pass(self):
        def body(case):
            for number in (1, 2):
                with case.subTest(number=number):
                    case.assertTrue(number)
        result, _, markers = self.run_case(body)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(markers, ['PASSED'])

    def test_nested_subtest_failure_is_not_duplicated(self):
        def body(case):
            with case.subTest(outer=1):
                with case.subTest(inner=2):
                    case.fail('original failure')
        result, output, markers = self.run_case(body)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(markers, ['FAILED'])
        self.assertIn('outer=1', output)
        self.assertIn('inner=2', output)

    def test_multiline_messages_cannot_add_protocol_events(self):
        def body(case):
            with case.subTest(name='café\n<ERROR::>literal'):
                case.fail('message\n<PASSED::>literal')
        _, output, markers = self.run_case(body)
        self.assertEqual(markers, ['FAILED'])
        self.assertIn('<:LF:><PASSED::>literal', output)

    def test_regular_tests_keep_existing_reporting(self):
        result, _, markers = self.run_case(lambda case: case.assertEqual(1, 1))
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(markers, ['PASSED'])

    def test_regular_failure_remains_failure(self):
        result, _, markers = self.run_case(lambda case: case.assertEqual(1, 2))
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(markers, ['FAILED'])
