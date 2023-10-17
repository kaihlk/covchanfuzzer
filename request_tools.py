###Header Compare

def compare_strings():
    header1 = "GET https://>>SUDBDOMAIN_PLACEHOLDER<<.>>DOMAIN_PLACEHOLDER<</ HTTP/1.1\nhOST: >>HOST_PLACEHOLDER<<\nuSER-aGENT: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\naCCEPT: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\naCCEPT-eNCODING: gzip, deflate, br\naCCEPT-lANGUAGE: en-US,en;q=0.5\ndnt: 1\ncONNECTION: keep-alive\nuPGRADE-iNSECURE-rEQUESTS: 1\nsEC-fETCH-dEST: document\nsEC-fETCH-mODE: navigate\nsEC-fETCH-sITE: cross-site"

    header2 = "GET https://>>SUDBDOMAIN_PLACEHOLDER<<.>>DOMAIN_PLACEHOLDER<</ HTTP/1.1\nHost: >>HOST_PLACEHOLDER<<\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\nAccept-Encoding: gzip, deflate, br\nAccept-Language: en-US,en;q=0.5\nDNT: 1\nConnection: keep-alive\nUpgrade-Insecure-Requests: 1\nSec-Fetch-Dest: document\nSec-Fetch-Mode: navigate\nSec-Fetch-Site: cross-site"

    # Initialize a count variable for differing letters
    differing_letter_count = 0

    # Compare the two headers character by character
    for char1, char2 in zip(header1, header2):
        if char1 != char2 and char1.lower() == char2.lower():
            differing_letter_count += 1

    print(f"The number of differing letters in case is: {differing_letter_count}")



if __name__ == '__main__':
    
    compare_strings()