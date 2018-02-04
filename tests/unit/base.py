from mock import patch
from unittest import TestCase, SkipTest

class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        if cls is not BaseTestCase and cls.setUp is not BaseTestCase.setUp:
            orig_setUp = cls.setUp
            def setUpOverride(self, *args, **kwargs):
                BaseTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

        if cls is BaseTestCase:
            raise SkipTest("Skip BaseTestCase tests, it's a base class")

        super(BaseTestCase, cls).setUpClass()

    def setUp(self):
        self.patches = []

    def tearDown(self):
        for p in self.patches:
            p.stop()
        
    def mock(self, path):
        p = patch(path)
        self.patches.append(p)