import bleach
import markdown

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    "h1",
    "h2",
    "h3",
    "h4",
    "p",
    "pre",
    "code",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "blockquote",
    "hr",
    "a",
}

ALLOWED_ATTRIBUTES = {
    "a": [
        "href",
        "title",
    ],
}

ALLOWED_PROTOCOLS = {
    "http",
    "https",
    "mailto",
}


def render_markdown(md: str, /) -> str:
    html = markdown.markdown(
        md,
        extensions=[
            "extra",
            "fenced_code",
            "toc",
        ],
        output_format="html",
    )

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
