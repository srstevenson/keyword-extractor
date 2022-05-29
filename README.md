# keyword-extractor

[![Licence](https://img.shields.io/github/license/srstevenson/keyword-extractor?label=Licence&color=blue)](https://github.com/srstevenson/keyword-extractor/blob/main/LICENCE)
[![CI status](https://github.com/srstevenson/keyword-extractor/workflows/CI/badge.svg)](https://github.com/srstevenson/keyword-extractor/actions)
[![Coverage](https://img.shields.io/codecov/c/gh/srstevenson/keyword-extractor?label=Coverage)](https://app.codecov.io/gh/srstevenson/keyword-extractor)

A toy package for extracting keywords from plain text documents. Pre-processing
is carried out using [spaCy][spacy] (tokenisation, removal of stop words, and
lemmatisation) and keywords are selected by applying [tf-idf][tf-idf] over
sentences, using the implementation in [scikit-learn][scikit-learn].

## Usage

[Poetry][poetry] is used for packaging and dependency management. Install the
package and its dependencies with:

```bash
poetry install
```

You also need to download the language model used for pre-processing:

```bash
poetry run python3 -m spacy download en_core_web_sm
```

To check everything is working, run the linting, type checking, and unit testing
with [Nox][nox]:

```bash
poetry run nox
```

After entering the virtual environment in which the package is installed, you
can use the `keyword-extractor` executable to perform keyword extraction from a
document. You can specify multiple input documents as positional arguments, and
choose the number of keywords you want to be extracted with the `-n` flag.

```
$ poetry shell
$ keyword-extractor --help
usage: keyword-extractor [-h] [-n N] PATH [PATH ...]

positional arguments:
  PATH        Input document

optional arguments:
  -h, --help  show this help message and exit
  -n N        Number of keywords to extract (default: 5)
$ keyword-extractor example_doc.txt
╒═════════╤═══════════════╤═════════════════╤═══════════════════════════════════════════════════════════════════════╕
│ Word    │   Occurrences │ Documents       │ Sentences                                                             │
╞═════════╪═══════════════╪═════════════════╪═══════════════════════════════════════════════════════════════════════╡
│ na      │             3 │ example_doc.txt │ In reality, you're as dumb as they come and I needed those seeds real │
│         │               │                 │ bad, and I had to give them up just to get your parents off my back,  │
│         │               │                 │ so now we're gonna have to go get more adventures.                    │
│         │               │                 │                                                                       │
│         │               │                 │ And then we're gonna go on even more adventures after that, Morty and │
│         │               │                 │ you're gonna keep your mouth shut about it, Morty, because the world  │
│         │               │                 │ is full of idiots that don't understand what's important, and they'll │
│         │               │                 │ tear us apart, Morty but if you stick with me, I'm gonna accomplish   │
│         │               │                 │ great things, Morty, and you're gonna be part of them, and together,  │
│         │               │                 │ we're gonna run around, Morty.                                        │
│         │               │                 │                                                                       │
│         │               │                 │ We're gonna do all kinds of wonderful things, Morty.                  │
├─────────┼───────────────┼─────────────────┼───────────────────────────────────────────────────────────────────────┤
│ forever │             3 │ example_doc.txt │ Rick and Morty forever and forever.                                   │
│         │               │                 │                                                                       │
│         │               │                 │ All day long, forever.                                                │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty forever 100 times.                                     │
├─────────┼───────────────┼─────────────────┼───────────────────────────────────────────────────────────────────────┤
│ gon     │             3 │ example_doc.txt │ In reality, you're as dumb as they come and I needed those seeds real │
│         │               │                 │ bad, and I had to give them up just to get your parents off my back,  │
│         │               │                 │ so now we're gonna have to go get more adventures.                    │
│         │               │                 │                                                                       │
│         │               │                 │ And then we're gonna go on even more adventures after that, Morty and │
│         │               │                 │ you're gonna keep your mouth shut about it, Morty, because the world  │
│         │               │                 │ is full of idiots that don't understand what's important, and they'll │
│         │               │                 │ tear us apart, Morty but if you stick with me, I'm gonna accomplish   │
│         │               │                 │ great things, Morty, and you're gonna be part of them, and together,  │
│         │               │                 │ we're gonna run around, Morty.                                        │
│         │               │                 │                                                                       │
│         │               │                 │ We're gonna do all kinds of wonderful things, Morty.                  │
├─────────┼───────────────┼─────────────────┼───────────────────────────────────────────────────────────────────────┤
│ rick    │             5 │ example_doc.txt │ It's just Rick and Morty.                                             │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty and their adventures, Morty.                           │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty forever and forever.                                   │
│         │               │                 │                                                                       │
│         │               │                 │ Me and Rick and Morty running around, and Rick and Morty time.        │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty forever 100 times.                                     │
├─────────┼───────────────┼─────────────────┼───────────────────────────────────────────────────────────────────────┤
│ morty   │            12 │ example_doc.txt │ I'm sorry, Morty.                                                     │
│         │               │                 │                                                                       │
│         │               │                 │ And then we're gonna go on even more adventures after that, Morty and │
│         │               │                 │ you're gonna keep your mouth shut about it, Morty, because the world  │
│         │               │                 │ is full of idiots that don't understand what's important, and they'll │
│         │               │                 │ tear us apart, Morty but if you stick with me, I'm gonna accomplish   │
│         │               │                 │ great things, Morty, and you're gonna be part of them, and together,  │
│         │               │                 │ we're gonna run around, Morty.                                        │
│         │               │                 │                                                                       │
│         │               │                 │ We're gonna do all kinds of wonderful things, Morty.                  │
│         │               │                 │                                                                       │
│         │               │                 │ Just you and me, Morty.                                               │
│         │               │                 │                                                                       │
│         │               │                 │ The outside world is our enemy, Morty.                                │
│         │               │                 │                                                                       │
│         │               │                 │ We're the only friends we've got, Morty.                              │
│         │               │                 │                                                                       │
│         │               │                 │ It's just Rick and Morty.                                             │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty and their adventures, Morty.                           │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty forever and forever.                                   │
│         │               │                 │                                                                       │
│         │               │                 │ Morty's things.                                                       │
│         │               │                 │                                                                       │
│         │               │                 │ Me and Rick and Morty running around, and Rick and Morty time.        │
│         │               │                 │                                                                       │
│         │               │                 │ Rick and Morty forever 100 times.                                     │
╘═════════╧═══════════════╧═════════════════╧═══════════════════════════════════════════════════════════════════════╛
```

[nox]: https://nox.thea.codes/
[poetry]: https://python-poetry.org/
[scikit-learn]: https://scikit-learn.org/
[spacy]: https://spacy.io/
[tf-idf]: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
