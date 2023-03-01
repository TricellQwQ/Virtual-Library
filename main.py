import sqlite3

import sys

from PyQt5.QtGui import QBrush, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog

from os import mkdir

from shutil import copy

from PIL import Image

from lib_design import Ui_lib_window


class Library(QMainWindow, Ui_lib_window):
    def __init__(self, *args):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.to_lib_btn_1.clicked.connect(self.lib_go)
        self.to_lib_btn_2.clicked.connect(self.lib_go)
        self.to_book_btn.clicked.connect(self.owned_go)
        self.return_btn.clicked.connect(self.ret)
        self.get_btn.clicked.connect(self.get)
        self.download_btn.clicked.connect(self.download)
        self.to_add_book_btn.clicked.connect(self.add_go)
        self.choose_pic_btn.clicked.connect(self.picture)
        self.choose_text_btn.clicked.connect(self.text)
        self.add_btn.clicked.connect(self.add)

    def add(self):
        con = sqlite3.connect("books")

        cur = con.cursor()

        books = list(cur.execute("""SELECT b.name FROM books AS b"""))

        if self.name_field.text() == "":
            print("Заполните имя книги")
        elif self.name_field.text() in books:
            print("Книга с таким именем уже существует")
        elif self.pic_file.text() == "(filename.jpg)":
            print("Выберите изображение для книги")
        elif self.text_file.text() == "(filename.txt)":
            print("Выберите текст для книги")
        else:
            cur.execute("""INSERT INTO books ("name")
            VALUES ("{}")""".format(self.name_field.text()))

            mkdir("book_files/{}".format(self.name_field.text()))
            copy(self.pic_file.text(), "book_files/{}/{}.jpg".format(self.name_field.text(), self.name_field.text()))
            copy(self.text_file.text(), "book_files/{}/{}.txt".format(self.name_field.text(), self.name_field.text()))

        con.commit()

        con.close()

    def text(self):
        file = QFileDialog.getOpenFileName(None, "Choose text (.txt)", "", "Text files (*.txt)")
        if file[0] != "":
            self.text_file.setText(file[0])

    def picture(self):
        file = QFileDialog.getOpenFileName(None, "Choose picture (.png)", "", "Image files (*.jpg)")
        if file[0] != "":
            pixmap = QPixmap(file[0])
            self.pic_show.setPixmap(pixmap)
            self.pic_file.setText(file[0])

    def download(self):
        with open("book_files/{}/{}.txt".format(self.book_name.text(), self.book_name.text()), mode="rt") as inp:
            directory = QFileDialog.getExistingDirectory(self, "Choose a directory")
            if directory:
                lines = inp.readlines()
                out = open("{}/{}.txt".format(directory, self.book_name.text()), mode="wt")
                print("".join(lines), file=out)

    def get(self):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        book = list(cur.execute("""SELECT a.book FROM accinf AS a
        WHERE a.login = '{}'""".format(self.user)))[0][0]

        if book is None:
            cur.execute("""UPDATE accinf
            SET book = '{}'
            WHERE login = '{}'""".format(self.books_widget.selectedItems()[0].text(), self.user))
            self.get_btn.setEnabled(False)
            self.return_btn.setEnabled(True)
        else:
            print("You already have a book")

        con.commit()

        con.close()

    def ret(self):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        cur.execute("""UPDATE accinf
        SET book = NULL
        WHERE book = '{}'""".format(self.books_widget.selectedItems()[0].text()))

        con.commit()

        con.close()

        self.get_btn.setEnabled(True)
        self.return_btn.setEnabled(False)

    def book(self):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        user_book = list(cur.execute("""SELECT a.book FROM accinf AS a
        WHERE a.login = '{}'""".format(self.user)))[0][0]

        con.close()

        if len(self.sender().selectedItems()) != 0:
            book = self.sender().selectedItems()[0].text()

            if book == user_book:
                self.return_btn.setEnabled(True)
                self.get_btn.setEnabled(False)
            else:
                self.return_btn.setEnabled(False)
                self.get_btn.setEnabled(True)
        else:
            self.return_btn.setEnabled(False)
            self.get_btn.setEnabled(False)

    def lib_go(self):
        self.book_text.setText("")
        self.return_btn.setEnabled(False)
        self.get_btn.setEnabled(False)
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        exept_books = list(cur.execute("""SELECT a.book FROM accinf AS a
        WHERE a.login NOT IN ("{}")""".format(self.user)))

        con.close()

        con = sqlite3.connect("books")

        cur = con.cursor()

        books = sorted(list(cur.execute("""SELECT b.name FROM books AS b""")))

        con.close()

        enabled_books = []

        for book in books:
            if book not in exept_books:
                enabled_books.append(book)

        for i in range(len(enabled_books)):
            row = i // 4
            col = i % 4
            brush = QBrush()
            img = Image.open("book_files\{}\{}.jpg".format(enabled_books[i][0], enabled_books[i][0]))
            width = 172
            height = 200
            resized_img = img.resize((width, height), Image.ANTIALIAS)
            resized_img.save("book_files\{}\{}.jpg".format(enabled_books[i][0], enabled_books[i][0]))
            brush.setTextureImage(QImage("book_files\{}\{}.jpg".format(enabled_books[i][0], enabled_books[i][0])))
            book = QTableWidgetItem(enabled_books[i][0])
            book.setBackground(brush)
            self.books_widget.setItem(row, col, book)
            self.books_widget.itemSelectionChanged.connect(lambda:self.book())
        self.pages.setCurrentIndex(1)

    def owned_go(self):
        con = sqlite3.connect("accounts")

        cur = con.cursor()

        book = list(cur.execute("""SELECT a.book FROM accinf AS a
        WHERE a.login = '{}'""".format(self.user)))[0][0]

        con.close()

        if book is None:
            self.book_name.setText("You have no owned book :(")
            self.download_btn.setEnabled(False)
        else:
            self.book_name.setText(book)
            f = open("book_files/{}/{}.txt".format(book, book))
            self.book_text.setText("".join(f.readlines()))
            self.download_btn.setEnabled(True)
        self.pages.setCurrentIndex(2)

    def add_go(self):
        self.pages.setCurrentIndex(0)
        self.name_field.setText("")
        self.pic_show.setPixmap(QPixmap())
        self.pic_file.setText("(filename.jpg)")
        self.text_file.setText("(filename.txt)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Library()
    ex.show()
    sys.exit(app.exec())