from io import StringIO
from unittest import TestCase
from unittest.mock import patch
import orc


class TestOrc(TestCase):

    def test_execute(self):
        with open("expected", mode="r", encoding="utf-8") as expected_file:
            expected = expected_file.read()

        with patch('sys.stdout', new=StringIO()) as fake_out:
            orc.execute("mail_test",
                        {'email_path': 'mail_test', 'headers': True, 'print_payload': False, 'payload_analysis': True,
                         'find_urls': True, 'debug': False})
            self.assertEqual(fake_out.getvalue(), expected)
