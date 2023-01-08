#!/usr/bin/python3

import argparse
import base64
import hashlib
import quopri
import re

from content_transfer_encoding_strategies.strategy_7bit import Strategy7bit
from content_transfer_encoding_strategies.strategy_8bit import Strategy8bit
from content_transfer_encoding_strategies.strategy_base64 import StrategyBase64
from content_transfer_encoding_strategies.strategy_binary import StrategyBinary
from content_transfer_encoding_strategies.strategy_quoted_printable import StrategyQuotedPrintable
from utils.hash_service import Utils
from utils.logger import Logger



def p_debug(debug):
    print("DEBUG>>>")
    print(debug)
    print(">>>DEBUG")


def find_boundary(content, logger):
    res = None
    for line in content:
        boundary_check = re.search("boundary=(\"(.+)\")", line)
        if boundary_check is not None:
            res = boundary_check.group().replace("boundary=\"", "").replace("\"", "")
            break
        else:  # sometimes boundary is not enclosed in a couple of "
            boundary_check = re.search("boundary=((.+))", line)
            if boundary_check is not None:
                res = boundary_check.group().replace("boundary=", "")
                break
    return res


def find_urls(string_to_check):
    urls = re.findall(
        r"((http|https)?:\/\/[www]?\.?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        string_to_check)
    if urls is not None and len(urls) > 0:
        print("____URLs____")
        for url in urls:
            print(url[0].replace(".", "[.]").replace(":", ": "))
        print("__END_URLs__")


def parse_headers(content_lines, boundary, logger):
    headers = {}
    for line in content_lines:
        # stops when payload is reached (= boundary appears), this is only to prevent non-rfc compliant cases, even if they are almost impossible to see
        # if line is the line where boundary is defined, goes on, header are not finished yet
        # if line is empty header section is finished (https://www.rfc-editor.org/rfc/rfc5322#section-3.5), so stops
        # if an email has empty lines between headers' lines it is not compliant with RFC
        if (boundary is not None and ("--" + boundary) in line) or (line == "\n"):
            logger.log("Header end")
            break
        # header name field format specs https://www.rfc-editor.org/rfc/rfc2822#section-2.2 , best regex of all time :)
        check_line_header = re.search("(^[!-~]*: )", line)
        # the line contains a keyword that identifies a header
        if check_line_header is not None:
            logger.log("Header line found: " + line)
            header_key = check_line_header.group().replace(": ", "")
            header_value = line.replace(check_line_header.group(), "").replace("\n", "")
            header_value = re.sub(" {2,}", "", header_value)  # replaces multiple whitespaces with just one
            if header_key not in headers.keys():
                # header found for the first time
                headers[header_key] = [header_value]
            elif type(headers[header_key]) is list:
                # header value is a list (e.g. Received)
                headers[header_key].append(header_value)
        # line starts with a blankspace, it is the following part of the last header found
        # https://www.rfc-editor.org/rfc/rfc5322#section-2.2.3
        elif line.startswith(" ") or line.startswith("\t"):
            line = line[1:]  # remove first blank, don't need it
            line = re.sub(" {2,}", " ", line)  # replaces multiple whitespaces with just one
            logger.log("Header next line found: " + line)
            # here header_jey is equal to the last processed header, so I can use the variable
            # if the current is an header that can appear multiple times AND its value can be defined on more than one row
            # here the script is processing the last header of that type in the headers-list, so the script pushes there
            if type(headers[header_key]) is list:
                headers[header_key][len(headers[header_key]) - 1] += line.replace("\n", "")
            # else it is a header that can appear only one time in the list,
            else:
                headers[header_key] += line.replace("\n", "")
    logger.log(headers)
    return headers


# returns an array where each element is a payload (= all the lines between a --boundary and --boundary-- couple)
# each payload has a header part and a real payload part
def parse_payload(whole_content, boundary, logger):
    # https://www.rfc-editor.org/rfc/rfc2046#section-5.1.1
    if boundary:
        payloads = whole_content.split(
            "--" + boundary + "\n")  # payload starts with "--" + boundary as per RFC1341, here split removes all --boundary but leaves closing --boundary-- to be romoved
        logger.log("parse_payload split boundary|payloads length: |" + str(len(payloads)) + "|" + str(payloads))
        del payloads[0]  # delete all the email part located before the start of boundary
        remove_boundary_from = len(payloads) - 1
        # a split like the one above leaves the closing boundary (that is --boundary--\n) in the last element of the array, that final boundary must be removed
        # because the split removed all of its relatives. Remove the last boundary line, that has "--" appended after boundary as per RFC1341
        payloads[remove_boundary_from] = payloads[remove_boundary_from].replace("--" + boundary + "--", "")
        logger.log("parse_payload remove closing boundary|" + str(payloads))
        return payloads
    return []  # no payloads defined with boundaries


# https://www.rfc-editor.org/rfc/rfc5321.html#section-4.4
# https://www.rfc-editor.org/rfc/rfc7489#section-3.1.1
# https://stackoverflow.com/questions/21480430/can-a-message-have-multiple-senders
def print_headers(headers):
    for k, v in headers.items():
        if isinstance(v, list):
            for i, r in enumerate(v):
                print("{:<30}".format(k), end="")
                print("{:}".format(r))
        else:
            print("{:<60}{:<50}".format(k, v))


def print_parsed_payloads(payloads):
    for i, p in enumerate(payloads):
        print("__PAYLOAD__" + str(i))
        print(p)
        print("__END_PAY__" + str(i))


def parse_email(content_lines, whole_content, logger):
    boundary = find_boundary(content_lines, logger)
    headers = parse_headers(content_lines, boundary, logger)
    payloads = parse_payload(whole_content, boundary, logger)
    return headers, payloads


def process_content_tansfer_encoding_base64(p_base64):
    return base64.b64decode(p_base64)


def hashes_of(obj):
    print("____HASHES____")
    md5 = hashlib.md5(obj).hexdigest()
    sha1 = hashlib.sha1(obj).hexdigest()
    sha256 = hashlib.sha256(obj).hexdigest()
    print("md5sum: {:80} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(md5, md5))
    print("sha1sum: {:79} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(sha1, sha1))
    print("sha256sum: {:77} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(sha256, sha256))
    print("__END_HASHES__")


def process_payloads(payloads, utils, logger, nest_level=-1):
    nest_level += 1
    for i, p in enumerate(payloads):
        print("__ANALYSIS_PAYLOAD__" + str(nest_level) + "_" + str(i))
        # https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
        # <<Each part starts with an encapsulation boundary, and then contains a body part consisting of header area, a blank line, and a body area>>
        to_process = p.splitlines(
            True)  # I want newline chars during header processing, parse_headers need them to find the header section end
        logger.log("process_payloads to_process splitlines|" + str(to_process))
        p_headers = parse_headers(to_process, None, logger)
        print_headers(p_headers)
        p_body_start = to_process.index(
            '\n') + 1  # find the first blank line, that is the one between headers and body, and add 1
        # TODO refactor: strategy and factory pattern can be applied here
        if p_headers is not None and "Content-Type" not in p_headers:
            # https://www.rfc-editor.org/rfc/rfc2045#section-5.2 defaults to: Content-type: text/plain; charset=us-ascii
            print("text/plain")
        if p_headers is not None and p_headers["Content-Type"] is not None and \
                "boundary" in p_headers["Content-Type"][0]:  # [0] -> only one Content-Type is admitted
            # nested payload, another boundary
            nested_headers, nested_payloads = parse_email(to_process, p, logger)
            process_payloads(nested_payloads, utils, logger, nest_level)
        if p_headers is not None and "Content-Transfer-Encoding" in p_headers:
            # try:
            #     print(p_headers["Content-Transfer-Encoding"][0])
            #     PAYLOAD_STRATEGIES[p_headers["Content-Transfer-Encoding"][0]]
            # except KeyError:
            #     print("Invalid Content-Transfer-Encoding")

            if "base64" in p_headers["Content-Transfer-Encoding"]:
                # Encoded 7-bit ASCII
                body = ''.join(to_process[p_body_start:]).replace("\n", "")
                decoded = process_content_tansfer_encoding_base64(body)
                logger.log(body)
                hashes_of(decoded)
                # if find_urls_conf: find_urls(str(decoded))
                # TODO
            elif "quoted-printable" in p_headers["Content-Transfer-Encoding"]:
                # Encoded 7-bit ASCII
                # join preserving \n because while it is useful not to have \n in base64, newlines are needed
                # to correctly process the body in quoted-printable elements (e.g. HTML code) https://www.rfc-editor.org/rfc/rfc2045#section-6.7
                body = ''.join(to_process[p_body_start:])
                decoded = quopri.decodestring(body).decode("utf-8")
                logger.log(body)
                print(decoded)
                utils.find_urls(decoded)
                # TODO
            elif "7bit" in p_headers["Content-Transfer-Encoding"]:
                # Unencoded 7-bit ASCII
                print("7bit")
                # TODO
            elif "8bit" in p_headers["Content-Transfer-Encoding"]:
                # Unencoded 8-bit ASCII
                print("8bit")
                # TODO
            elif "binary" in p_headers["Content-Transfer-Encoding"]:
                # Any data acceptable, no restrictions on character set
                print("binary")
                hashes_of(body)
                # TODO
        print("__END_ANALYSIS_PAY__" + str(nest_level) + "_" + str(i))


def print_text_plain(whole_content):
    print("____TEXT_PLAIN____")
    whole_content_lines = whole_content.splitlines(True)
    text_plain_index = whole_content_lines.index("\n") + 1  # end of headers section, plus 1 to exclude the \n line
    text_plain = "".join(whole_content_lines[text_plain_index:])
    print(text_plain)
    print("__END_TEXT_PLAIN__")


def forensic(headers, whole_content):
    if "Content-Length" in headers.keys():
        content_length = headers["Content-Length"]
        whole_content_lines = whole_content.splitlines(True)
        end_of_header_section_index = whole_content_lines.index("\n")  # also start of payload section
        end_of_payload_section = len(whole_content_lines)
        payloads_as_string = "".join(whole_content_lines[end_of_header_section_index:end_of_payload_section])
        print(len(payloads_as_string))


def execute(email_path, config):
    # read email file
    with open(email_path, mode="rt", encoding="utf-8") as email:
        content_lines = email.readlines()
        email.seek(0)
        whole_content = email.read()
    
    # initialize objects
    logger = Logger(config["debug"])
    utils = Utils(logger, config["find_urls"])
    payload_strategies = {"base64": StrategyBase64(config, logger, utils),
                          "quoted-printable": StrategyQuotedPrintable(config, logger, utils),
                          "7bit": Strategy7bit(logger), "8bit": Strategy8bit(logger),
                          "binary": StrategyBinary(logger, utils)}

    headers, payloads = parse_email(content_lines, whole_content, logger)
    if config["headers"]: print_headers(headers)

    if len(payloads) > 0:
        if config["print_payload"]: print_parsed_payloads(payloads)
        if config["payload_analysis"]: process_payloads(payloads, utils, logger)
    elif len(payloads) == 0:
        if config["print_payload"]: print_text_plain(whole_content)

    # forensic(headers, whole_content)


if __name__ == "__main__":
    LOGO = "           ▄▄▄   ▄▄·\n" \
           "     ▪     ▀▄ █·▐█ ▌▪\n" \
           "      ▄█▀▄ ▐▀▀▄ ██ ▄▄\n" \
           "     ▐█▌.▐▌▐█•█▌▐███▌\n" \
           "      ▀█▄▀▪.▀  ▀·▀▀▀\n" \
           "_____________________\n"

    parser = argparse.ArgumentParser(description="Email forensic tool",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("email_path", type=str, help="Path of the email to analyze")
    parser.add_argument("-H", "--headers", help="Print email headers in a friendly way", action="store_true")
    parser.add_argument("-p", "--print-payload", help="Print email payloads as they are", action="store_true")
    parser.add_argument("-a", "--payload-analysis", help="Payload analysis", action="store_true")
    parser.add_argument("-u", "--find-urls", help="Search for URLs", action="store_true")
    parser.add_argument("-d", "--debug", help="Debug info to stdout", action="store_true")
    args = parser.parse_args()
    config_args = vars(args)
    print(LOGO)

    execute(args.email_path, config_args)
