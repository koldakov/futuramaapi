def to_camel(val: str, /) -> str:
    return "".join([word if idx == 0 else word.capitalize() for idx, word in enumerate(val.lower().split("_"))])
