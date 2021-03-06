acciobook
=========

`acciobook` scrapes Harry Potter audiobook files from [the web][web].

[web]: https://hpaudiobooks.club

Installation
------------

### pip

If you have [pipx][] installed, simply use

    pipx install acciobook

Otherwise, use pip with the `--user` flag:

    pip install --user acciobook

[pipx]: https://pipxproject.github.io/pipx/

### Poetry

Ensure [poetry][] is installed. Then run the following commands:

    git clone https://git.sr.ht/~gpanders/acciobook
    cd acciobook
    poetry install

Run using `poetry run acciobook`.

[poetry]: https://python-poetry.org/

Usage
-----

Usage is straightforward: simply run `acciobook` (or `poetry run acciobook` if
[installed from source](#poetry)). You will be asked to make selections
for which book to download, which narrator you prefer ([Stephen Fry][fry] or
[Jim Dale][dale]) and which chapters to download. The default settings are to
download all chapters of the book.

The files are downloaded as MP3 files to your current working directory.

[fry]: https://stephenfry.com/
[dale]: http://jim-dale.com/
