import unittest


class TestMeta(unittest.TestCase):
    def test_version_defined(self):
        """
        Ensure __version__ is defined in the stream_tap module.

        Ensure __version_info__ is defined in the stream_tap module.

        """
        from stream_tap import __version__
        from stream_tap import __version_info__
        self.assertTrue(__version__)
        self.assertTrue(__version_info__)
