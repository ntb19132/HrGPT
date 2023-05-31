import unittest

from app import generate_response


class HrgptTestCase(unittest.TestCase):
    def test_prompt(self):
        question = 'who is run'
        # {"messages": [{"role": "user", "content": "who r u?"}]
        #  }
        chat_logs = [{"role": "user", "content": 'who is run'}]
        generate_response('hrgpt', chat_logs)
        # self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
