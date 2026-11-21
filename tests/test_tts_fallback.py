import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generate_aibrief_vo as vo

NS = "{http://www.w3.org/2001/10/synthesis}"


class AzureSsmlTest(unittest.TestCase):
    def test_keeps_voice_rate_and_volume(self):
        root = ET.fromstring(vo.azure_ssml("Hello.", vo.CORRESPONDENT_VOICE, vo.RATE, "+15%"))
        voice = root.find(f"{NS}voice")
        prosody = voice.find(f"{NS}prosody")
        self.assertEqual(voice.get("name"), "en-US-AriaNeural")
        self.assertEqual(prosody.get("rate"), vo.RATE)
        self.assertEqual(prosody.get("volume"), "+15%")

    def test_escapes_script_text(self):
        text = 'AT&T says "<10%" of chips are idle'
        root = ET.fromstring(vo.azure_ssml(text, vo.LEAD_VOICE, vo.RATE, "+25%"))
        self.assertEqual(root.find(f"{NS}voice/{NS}prosody").text, text)


if __name__ == "__main__":
    unittest.main()
