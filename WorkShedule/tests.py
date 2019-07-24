from django.test import TestCase

from selenium import webdriver
import time
import unittest

from WorkShedule.local_settings import password_user


class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome("/home/destro6984/OwnExcercise/Selenium/drivers/chromedriver.exe")

        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()

    def test_login(self):
        self.driver.get("http://127.0.0.1:8000/login/")

        self.driver.find_element_by_id("id_login").send_keys("tester1")
        self.driver.find_element_by_id("id_password").send_keys(password_user)
        self.driver.find_element_by_class_name("btn").click()

        self.driver.find_element_by_link_text("Logout").click()
        time.sleep(2)

    @classmethod
    def tearDown(cls):
        cls.driver.close()
        cls.driver.quit()
        print("Success")


if __name__ == "__main__":
    unittest.main()
