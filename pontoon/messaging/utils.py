import html2text


def html_to_plain_text_with_links(html):
    h = html2text.HTML2Text()

    h.wrap_links = False
    h.body_width = 0

    return h.handle(html)
