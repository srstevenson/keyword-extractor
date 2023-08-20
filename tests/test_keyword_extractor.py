import pathlib
import textwrap
from collections.abc import Iterable

import pytest

from keyword_extractor import (
    Document,
    KeywordExtractor,
    KeywordMetadata,
    KeywordSummary,
    parse_args,
)

TEST_DOCUMENT_NAME = "pilot_transcript.txt"
TEST_DOCUMENTS = [
    Document(
        TEST_DOCUMENT_NAME,
        textwrap.dedent(
            """
            I'm sorry, Morty. It's a bummer. In reality, you're as dumb as they
            come and I needed those seeds real bad, and I had to give them up
            just to get your parents off my back, so now we're gonna have to go
            get more adventures. And then we're gonna go on even more
            adventures after that, Morty and you're gonna keep your mouth shut
            about it, Morty, because the world is full of idiots that don't
            understand what's important, and they'll tear us apart, Morty but
            if you stick with me, I'm gonna accomplish great things, Morty, and
            you're gonna be part of them, and together, we're gonna run around,
            Morty. We're gonna do all kinds of wonderful things, Morty. Just
            you and me, Morty. The outside world is our enemy, Morty. We're the
            only friends we've got, Morty. It's just Rick and Morty. Rick and
            Morty and their adventures, Morty. Rick and Morty forever and
            forever. Morty's things. Me and Rick and Morty running around, and
            Rick and Morty time. All day long, forever. All a hundred days.
            Rick and Morty forever 100 times. Over and over,
            rickandmortyadventures.com. All 100 years. Every minute,
            rickandmorty.com.
            """
        ),
    )
]


def test_document_from_path() -> None:
    """Test parsing a document from a path."""
    path = pathlib.Path(__file__).parent / "data" / "tongue_twister.txt"
    document = Document.from_path(path)
    assert document.name == "tongue_twister.txt"
    assert document.text == "She sells sea shells on the sea shore."


@pytest.mark.parametrize(
    ("n_keywords_arg", "n_keywords_attr"), [(None, 10), (5, 5)]
)
def test_keyword_extractor_init(
    n_keywords_arg: int | None, n_keywords_attr: int
) -> None:
    """Test KeywordExtractor.__init__."""
    if n_keywords_arg is not None:
        extractor = KeywordExtractor(n_keywords=n_keywords_arg)
    else:
        extractor = KeywordExtractor()

    params = extractor.tfidf.get_params()
    assert params.get("max_features") == n_keywords_attr


def test_keyword_extractor_fit() -> None:
    """Test KeywordExtractor.fit."""
    extractor = KeywordExtractor(n_keywords=5)
    keywords = set(extractor.fit(TEST_DOCUMENTS))
    for word in ("rick", "morty", "forever"):
        assert word in keywords


def test_keyword_extractor_transform() -> None:
    """Test KeywordExtractor.transform."""
    extractor = KeywordExtractor(n_keywords=5)
    keywords = set(extractor.fit(TEST_DOCUMENTS))
    summary = extractor.transform(TEST_DOCUMENTS)
    for keyword in keywords:
        assert keyword in summary.data

    assert "rick" in summary.data
    summary_rick = summary.data["rick"]
    assert summary_rick.keyword == "rick"
    assert summary_rick.occurrences == 5
    assert summary_rick.document_names == {TEST_DOCUMENT_NAME}
    assert len(summary_rick.sentences) == 5

    assert "forever" in summary.data
    summary_forever = summary.data["forever"]
    assert summary_forever.keyword == "forever"
    assert summary_forever.occurrences == 3
    assert summary_forever.document_names == {TEST_DOCUMENT_NAME}
    assert len(summary_forever.sentences) == 3


def test_keyword_extractor_fit_transform() -> None:
    """Test KeywordExtractor.fit_transform."""
    extractor = KeywordExtractor(n_keywords=5)
    summary = extractor.fit_transform(TEST_DOCUMENTS)

    assert "rick" in summary.data
    summary_rick = summary.data["rick"]
    assert summary_rick.keyword == "rick"
    assert summary_rick.occurrences == 5
    assert summary_rick.document_names == {TEST_DOCUMENT_NAME}
    assert len(summary_rick.sentences) == 5

    assert "forever" in summary.data
    summary_forever = summary.data["forever"]
    assert summary_forever.keyword == "forever"
    assert summary_forever.occurrences == 3
    assert summary_forever.document_names == {TEST_DOCUMENT_NAME}
    assert len(summary_forever.sentences) == 3


def test_keyword_summary() -> None:
    """Test KeywordSummary."""
    data = {
        "keyword": KeywordMetadata(
            "keyword",
            2,
            {"doc.txt"},
            ["this contains keyword", "keyword is here too"],
        )
    }
    summary = KeywordSummary(data)

    expected = textwrap.dedent(
        """
        ╒═════════╤═══════════════╤═════════════╤═══════════════════════╕
        │ Word    │   Occurrences │ Documents   │ Sentences             │
        ╞═════════╪═══════════════╪═════════════╪═══════════════════════╡
        │ keyword │             2 │ doc.txt     │ this contains keyword │
        │         │               │             │                       │
        │         │               │             │ keyword is here too   │
        ╘═════════╧═══════════════╧═════════════╧═══════════════════════╛
        """
    ).strip()
    assert str(summary) == expected


@pytest.mark.parametrize(
    ("argv", "n_keywords", "paths"),
    [
        ("foo.txt", 5, ["foo.txt"]),
        ("-n 3 foo.txt bar.txt", 3, "foo.txt bar.txt".split()),
    ],
)
def test_parse_args(argv: str, n_keywords: int, paths: Iterable[str]) -> None:
    """Test parse_args."""
    args = parse_args(argv.split())
    assert args.n == n_keywords
    assert args.paths == [pathlib.Path(path) for path in paths]
