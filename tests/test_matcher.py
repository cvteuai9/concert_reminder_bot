import unittest

from src.config import Artist
from src.matcher import match_events
from src.scrapers.base import Event


class MatchEventsTest(unittest.TestCase):
    def setUp(self):
        self.artists = [Artist(name="Bruno Mars", keywords=["Bruno Mars"])]

    def test_title_containing_keyword_matches(self):
        event = Event(
            source="tixcraft",
            id="1",
            title="Bruno Mars - The Romantic Tour",
            url="https://example.com/1",
        )
        matches = match_events(self.artists, [event])
        self.assertEqual(matches, [("Bruno Mars", event)])

    def test_title_without_keyword_does_not_match(self):
        event = Event(
            source="tixcraft",
            id="2",
            title="Disturbed - The Sickness",
            url="https://example.com/2",
        )
        matches = match_events(self.artists, [event])
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
