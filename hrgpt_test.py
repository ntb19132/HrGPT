import unittest

from app import generate_response


class HrgptTestCase(unittest.TestCase):
    def test_prompt(self):
        question = 'who is run'
        chat_logs = []
        generate_response(question, chat_logs)
        # self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
