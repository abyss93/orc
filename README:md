# orc [WIP]
Quick and dirty email header and body parser.

Just like an Orc, this script is ugly, probably it won't have unit tests, unless parse operation becomes difficult: only trying to parse many mails will tell.
Purpose of this tool is to have an automatic help to perform phishing/spam mail analysis looking at headers and body content. What I want to do is automatically decode base64 (and other types of encodings) mail content to verify if it is legit or not. I also want to extract URLs, eventually decode them (phishing mails often contains 'strange' URLs) and IPs, then do some automatic query on the web to find reputation etc.

Opening mail with this tool should be safe enough, because EML files are read and interpreted by Python as text files, so nothing will be executed and nothing malicious should be triggered unless Python itself contains vulnerable code in the read method (very unlikely, but possible).
