import os


def from_file(
    filename: str,
    /,
    *,
    separator: str = "=",
    symbol_comment: str = "#",
) -> None:
    with open(filename) as file:
        data = file.read()

    for line in data.splitlines():
        if not line.strip() or line.startswith(symbol_comment):
            continue

        key, value = line.split()[0].split(separator, 1)
        os.environ[key] = value


from_file(".env.template")
