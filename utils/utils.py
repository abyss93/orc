import hashlib
import re


class Utils:
    def __init__(self, logger):
        self.logger = logger

    @staticmethod
    def hashes_of(obj):
        print("*****HASHES*****")
        md5 = hashlib.md5(obj).hexdigest()
        sha1 = hashlib.sha1(obj).hexdigest()
        sha256 = hashlib.sha256(obj).hexdigest()
        print("md5sum: {:80} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(md5, md5))
        print("sha1sum: {:79} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(sha1, sha1))
        print("sha256sum: {:77} -> PIVOT TO VT: https://www.virustotal.com/gui/search/{:}".format(sha256, sha256))
        print("***END_HASHES***")

    @staticmethod
    def find_urls(string_to_check):
        res = []
        urls = re.findall(
            r"((http:\/\/|https:\/\/|ftp:\/\/|www.)\.?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            string_to_check)
        if urls is not None and len(urls) > 0:
            for url in urls:
                res.append(url[0].replace(".", "[.]").replace(":", "[:]"))
        res = list(dict.fromkeys(res))
        print("____URLs____")
        for r in res:
            print(r)
        print("__END_URLs__")
        return res

    @staticmethod
    def find_urls_html(html):
        res = []
        urls = re.findall("(?<=href=\")(.*?)(?=\")", html)
        if urls is not None and len(urls) > 0:
            for url in urls:
                res.append(url.replace(".", "[.]").replace(":", "[:]"))
        res = list(dict.fromkeys(res))
        print("____URLs____")
        for r in res:
            print(r)
        print("__END_URLs__")
        return res
