#!/usr/bin/python3

import argparse
import email

from content_transfer_encoding_strategies.strategy_7bit import Strategy7bit
from content_transfer_encoding_strategies.strategy_8bit import Strategy8bit
from content_transfer_encoding_strategies.strategy_base64 import StrategyBase64
from content_transfer_encoding_strategies.strategy_binary import StrategyBinary
from content_transfer_encoding_strategies.strategy_fallback import StrategyFallback
from content_transfer_encoding_strategies.strategy_quoted_printable import StrategyQuotedPrintable
from utils.logger import Logger
from utils.utils import Utils
from view.UI import UI
from view.terminal_view import TerminalView


def check_for_duplicate_content_type_header(p_headers):
    result = ""
    for h_tuple in p_headers:
        header_key = h_tuple[0]
        header_value = h_tuple[1]
        if header_key != "Content-Type":
            continue
        result = header_value
        if "boundary" in header_value:
            return header_value
    return result


def process_payloads(email_msg, utils, logger, payload_strategies, view, nest_level=-1):
    nest_level += 1
    if isinstance(email_msg.get_payload(), str):
        print("__PLAIN_TEXT__")
    else:
        for i, p in enumerate(email_msg.get_payload()):
            print("**FOUND_PAYLOAD__" + str(nest_level) + "_" + str(i) + "**")
            # https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
            # <<Each part starts with an encapsulation boundary, and then contains a body part consisting of header area, a blank line, and a body area>>
            p_headers = p.items()
            # in some emails there could be duplicate Content-Type header, hence the dict casting would preserve only the last of them
            # but the discarded header could contain a boundary, this way part of the mail would not be considered
            # we need to give priority to analyze ALL the email contents, since this is a security tool, not a tool that checks if the email is RFC-compliant
            content_type_h = check_for_duplicate_content_type_header(p_headers)
            p_headers = dict(p_headers)
            p_headers["Content-Type"] = content_type_h
            view.print_headers(p_headers.items())
            
            if "Content-Transfer-Encoding" in p_headers:
                try:
                    payload_strategies[p_headers["Content-Transfer-Encoding"]].process(p_headers["Content-Type"],
                                                                                       p.get_payload())
                except KeyError:
                    # There are only five valid values for the Content-Transfer-Encoding header: "7bit", "8bit", "base64", 
                    # "quoted-printable" and "binary". The email is broken on purpose by the sender
                    print(
                        f"Error: Strategy not defined for -> Content-Transfer-Encoding: \"{p_headers['Content-Transfer-Encoding']}\"."
                        f" EMAIL IS PROBABLY BROKEN ON PURPOSE BY THE SENDER."
                        f" DOING FALLBACK ON A GENERIC-ANALYSIS STRATEGY")
                    payload_strategies["fallback"].process(p_headers["Content-Type"], p.as_string())
            
            if "Content-Type" not in p_headers:
                # https://www.rfc-editor.org/rfc/rfc2045#section-5.2 defaults to: Content-type: text/plain; charset=us-ascii
                print("text/plain")
            elif p_headers["Content-Type"] is not None and "boundary" in p_headers["Content-Type"]:
                # nested payload, another boundary is present and a recursive call is needed for the next nest_level
                process_payloads(p, utils, logger, payload_strategies, view, nest_level)
            
            
            print("**END_PAYLOAD__" + str(nest_level) + "_" + str(i) + "**")


def execute(email_path, config):
    # read email file
    with open(email_path, mode="rt", encoding="utf-8") as f:
        email_msg = email.message_from_file(f)

    # initialize objects
    logger = Logger(config["debug"])
    view = TerminalView(config["color"])
    utils = Utils(logger)
    payload_strategies = {
        "base64": StrategyBase64(config, logger, utils),
        "quoted-printable": StrategyQuotedPrintable(config, logger, utils),
        "7bit": Strategy7bit(config, logger, utils),
        "8bit": Strategy8bit(config, logger, utils),
        "binary": StrategyBinary(config, logger, utils),
        "fallback": StrategyFallback(config, logger, utils)
    }

    # email processing
    headers = email_msg.items()
    if config["headers"]:
        print("*****HEADERS*****")
        view.print_headers(headers)
        print("*****************")
        print()
    print("*****PAYLOADS*****")
    process_payloads(email_msg, utils, logger, payload_strategies, view)
    print("******************")

    # user-interface only if requested by the user
    if config["user_interface"]:
        ui = UI()
        ui.render(headers)


if __name__ == "__main__":
    LOGO = "\033[35m           ▄▄▄   ▄▄·\033[0m\n" \
           "\033[35m     ▪     ▀▄ █·▐█ ▌▪\033[0m\n" \
           "\033[35m      ▄█▀▄ ▐▀▀▄ ██ ▄▄\033[0m\n" \
           "\033[35m     ▐█▌.▐▌▐█•█▌▐███▌\033[0m\n" \
           "\033[35m      ▀█▄▀▪.▀  ▀·▀▀▀\033[0m\n" \
           "\033[35m -- Email Forensic Tool --\033[0m\n"

    parser = argparse.ArgumentParser(description="\033[35m -- ORC -- Email Forensic Tool --\033[0m\n",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("email_path", type=str, help="Path of the email to analyze (EML format)")
    parser.add_argument("-H", "--headers", help="Print email headers in a friendly way",
                        action="store_true",
                        default=True)
    parser.add_argument("-p", "--print-payload", help="Print email payloads as they are", action="store_true")
    parser.add_argument("-a", "--payload-analysis", help="Payload analysis: hashes, URLs...", action="store_true")
    parser.add_argument("-d", "--debug", help="Debug info to stdout", action="store_true")
    parser.add_argument("-c", "--color", help="Some output sections are printed using terminal colors",
                        action="store_true")
    parser.add_argument("-x", "--user-interface", help="Display Headers in a window", action="store_true")
    args = parser.parse_args()
    config_args = vars(args)
    print(LOGO)
    execute(args.email_path, config_args)
