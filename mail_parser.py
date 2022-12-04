import re
import base64
import hashlib
import quopri
from colorize import Colorize


def find_boundary(content):
    res = None
    for line in content:
        boundary_check = re.search("boundary=(\"(.+)\")", line)
        if boundary_check is not None:
            res = boundary_check.group().replace("boundary=\"", "").replace("\"", "")
            break
    return res


def find_urls(strint_to_check):
    return re.findall(
        r"(https?:\/\/www\.?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        strint_to_check)


def parse_headers(content_lines, boundary, debug=False):
    headers = {}
    for line in content_lines:
        # stops when payload is reached (= boundary appears), this is only to prevent non-rfc compliant cases, even if they are almost impossible to see
        # if line is the line where boundary is defined, goes on, header are not finished yet
        # if line is empty header section is finished (https://www.rfc-editor.org/rfc/rfc5322#section-3.5), so stops
        if (boundary is not None and ("--" + boundary) in line) or line == "":
            if debug: print("Header end")
            break
        check_line_header = re.search("(.*: )", line)
        # the line contains a keyword that identifies an header
        if check_line_header is not None:
            if debug: print("Header line found: " + line)
            header_key = check_line_header.group().replace(": ", "")
            header_value = line.replace(check_line_header.group(), "").replace("\n", "")
            if header_key not in headers.keys():
                # header found for the first time
                headers[header_key] = header_value
            elif type(headers[header_key]) is list:
                # header value is a list (e.g. Received)
                headers[header_key].append(header_value)
            else:
                headers[header_key] = [headers[header_key]]
                headers[header_key].append(header_value)
        # line starts with a blankspace, it is the following part of the last header found
        # https://www.rfc-editor.org/rfc/rfc5322#section-2.2.3
        elif line.startswith(" "):
            if debug: print("Header next line found: " + line)
            # here header_jey is equal to the last processed header, so I can use the variable
            # if the current is an header that can appear multiple times AND its value can be defined on more than one row
            # here the script is processing the last header of that type in the headers-list, so the script pushes there
            if type(headers[header_key]) is list:
                headers[header_key][len(headers[header_key]) - 1] += line.replace("\n", "")
            # else it is a header that can appear only one time in the list,
            else:
                headers[header_key] += line.replace("\n", "")
    return headers


def parse_payload(whole_content, boundary):
    # https://www.rfc-editor.org/rfc/rfc2046#section-5.1.1
    if boundary:
        payloads = whole_content.split("--" + boundary + "\n")  # payload starts with "--" + boundary as per RFC1341
        del payloads[0]  # delete all the email part located before the start of boundary
        remove_boundary_from = len(payloads) - 1
        # a split like the one above leaves the closing boundary (that is --boundary--\n) in the last element of the array, that final boundary must be removed
        # because the split removed all of its relatives. Remove the last boundary line, that has "--" appended after boundary as per RFC1341
        payloads[remove_boundary_from] = payloads[remove_boundary_from].replace("--" + boundary + "--\n", "")
        return payloads


def print_parsed_headers(headers):
    for k, v in headers.items():
        # TODO refator: make function to group common code
        if k == "Received":  # https://www.rfc-editor.org/rfc/rfc5321.html#section-4.4
            for i, r in enumerate(v):
                colorize.printc("{:<30}".format(k), "blue", end="")
                # hop 0 = email destination ; hop X (biggest one) = email source
                colorize.printc("hop {:<26}".format(i), "blue", end="")
                colorize.printc("{:}".format(r), "blue")
        elif k == "From" and isinstance(v,
                                        list):  # https://stackoverflow.com/questions/21480430/can-a-message-have-multiple-senders
            for i, r in enumerate(v):
                colorize.printc("{:<30}".format(k), "blue", end="")
                colorize.printc("originator {:<19}".format(i), "blue", end="")
                colorize.printc("{:}".format(r), "blue")
        elif k == "DKIM-Signature" and isinstance(v,
                                                  list):  # https://www.rfc-editor.org/rfc/rfc7489#section-3.1.1
            for i, r in enumerate(v):
                colorize.printc("{:<30}".format(k), "blue", end="")
                colorize.printc("signature {:<19}".format(i), "blue", end="")
                colorize.printc("{:}".format(r), "blue")
        else:
            print("{:<60}{:<50}".format(k, v))


def print_parsed_payloads(payloads):
    for i, p in enumerate(payloads):
        colorize.printc("__PAYLOAD__" + str(i), "red")
        print(p)
        colorize.printc("__END_PAY__" + str(i), "red")


def parse_email(content_lines, whole_content, debug):
    boundary = find_boundary(content_lines)
    headers = parse_headers(content_lines, boundary, debug)
    payloads = parse_payload(whole_content, boundary)
    return headers, payloads


def process_content_tansfer_encoding_base64(p_base64):
    return base64.b64decode(p_base64)


def hashes_of(obj):
    print("md5sum:    " + hashlib.md5(obj).hexdigest())
    print("sha1sum:   " + hashlib.sha1(obj).hexdigest())
    print("sha256sum: " + hashlib.sha256(obj).hexdigest())


def process_payloads(payloads):
    for i, p in enumerate(payloads):
        colorize.printc("__ANALYSIS_PAYLOAD__" + str(i), "yellow")
        # https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
        # <<Each part starts with an encapsulation boundary, and then contains a body part consisting of header area, a blank line, and a body area>>
        to_process = p.splitlines()  # I don't want newline chars during header processing, eventually restore them after, in quoted-printable for example
        p_headers = parse_headers(to_process, None)
        print_parsed_headers(p_headers)
        p_body_start = to_process.index(
            '') + 1  # find the first blank line, that is the one between headers and body, and add 1
        # TODO refactor: strategy and factory pattern can be applied here
        if p_headers is not None and "Content-Transfer-Encoding" in p_headers:
            if p_headers["Content-Transfer-Encoding"] == "base64":
                # Encoded 7-bit ASCII
                # slicing guarantees that the last blank line placed between body-end and closing-boundary-element is not considered part of the body
                # itself, because slice operation does not include the right-end index, len(p_body_start) - 1 can be used
                # while joining with \n still works (decoded body has the same hash of decoded body joining with '')
                # I prefer to remove line breaks
                body = ''.join(to_process[p_body_start:len(to_process) - 1])
                decoded = process_content_tansfer_encoding_base64(body)
                hashes_of(decoded)
                # TODO
            elif p_headers["Content-Transfer-Encoding"] == "quoted-printable":
                # Encoded 7-bit ASCII
                # slicing guarantees that the last blank line placed between body-end and closing-boundary-element is not considered part of the body
                # itself, because slice operation does not include the right-end index, len(p_body_start) - 1 can be used
                # join with \n because while it is useful not to have \n in lines in method parse_headers
                # they are needed to correctly process the body in quoted-printable elements (e.g. HTML code)
                body = '\n'.join(to_process[p_body_start:len(to_process) - 1])
                print("quoted‑printable")
                decoded = quopri.decodestring(body).decode("utf-8")
                print(find_urls(decoded))
                # TODO
            elif p_headers["Content-Transfer-Encoding"] == "7bit":
                # Unencoded 7-bit ASCII
                print("7bit")
                # TODO
            elif p_headers["Content-Transfer-Encoding"] == "8bit":
                # Unencoded 8-bit ASCII
                print("8bit")
                # TODO
            elif p_headers["Content-Transfer-Encoding"] == "binary":
                # Any data acceptable, no restrictions on character set
                print("binary")
                hashes_of(body)
                # TODO
        colorize.printc("__END_ANALYSIS_PAY__" + str(i), "yellow")


colorize = Colorize()
with open("mail_test_4", mode="rt", encoding="utf-8") as email:
    content_lines = email.readlines()
    email.seek(0)
    whole_content = email.read()

headers, payloads = parse_email(content_lines, whole_content, debug=False)
print_parsed_headers(headers)

if payloads is not None:
    # print_parsed_payloads(payloads)
    process_payloads(payloads)

# print(find_email_urls(content_lines))
