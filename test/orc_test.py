from io import StringIO
from unittest import TestCase
from unittest.mock import patch
import orc
from content_transfer_encoding_strategies.strategy_7bit import Strategy7bit
from utils.logger import Logger
from utils.utils import Utils


class TestOrc(TestCase):
    logger = Logger(False)

    def open_file(self, file_name, lines=False):
        with open(file_name, mode="r", encoding="utf-8") as expected_file:
            if lines is False: content = expected_file.read()
            if lines is True: content = expected_file.readlines()
        return content

    def test_attachments_pdf_png_multipart(self):
        # given
        with patch('sys.stdout', new=StringIO()) as fake_out:
            # when
            orc.execute("test_attachments_pdf_png_multipart",
                        {'email_path': 'test_attachments_pdf_png_multipart', 'headers': True, 'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': True, 'debug': False, 'color': False, 'user_interface': False})
            # then
            self.assertEqual(fake_out.getvalue(), self.open_file("test_attachments_pdf_png_multipart_expected"))

    def test_execute_2(self):
        # given
        with patch('sys.stdout', new=StringIO()) as fake_out:
            # when
            orc.execute("test_boundary_not_enclosed_in_quotation_marks",
                        {'email_path': 'test_boundary_not_enclosed_in_quotation_marks', 'headers': True,
                         'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': False, 'debug': False, 'color': False, 'user_interface': False})
            # then
            self.assertEqual(self.open_file("test_boundary_not_enclosed_in_quotation_marks_expected"),
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
https[:]//www[.]bleepingcomputer[.]com/news/security/google-pushes-emergency-chrome-update-to-fix-8th-zero-day-in-2022/
https[:]//thehackernews[.]com/2022/11/update-chrome-browser-now-to-patch-new[.]html
__END_URLs__
__END_ANALYSIS_PAY__0_0
"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            orc.execute("test_quoted_printable",
                        {'email_path': 'test_quoted_printable', 'headers': True, 'print_payload': False,
                         'payload_analysis': True,
                         'find_urls': True, 'debug': False, 'color': False, 'user_interface': False})
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

    def test_parse_header_Received_SPF_becomes_one_line(self):
        # given
        content_lines = """Received-SPF: pass (mybox.example.org: domain of
    myname@example.com designates 192.0.2.1 as permitted sender)
       receiver=mybox.example.org; client-ip=192.0.2.1;
       envelope-from="myname@example.com"; helo=foo.example.com;""".splitlines()

        # when
        result = orc.parse_headers(content_lines, "", self.logger)

        # then
        expected = {'Received-SPF': [
            "pass (mybox.example.org: domain of myname@example.com designates 192.0.2.1 as permitted sender) receiver=mybox.example.org; client-ip=192.0.2.1; envelope-from=\"myname@example.com\"; helo=foo.example.com;"]}
        self.assertEqual(expected["Received-SPF"][0], result["Received-SPF"][0])

    def test_strategy_7bit_url_are_recognized_text_html(self):
        # given
        utils = Utils(self.logger, True)
        sut = Strategy7bit(self.logger, utils)
        to_process = ['Content-Type: text/html; charset=UTF-8\n', 'Content-Transfer-Encoding: 7bit\n', '\n', '<html>\n',
                      '  <head>\n', '\n', '    <meta http-equiv="content-type" content="text/html; charset=UTF-8">\n',
                      '  </head>\n', '  <body>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr">TEST PLAIN TEXT</span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <p><font face="Courier New, Courier, monospace"><font size="6">Lorem\n',
                      '          ipsum dolor sit amet, consectetur adipisci elit, sed do\n',
                      '          eiusmod tempor incidunt ut labore et dolore magna aliqua. Ut\n',
                      '          enim ad minim veniam, quis nostrum exercitationem ullamco\n',
                      '          laboriosam, nisi ut aliquid ex ea commodi consequatur. Duis\n',
                      '          aute irure reprehenderit in voluptate velit esse cillum dolore\n',
                      '          eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat\n',
                      '          non proident, sunt in culpa qui officia deserunt mollit anim\n',
                      '          id est laborum.</font></font></p>\n',
                      '    <p><font face="Courier New, Courier, monospace"><font size="6">________________________________________<br>\n',
                      '          <span style="left: 94.6667px; top: 97.8346px; font-size: 20px;\n',
                      '            transform: scaleX(0.859947);" role="presentation" dir="ltr"></span></font></font></p>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr">TEST URLS</span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 97.8346px; font-size: 20px; transform:\n',
                      '        scaleX(0.859947);" role="presentation" dir="ltr"><br>\n', '      </span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 143.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.80414);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_blah">http://foo.com/blah_blah</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 166.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.804636);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_blah/">http://foo.com/blah_blah/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 189.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.811991);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_blah_(wikipedia)">http://foo.com/blah_blah_(wikipedia)</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 212.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.812986);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_blah_(wikipedia)_(again)">http://foo.com/blah_blah_(wikipedia)_(again)</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 235.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.797146);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://www.example.com/wpstyle/?p=364">http://www.example.com/wpstyle/?p=364</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 258.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.796102);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="https://www.example.com/foo/?bar=baz&amp;inga=42&amp;quux">https://www.example.com/foo/?bar=baz&amp;inga=42&amp;quux</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 304.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.791765);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid:password@example.com:8080">http://userid:password@example.com:8080</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 327.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.792232);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid:password@example.com:8080/">http://userid:password@example.com:8080/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 350.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.795321);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid@example.com">http://userid@example.com</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 373.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.795828);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid@example.com/">http://userid@example.com/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 396.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.794281);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid@example.com:8080">http://userid@example.com:8080</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 419.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.794839);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid@example.com:8080/">http://userid@example.com:8080/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 442.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.79178);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid:password@example.com">http://userid:password@example.com</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 465.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.792572);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://userid:password@example.com/">http://userid:password@example.com/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 488.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.781782);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://142.42.1.1/">http://142.42.1.1/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 511.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.784382);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://142.42.1.1:8080/">http://142.42.1.1:8080/</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 606.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.799555);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_(wikipedia)#cite-1">http://foo.com/blah_(wikipedia)#cite-1</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 629.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.802541);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/blah_(wikipedia)_blah#cite-1">http://foo.com/blah_(wikipedia)_blah#cite-1</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 675.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.781742);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.com/(something)?after=parens">http://foo.com/(something)?after=parens</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 721.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.776947);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://code.google.com/events/#&amp;product=browser">http://code.google.com/events/#&amp;product=browser</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 744.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.788394);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://j.mp">http://j.mp</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 767.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.797328);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="ftp://foo.bar/baz">ftp://foo.bar/baz</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 790.001px; font-size: 20px; transform:\n',
                      '        scaleX(0.802077);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://foo.bar/?q=Test%20URL-encoded%20stuff">http://foo.bar/?q=Test%20URL-encoded%20stuff</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 864.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.808844);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://-.~_!$&amp;\'()*+,;=:%40:80%2f::::::@example.com">http://-.~_!$&amp;\'()*+,;=:%40:80%2f::::::@example.com</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 887.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.771212);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://1337.net">http://1337.net</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 910.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.781966);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://a.b-c.de">http://a.b-c.de</a></span></font><br\n',
                      '      role="presentation">\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 933.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.781849);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="http://223.255.255.254">http://223.255.255.254</a></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 956.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.80114);" role="presentation" dir="ltr"><a class="moz-txt-link-freetext" href="https://foo_bar.example.com/">https://foo_bar.example.com/</a></span><span\n',
                      '        style="left: 94.6667px; top: 258.835px; font-size: 20px;\n',
                      '        transform: scaleX(0.796102);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 258.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.796102);" role="presentation" dir="ltr"><a class="moz-txt-link-abbreviated" href="http://www.example.com/foo/?bar=baz&amp;inga=42&amp;quux">www.example.com/foo/?bar=baz&amp;inga=42&amp;quux</a></span></font><font\n',
                      '      face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 956.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.80114);" role="presentation" dir="ltr"></span></font><br>\n',
                      '    <font face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 258.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.796102);" role="presentation" dir="ltr">example.com/foo/?bar=baz&amp;inga=42&amp;quux</span></font><font\n',
                      '      face="Courier New, Courier, monospace"><span style="left:\n',
                      '        94.6667px; top: 956.835px; font-size: 20px; transform:\n',
                      '        scaleX(0.80114);" role="presentation" dir="ltr"></span></font>\n',
                      '    <div id="dialogContainer"> </div>\n',
                      '    <font face="Courier New, Courier, monospace"> </font>\n', '  </body>\n', '</html>\n', '\n']
        p_body_start = 3

        # when
        result = sut.process(["text/html"], to_process, 3)

        # then
        expected = [
            "http[:]//foo[.]com/blah_blah",
            "http[:]//foo[.]com/blah_blah/",
            "http[:]//foo[.]com/blah_blah_(wikipedia)",
            "http[:]//foo[.]com/blah_blah_(wikipedia)_(again)",
            "http[:]//www[.]example[.]com/wpstyle/?p=364",
            "https[:]//www[.]example[.]com/foo/?bar=baz&amp;inga=42&amp;quux",
            "http[:]//userid[:]password@example[.]com[:]8080",
            "http[:]//userid[:]password@example[.]com[:]8080/",
            "http[:]//userid@example[.]com",
            "http[:]//userid@example[.]com/",
            "http[:]//userid@example[.]com[:]8080",
            "http[:]//userid@example[.]com[:]8080/",
            "http[:]//userid[:]password@example[.]com",
            "http[:]//userid[:]password@example[.]com/",
            "http[:]//142[.]42[.]1[.]1/",
            "http[:]//142[.]42[.]1[.]1[:]8080/",
            "http[:]//foo[.]com/blah_(wikipedia)#cite-1",
            "http[:]//foo[.]com/blah_(wikipedia)_blah#cite-1",
            "http[:]//foo[.]com/(something)?after=parens",
            "http[:]//code[.]google[.]com/events/#&amp;product=browser",
            "http[:]//j[.]mp",
            "ftp[:]//foo[.]bar/baz",
            "http[:]//foo[.]bar/?q=Test%20URL-encoded%20stuff",
            "http[:]//-[.]~_!$&amp;'()*+,;=[:]%40[:]80%2f[:][:][:][:][:][:]@example[.]com",
            "http[:]//1337[.]net",
            "http[:]//a[.]b-c[.]de",
            "http[:]//223[.]255[.]255[.]254",
            "https[:]//foo_bar[.]example[.]com/",
            "http[:]//www[.]example[.]com/foo/?bar=baz&amp;inga=42&amp;quux",
        ]

        self.assertEqual(expected, result)


    def test_payload_structure(self):
        # given
        email = self.open_file("test_attachments_pdf_png_multipart")
        
        # when
        result = orc.payload_structure(email, {})
        
        # then
        expected = {}
        #self.assertEqual(expected, result)