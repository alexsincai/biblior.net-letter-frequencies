"""Scrapes https://biblior.net and outputs a sorted dictionary of letter frequencies."""

from string import whitespace, punctuation, digits
from typing import Any, List
from json import dump
import requests
from bs4 import BeautifulSoup

URL = "https://biblior.net"


def read_links_on_page(url: str, selector: str) -> List[str]:
    """Reads all links on a given page

    Args:
        url (str): The URL to be read
        selector (str): The CSS selector for the wanted links

    Returns:
        List[str]: The desired list of links
    """
    page = requests.get(url)
    tree = BeautifulSoup(page.text, "html.parser")

    return [item.attrs.get("href") for item in tree.select(selector)]


def read_contents(url: str, body: str, removes: List[str]) -> str:
    """Reads the contents of a URL, keeping the element specified and removing the rest

    Args:
        url (str): The URL of the page to be read
        body (str): The CSS selector for the content block
        removes (List[str]): The list of CSS selectors to be removed from the page

    Returns:
        str: The text of the page
    """
    page = requests.get(url)
    tree = BeautifulSoup(page.text, "html.parser")

    for remove in removes:
        for rem in tree.select(remove):
            rem.decompose()

    output = ""

    for item in tree.select(body):
        output += item.get_text()

    return output


def filter_output(string: str) -> List[str]:
    """Keeps only alphabetic characters from a string

    Args:
        string (str): The input string

    Returns:
        List[str]: The list of alphabetic characters
    """
    extras = [
        "—",
        " ",
        "–",
        "„",
        "•",
        "”",
        "«",
        "»",
        "­",
        "°",
        "£",
        "…",
        "’",
        "“",
        "‚",
        "½",
        "˝",
    ]

    return [
        character.lower()
        for character in string
        if character not in whitespace
        and character not in punctuation
        and character not in digits
        and character not in extras
    ]


def counter(array: List[str]) -> dict:
    """Counts the number of times a character shows up in a list

    Args:
        array (List[str]): A list of characters

    Returns:
        dict: A dictionary of { character : number of occurences }
    """
    output = {}

    for index, character in enumerate(array):
        char = character

        if index < len(array) - 1 and array[index + 1] in "ei":
            if character in "cC":
                char = "ç"
            elif character in "gG":
                char = "ģ"

        if character in "şșŞȘ":
            char = "ş"

        if character in "ţțŢȚ":
            char = "ţ"

        if character in "îâÎÂ":
            char = "î"

        try:
            output[char] += 1
        except KeyError:
            output[char] = 1

    return output


def flatten(nested: List[List[Any]]) -> List[Any]:
    """Flattens a nested list

    Args:
        nested (List[List[Any]]): A nested list

    Returns:
        List[Any]: A flattened list
    """
    return [item for subl in nested for item in subl]


def main():
    """The main runner"""

    # The main index of works
    page_links = read_links_on_page(
        url=URL + "/carti",
        selector=".views-summary-unformatted a",
    )

    # The list of works for each letter
    links = flatten(
        [
            read_links_on_page(url=URL + item, selector="td.views-field a")
            for item in page_links
        ]
    )

    # The list of pages for each work
    pages = flatten(
        [
            read_links_on_page(url=URL + item, selector="#content ul.menu li.leaf a")
            for item in links
        ]
    )

    # This will be the output
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
        for key in count:
            try:
                output[key] += count[key]
            except KeyError:
                output[key] = count[key]

    # Sort the output by values rather than key
    output = dict(
        sorted(
            output.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    )

    # The program's output
    with open("output.json", mode="w", encoding="utf8") as file:
        dump(obj=output, fp=file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
