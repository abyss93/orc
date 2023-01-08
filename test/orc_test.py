from io import StringIO
from unittest import TestCase
from unittest.mock import patch
import orc
from utils.logger import Logger


class TestOrc(TestCase):
    logger = Logger(False)

    def get_expected(self, file_name):
        with open(file_name, mode="r", encoding="utf-8") as expected_file:
            expected = expected_file.read()
        return expected

    def test_attachments_pdf_png_multipart(self):
        # given
        with patch('sys.stdout', new=StringIO()) as fake_out:
            orc.execute("test_attachments_pdf_png_multipart",
                        {'email_path': 'test_attachments_pdf_png_multipart', 'headers': True, 'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': True, 'debug': False})
            self.assertEqual(fake_out.getvalue(), self.get_expected("test_attachments_pdf_png_multipart_expected"))

    def test_execute_2(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            orc.execute("test_boundary_not_enclosed_in_quotation_marks",
                        {'email_path': 'test_boundary_not_enclosed_in_quotation_marks', 'headers': True,
                         'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': False, 'debug': False})
            self.assertEqual(self.get_expected("test_boundary_not_enclosed_in_quotation_marks_expected"),
                             fake_out.getvalue())

    def test_quoted_printable(self):
        expected = """Return-Path                   <XXXXXXX@XXXXXXX.XXXXXXX>
Received                      from XXXXXXX (XXXXXXX [XX.XX.XX.XX]) by XXXXXXX with ESMTPSA id XXXXXXX for <XXXXXXX@XXXXXXX.XXXXXXX> (version=TLS1_3 cipher=TLS_AES_256_GCM_SHA384 bits=256/256); Sun, 27 Nov 2022 10:12:34 -0800 (PST)
Received                      by XXXXXXX (Postfix, from XXXXXXX XXXXXXX)id XXXXXXX; Sun, 27 Nov 2022 19:12:33 +0100 (CET)
Date                          Sun, 27 Nov 2022 19:12:33 +0100
From                          XXXXXXX@XXXXXXX.XXXXXXX
To                            XXXXXXX@XXXXXXX.XXXXXXX
Message-ID                    <XXXXXXX@XXXXXXX-XXXXXXX.XXXXXXX>
Subject                       TEST quoted printable
Mime-Version                  1.0
Content-Type                  multipart/mixed;boundary="--==_mimepart_9999999999999_88888888-777";charset=UTF-8
Content-Transfer-Encoding     7bit
__ANALYSIS_PAYLOAD__0_0
Content-Type                  text/html;charset=UTF-8
Content-Transfer-Encoding     quoted-printable

    <html>
        <head>
            <style>
                body {
                  font-family: Tahoma, Verdana, sans-serif;
                  font-size: 14px;
                }
                table.articles_table {
                  background-color: #FFFFFF;
                  width: 100%;
                  text-align: left;
                  border-collapse: collapse;
                }
                table.articles_table td, table.articles_table th {
                  border: 0px solid #AAAAAA;
                  padding: 5px 5px;
                  font-size: 13px;
                }
                table.articles_table tbody td {
                  font-size: 10px;
                }
                table.articles_table tr:nth-child(even) {
                  background: #D0E4F5;
                }
                table.articles_table thead {
                  background: #1C6EA4;
                  border-bottom: 2px solid #444444;
                }
                table.articles_table thead th {
                  font-size: 12px;
                  font-weight: bold;
                  color: #FFFFFF;
                }
            </style>
        </head>
        <body>
        <div class="content">
            <table class="articles_table"><tr><th>Feed</th><th>Source</th><th>Topics</th></tr>
\t\t\t\t<tr><td><a href="https://www.bleepingcomputer.com/news/security/google-pushes-emergency-chrome-update-to-fix-8th-zero-day-in-2022/"><b>Google pushes emergency Chrome update to fix 8th zero-day in 2022</b></a></td><td><i>BleepingComputer</i></td><td><i>google</i></td>
\t\t\t\t<tr><td><a href="https://thehackernews.com/2022/11/update-chrome-browser-now-to-patch-new.html"><b>Update Chrome Browser Now to Patch New Actively Exploited Zero-Day Flaw</b></a></td><td><i>The Hacker News</i></td><td><i>google</i></td>
            </table>
        </div>
    </html>

____URLs____
https: //www[.]bleepingcomputer[.]com/news/security/google-pushes-emergency-chrome-update-to-fix-8th-zero-day-in-2022/
https: //thehackernews[.]com/2022/11/update-chrome-browser-now-to-patch-new[.]html
__END_URLs__
__END_ANALYSIS_PAY__0_0
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            orc.execute("test_quoted_printable",
                        {'email_path': 'test_quoted_printable', 'headers': True, 'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': True, 'debug': False})
            self.assertEqual(fake_out.getvalue().replace("\r", ""), expected)
            # if I don't remove carriage return test fails even if output are visually equal

    def test_parse_headers(self):
        # given
        with open('./test_quoted_printable', mode="rt", encoding="utf-8") as email:
            content_lines = email.readlines()
        boundary = "--==_mimepart_9999999999999_88888888-777"

        # when
        result = orc.parse_headers(content_lines, boundary, self.logger)

        # then
        expected = {'Return-Path': ['<XXXXXXX@XXXXXXX.XXXXXXX>'], 'Received':
            [
                'from XXXXXXX (XXXXXXX [XX.XX.XX.XX]) by XXXXXXX with ESMTPSA id XXXXXXX for <XXXXXXX@XXXXXXX.XXXXXXX> (version=TLS1_3 cipher=TLS_AES_256_GCM_SHA384 bits=256/256); Sun, 27 Nov 2022 10:12:34 -0800 (PST)',
                'by XXXXXXX (Postfix, from XXXXXXX XXXXXXX)id XXXXXXX; Sun, 27 Nov 2022 19:12:33 +0100 (CET)'],
                    'Date': ['Sun, 27 Nov 2022 19:12:33 +0100'], 'From': ['XXXXXXX@XXXXXXX.XXXXXXX'],
                    'To': ['XXXXXXX@XXXXXXX.XXXXXXX'], 'Message-ID': ['<XXXXXXX@XXXXXXX-XXXXXXX.XXXXXXX>'],
                    'Subject': ['TEST quoted printable'], 'Mime-Version': ['1.0'],
                    'Content-Type': [
                        'multipart/mixed;boundary="--==_mimepart_9999999999999_88888888-777";charset=UTF-8'],
                    'Content-Transfer-Encoding': ['7bit']}
        self.assertEqual(expected, result)

    def test_parse_headers_Received_always_a_list(self):
        # given
        content_lines = """Return-Path: <XXXXXXX@XXXXXXX.XXXXXXX>
Received: ONLY ONE RECEIVED HEADER IS PRESENT
Date: Sun, 27 Nov 2022 19:12:33 +0100
From: XXXXXXX@XXXXXXX.XXXXXXX
To: XXXXXXX@XXXXXXX.XXXXXXX
Message-ID: <XXXXXXX@XXXXXXX-XXXXXXX.XXXXXXX>
Subject: TEST quoted printable
Mime-Version: 1.0
Content-Type: multipart/mixed;
 boundary="--==_mimepart_9999999999999_88888888-777";
 charset=UTF-8
Content-Transfer-Encoding: 7bit

""".splitlines()
        boundary = "--==_mimepart_9999999999999_88888888-777"

        # when
        result = orc.parse_headers(content_lines, boundary, self.logger)

        # then
        expected = {'Return-Path': ['<XXXXXXX@XXXXXXX.XXXXXXX>'], 'Received': [
            'ONLY ONE RECEIVED HEADER IS PRESENT'],
                    'Date': ['Sun, 27 Nov 2022 19:12:33 +0100'], 'From': ['XXXXXXX@XXXXXXX.XXXXXXX'],
                    'To': ['XXXXXXX@XXXXXXX.XXXXXXX'], 'Message-ID': ['<XXXXXXX@XXXXXXX-XXXXXXX.XXXXXXX>'],
                    'Subject': ['TEST quoted printable'], 'Mime-Version': ['1.0'],
                    'Content-Type': [
                        'multipart/mixed;boundary="--==_mimepart_9999999999999_88888888-777";charset=UTF-8'],
                    'Content-Transfer-Encoding': ['7bit']}
        self.assertEqual(expected, result)
