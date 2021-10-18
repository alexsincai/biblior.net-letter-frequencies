import requests
from bs4 import BeautifulSoup
from string import whitespace, punctuation, digits

URL = "https://biblior.net"


def read_links_on_page(url, selector):
    page = requests.get(url)
    tree = BeautifulSoup(page.text, "html.parser")

    return [item.attrs.get("href") for item in tree.select(selector)]


def read_contents(url, body, removes):
    page = requests.get(url)
    tree = BeautifulSoup(page.text, "html.parser")

    for remove in removes:
        for rem in tree.select(remove):
            rem.decompose()

    output = ""

    for item in tree.select(body):
        output += item.get_text()

    return output


def filter_output(string):
    return [
        c.lower()
        for c in string
        if c not in whitespace and c not in punctuation and c not in digits
    ]


def counter(array):
    temp = {}

    for c in array:
        try:
            temp[c] += 1
        except KeyError:
            temp[c] = 1

    return temp


def flatten(nested):
    return [item for subl in nested for item in subl]


def main():

    page_links = read_links_on_page(
        url=URL + "/carti",
        selector=".views-summary-unformatted a",
    )

    links = flatten(
        [
            read_links_on_page(url=URL + item, selector="td.views-field a")
            for item in page_links
        ]
    )

    pages = flatten(
        [
            read_links_on_page(url=URL + item, selector="#content ul.menu li.leaf a")
            for item in links
        ]
    )

    output = {}

    for page in pages:
        text = filter_output(
            read_contents(
                url=URL + page,
                body="#content .content",
                removes=[".fb-social-like-widget", ".book-navigation"],
            )
        )

        count = counter(text)
        for c in count:
            try:
                output[c] += count[c]
            except KeyError:
                output[c] = count[c]

    output = dict(
        sorted(
            output.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    )
    print(output)


if __name__ == "__main__":
    main()
