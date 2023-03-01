import sys

import sqlite3

from PyQt5.QtWidgets import QApplication, QWidget

import main

from start_design import Ui_start_window


class Start(QWidget, Ui_start_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.wnd = main.Library(self)

    def initUI(self):
        self.swap_btn_1.clicked.connect(lambda:(self.pages.setCurrentIndex(1),self.login_field_1.setText(""),self.reg_password_field.setText(""),self.reg_password_confirm_field.setText("")))
        self.swap_btn_2.clicked.connect(lambda:(self.pages.setCurrentIndex(0),self.login_field_2.setText(""),self.log_password_field.setText("")))
        self.reg_btn.clicked.connect(self.registration)
        self.log_btn.clicked.connect(lambda:self.login(self.login_field_2.text(), self.log_password_field.text()))


    def registration(self):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        if self.login_field_1.text() == "":
            print("Пожалуйста, заполните поле логина")
        elif list(cur.execute("""SELECT a.login FROM accinf AS a
        WHERE a.login IN ("{}")""".format(self.login_field_1.text()))):
            print("Аккаунт с данным логином уже существует")
        elif self.reg_password_field.text() == "" or self.reg_password_confirm_field.text() == "":
            print("Пожалуйста, заполните поля пароля")
        elif len(self.reg_password_field.text()) < 8:
            print("Длина пароля должна быть больше 8 символов")
        elif self.reg_password_field.text() != self.reg_password_confirm_field.text():
            print("Пароли не совпадают")
        else:
            cur.execute("""INSERT INTO accinf ("login", "password")
            VALUES ("{}", "{}")""".format(self.login_field_1.text(), self.reg_password_field.text()))
            con.commit()

            con.close()

            self.login(self.login_field_1.text(), self.reg_password_field.text())

    def login(self, lg, pw):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        res = list(cur.execute("""SELECT a.password FROM accinf AS a
        WHERE a.login IN ("{}")""".format(lg)))

        con.close()

        if lg == "":
            print("Пожалуйста, заполните поле логина")
        elif pw == "":
            print("Пожалуйста, заполните поля пароля")
        elif res == []:
            print("Данного логина не существует")
        elif str(res[0][0]) != str(pw):
            print("Неверный пароль")
        else:
            print("Успешный вход")
            self.hide()

            self.wnd.user = lg
            self.wnd.lib_go()
            self.wnd.show()
            if self.wnd.user != "ADMIN":
                self.wnd.to_add_book_btn.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec())