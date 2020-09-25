accio
=====

`accio` scrapes Harry Potter audiobook files from [the web][web].

[web]: https://hpaudiobooks.club

Installation
------------

### pip

    pip install --user accio

### From source

Ensure [poetry][] is installed. Then run the following commands:

    git clone https://git.sr.ht/~gpanders/accio
    cd accio
    poetry install
    poetry run accio

[poetry]: https://python-poetry.org/

Usage
-----

Usage is straightforward. Simply run `accio` (or `poetry run accio` if
[installed from source](#from-source)). You will be asked to make selections
for which book to download, which narrator you prefer ([Stephen Fry][fry] or
[Jim Dale][dale]) and which chapters to download. The default settings are to
download all chapters of the book.

The files are downloaded as MP3 files to your current working directory.

[fry]: https://stephenfry.com/
[dale]: http://jim-dale.com/
