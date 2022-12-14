import unittest

from datetime import datetime
from digipics import digiimport


class TestSignalCheckers(unittest.TestCase):
    def test_signal1(self):
        filename = "signal-2022-06-06-214121.jpeg"
        output = digiimport.check_signal(filename)
        destname = output.strftime("%Y%m%d_%H%M%S")
        self.assertEqual(destname,"20220606_214121")

    def test_signal2(self):
        filename = "signal-2022-06-06-214121_001.jpeg"
        output = digiimport.check_signal(filename)
        destname = output.strftime("%Y%m%d_%H%M%S")
        self.assertEqual(destname,"20220606_214121")

    def test_signal3(self):
        filename = "xignal-2022-06-06-214121_001.jpeg"
        output = digiimport.check_signal(filename)
        self.assertIsNone(output)

class TestWhatsAppCheckers(unittest.TestCase):
    def test_wa1(self):
        filename = "WhatsApp Image 2017-01-11 at 13.41.31.jpeg"
        output = digiimport.check_whatsapp(filename)
        destname = output.strftime("%Y%m%d_%H%M%S")
        self.assertEqual(destname,"20170111_134131")

    def test_wa2(self):
        filename = "XhatsApp Image 2017-01-11 at 13.41.31.jpeg"
        output = digiimport.check_whatsapp(filename)
        self.assertIsNone(output)

class TestFileNameCheckers(unittest.TestCase):
    def test_filename1(self):
        filename = "20220830_120000.jpg"
        output = digiimport.check_filename(filename)
        destname = output.strftime("%Y%m%d_%H%M%S")
        self.assertEqual(destname,"20220830_120000")

    def test_filename2(self):
        filename = "foo_20220830_120000.jpg"
        output = digiimport.check_filename(filename)
        self.assertIsNone(output)



if __name__ == "__main__":
    unittest.main()