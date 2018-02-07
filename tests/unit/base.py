from mock import patch
from unittest import TestCase, SkipTest

from tornado.testing import AsyncTestCase

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
        return p.start()
    
class BaseAsyncTestCase(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        if cls is not BaseAsyncTestCase and cls.setUp is not BaseAsyncTestCase.setUp:
            orig_setUp = cls.setUp
            def setUpOverride(self, *args, **kwargs):
                BaseAsyncTestCase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

        if cls is BaseAsyncTestCase:
            raise SkipTest("Skip BaseAsyncTestCase tests, it's a base class")

        super(BaseAsyncTestCase, cls).setUpClass()

    def setUp(self):
        self.patches = []
        super(BaseAsyncTestCase, self).setUp()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        super(BaseAsyncTestCase, self).tearDown()
        
    def mock(self, path):
        p = patch(path)
        self.patches.append(p)
        return p.start()
