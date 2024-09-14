from bs4 import BeautifulSoup


def html_to_plain_text_with_links(html):
    soup = BeautifulSoup(html, "html.parser")

    # Replace links with `link_text (url)`
    for tag in soup.find_all("a"):
        tag.replace_with(f"{tag.text} ({tag.get('href')})")

    # Add empty lines after <p>, </div>, and <br>. Not using the `separator`
    # parameter, as it would apply to other inline tags like <span>.
    for tag in soup.find_all(["p", "div", "br"]):
        tag.insert_after("\n")

    text = soup.get_text()
    # Remove empty spaces at the beginning of lines
    text = "\n".join([line.lstrip() for line in text.split("\n")])

    return text
