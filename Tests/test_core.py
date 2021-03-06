# Import dependencies
from Songs2Slides import core, config
import unittest
from unittest.mock import patch



class TestCore(unittest.TestCase):
    # Test GetLyrics method on cached songs
    def test_GetLyrics_cache(self):
        # Set cached songs
        config.cachedSongs = {
            "test-artist-test-song": {
                "title": "Test Song",
                "artist": "Test Artist",
                "lyrics":"test1\ntest2\n\ntest3\ntest4"
            }
        }

        # Test cached song
        lyrics, title, artist = core.GetLyrics("tEsT sOnG", "tEsT aRtIsT")
        self.assertEqual(lyrics, "test1\ntest2\n\ntest3\ntest4")
        self.assertEqual(title, "Test Song")
        self.assertEqual(artist, "Test Artist")



    # Test GetLyrics method on songs on the internet
    def test_GetLyrics_web(self):
        with patch('Songs2Slides.core.requests.get') as mocked_get:
            # Initialize mocked_get
            mocked_get.return_value.text = b"<!DOCTYPE html><html><head></head><body><h1 class=\"header_with_cover_art-primary_info-title\">Test Song 2</h1><h2><a class=\"header_with_cover_art-primary_info-primary_artist\">Test Artist</a></h2><div class=\"lyrics\"><p><br>\n<br>\n[Verse 1]<br>\nTest1<br>\nTest2<br>\nTest3<br>\nTest4<br>\nTest5<br>\n<br>\n[Verse 2]<br>\nTest10<br>\nTest20<br>\nTest30<br>\nTest40<br>\nTest50<br>\n<br>\n</p></div></body></html>"
            
            # Get song lyrics
            lyrics, title, artist = core.GetLyrics("tEsT sOnG 2", "tEsT aRtIsT")

            # Validate responce
            mocked_get.assert_called_with("https://genius.com/test-artist-test-song-2-lyrics")
            self.assertEqual(lyrics, "[Verse 1]\nTest1\nTest2\nTest3\nTest4\nTest5\n\n[Verse 2]\nTest10\nTest20\nTest30\nTest40\nTest50")
            self.assertEqual(title, "Test Song 2")
            self.assertEqual(artist, "Test Artist")
    


    # Test ParseLyrics method
    def test_ParseLyrics(self):
        # Initialize settings
        settings = {
            "title-slides": True,
            "slide-between-songs": True,
            "lines-per-slide": 4,
            "remove-parentheses": False,
        }

        # Mock core.getLyrics method
        with patch('Songs2Slides.core.GetLyrics') as mocked_get:
            # Initialize mocked_get
            mocked_get.return_value = ("[Verse 1]\nTest1\nTest2\nTest3\nTest4\nTest5 (Test5)\n\n[Verse 2]\nTest10\nTest20\nTest30\nTest40\nTest50(Test50)", "Test Song", "Test Artist")
            
            # Test parser
            lyrics = core.ParseLyrics("tEsT sOnG 2", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test Song\nTest Artist", "Test1\nTest2\nTest3\nTest4", "Test5 (Test5)", "Test10\nTest20\nTest30\nTest40", "Test50(Test50)", ""])
            mocked_get.assert_called_with("tEsT sOnG 2", "tEsT aRtIsT")
        
            # Test parser without title slide
            settings["title-slides"] = False
            lyrics = core.ParseLyrics("tEsT sOnG", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test1\nTest2\nTest3\nTest4", "Test5 (Test5)", "Test10\nTest20\nTest30\nTest40", "Test50(Test50)", ""])
        
            # Test parser without slide at end
            settings["slide-between-songs"] = False
            lyrics = core.ParseLyrics("tEsT sOnG", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test1\nTest2\nTest3\nTest4", "Test5 (Test5)", "Test10\nTest20\nTest30\nTest40", "Test50(Test50)"])
        
            # Test parser with 3 lines per slide
            settings["lines-per-slide"] = 3
            lyrics = core.ParseLyrics("tEsT sOnG", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test1\nTest2\nTest3", "Test4\nTest5 (Test5)", "Test10\nTest20\nTest30", "Test40\nTest50(Test50)"])
            
            # Test parser with parentheses remover
            settings["remove-parentheses"] = True
            lyrics = core.ParseLyrics("tEsT sOnG 2", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test1\nTest2\nTest3", "Test4\nTest5", "Test10\nTest20\nTest30", "Test40\nTest50"])
            
            # Test parser with blank line
            mocked_get.return_value = ("[Verse 1]\nTest1\n\n[Instrumental]\n\n[Verse 2]\nTest2", "Test Song", "Test Artist")
            lyrics = core.ParseLyrics("tEsT sOnG 2", "tEsT aRtIsT", settings)
            self.assertEqual(lyrics, ["Test1", "", "Test2"])
