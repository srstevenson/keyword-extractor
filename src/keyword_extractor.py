import argparse
import pathlib
import sys
import textwrap
from collections.abc import Generator, Iterable
from dataclasses import dataclass, field

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from spacy.tokens.token import Token
from tabulate import tabulate


@dataclass(frozen=True)
class Document:
    """A document with a name and text content."""

    name: str
    text: str

    @classmethod
    def from_path(cls, path: pathlib.Path) -> "Document":
        """Construct a document from a plain text file on disk.

        Parameters
        ----------
        path : pathlib.Path
            Path to the plain text file.

        Returns
        -------
        Document
            The document read from disk.

        """
        text = path.read_text().replace("\n", " ").strip()
        return cls(path.name, text)


@dataclass
class KeywordMetadata:
    """Metadata for occurrences of an extracted keyword."""

    keyword: str
    occurrences: int = 0
    document_names: set[str] = field(default_factory=set)
    sentences: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KeywordSummary:
    """Summary of extracted keywords."""

    data: dict[str, KeywordMetadata]

    def __str__(self) -> str:
        """Return a formatted table containing the summary.

        Returns
        -------
        str
            Formatted table containing the summary.

        """
        sentences = []
        for metadata in self.data.values():
            sentences.append(
                "\n\n".join(
                    textwrap.fill(sentence) for sentence in metadata.sentences
                )
            )

        table = {
            "Word": [metadata.keyword for metadata in self.data.values()],
            "Occurrences": [
                metadata.occurrences for metadata in self.data.values()
            ],
            "Documents": [
                ", ".join(metadata.document_names)
                for metadata in self.data.values()
            ],
            "Sentences": sentences,
        }
        return tabulate(table, headers="keys", tablefmt="fancy_grid")


class KeywordExtractor:
    """Extract keywords from documents.

    Pre-processing is carried out using spaCy (tokenisation, removal of stop
    words, and lemmatisation) and keywords are selected by applying tf-idf over
    sentences, using the implementation in scikit-learn.

    """

    def __init__(self, n_keywords: int = 10) -> None:
        """Construct a keyword extractor.

        Parameters
        ----------
        n_keywords : int
            The number of keywords to extract (default 10).

        Returns
        -------
        None

        """
        self.language_model = spacy.load(
            "en_core_web_sm", disable=["tok2vec", "parser", "ner"]
        )
        self.language_model.add_pipe("sentencizer")
        self.tfidf = TfidfVectorizer(max_features=n_keywords)
        self.keywords: set[str] = set()

    @staticmethod
    def _lemmatise_and_remove_stops(
        text: Iterable[Token],
    ) -> Generator[str, None, None]:
        """Lemmatise tokens whilst dropping stop words and punctuation.

        Parameters
        ----------
        text : Iterable[Token]
            Tokens to lemmatise and drop stop words from.

        Yields
        ------
        str
            Lemmatised and lower cased form of token.

        """
        for token in text:
            if not token.is_stop and not token.is_punct:
                yield token.lemma_.lower()

    def fit(self, documents: Iterable[Document]) -> list[str]:
        """Fit the keyword extractor to documents.

        This finds the most prevalent keywords, applying tf-idf across
        sentences after lemmatising tokens and dropping stop words.

        Parameters
        ----------
        documents : Iterable[Document]
            Documents to fit keyword extractor to.

        Returns
        -------
        list[str]
            A list of the most prevalent keywords.

        """
        texts = (document.text for document in documents)
        lemmatised_sentences = (
            self._lemmatise_and_remove_stops(sentence)
            for document in self.language_model.pipe(texts)
            for sentence in document.sents
        )
        self.tfidf.fit(
            " ".join(token for token in sentence)
            for sentence in lemmatised_sentences
        )
        self.keywords.update(self.tfidf.get_feature_names_out())
        return list(self.keywords)

    def transform(self, documents: Iterable[Document]) -> KeywordSummary:
        """Extract keyword summary from new documents after fitting.

        This method extracts a keyword summary from a new corpus of documents,
        having previously fitted the extractor on a different corpus. This
        allows comparing the prevalence of the same keywords across two corpora
        of documents.

        Parameters
        ----------
        documents : Iterable[Document]
            Documents to extract keyword summary from.

        Returns
        -------
        KeywordSummary
            A summary of extracted keywords.

        """
        summary = {}
        for keyword in self.keywords:
            metadata = KeywordMetadata(keyword)
            for document in documents:
                for sentence in self.language_model(document.text).sents:
                    tokens = set(self._lemmatise_and_remove_stops(sentence))
                    if keyword not in tokens:
                        continue
                    metadata.occurrences += 1
                    metadata.document_names.add(document.name)
                    metadata.sentences.append(sentence.text)
            summary[keyword] = metadata
        return KeywordSummary(summary)

    def fit_transform(self, documents: Iterable[Document]) -> KeywordSummary:
        """Fit to and extract keywords from a single corpus of documents.

        This method fits the most common keywords on a corpus of documents, and
        extracts a summary of the keyword prevalence from that same corpus of
        documents.

        Parameters
        ----------
        documents : Iterable[Document]
            Documents to fit keyword extractor to and extract keyword summary
            from.

        Returns
        -------
        KeywordSummary
            A summary of extracted keywords.

        """
        self.fit(documents)
        return self.transform(documents)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Parameters
    ----------
    argv : list[str]
        Command line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.

    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-n",
        default=5,
        type=int,
        help="Number of keywords to extract",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        type=pathlib.Path,
        help="Input document",
    )
    return parser.parse_args(argv)


def main() -> None:  # pragma: no cover
    """Command line entry point."""
    args = parse_args(sys.argv[1:])
    documents = [Document.from_path(path) for path in args.paths]
    extractor = KeywordExtractor(n_keywords=args.n)
    summary = extractor.fit_transform(documents)
    print(summary)


if __name__ == "__main__":  # pragma: no cover
    main()
