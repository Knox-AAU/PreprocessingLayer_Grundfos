import requests

FILETYPE = '.pdf'
DOMAIN = 'https://www.grundfos.com'
MAX_SITES_TO_CHECK = 7000001
PDF_DOMAIN = "http://net.grundfos.com/Appl/ccmsservices/public/literature/filedata/Grundfosliterature-"

invalid_links = set()
valid_links = set()

# http://net.grundfos.com/Appl/ccmsservices/public/literature/filedata/Grundfosliterature-425556.pdf

def get_response_headers():
    iterations = 0
    for x in range(53):
        link = PDF_DOMAIN + str(x) + FILETYPE
        read = requests.get(link)
        content_type = read.headers.get("content-type")
        print(f"{x}: Content-type = {content_type}")
        if content_type == "None":
            invalid_links.add(x)
        elif content_type == "application/pdf":
            valid_links.add(x)
        iterations = iterations + 1
        if iterations >= 10:
            print("10 iterations")
            print(iterations % 10)
            iterations = 0
    return


if __name__ == "__main__":
    print("initiating the scraper")
    get_response_headers()
