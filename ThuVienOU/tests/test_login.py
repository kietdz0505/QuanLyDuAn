import unittest
from libraryapp import dao

class TestLogin(unittest.TestCase):
    def test_1(self):
        self.assertTrue(dao.auth_user("user",123))

    def test_2(self):
        self.assertFalse(dao.auth_user("admin",123))

if __name__=="__main__":
    unittest.main()