from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QMessageBox, QComboBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QInputDialog, QHBoxLayout, QTableWidgetItem
)
from PyQt6.QtCore import Qt
import sqlite3
import sys

# База данных
def init_db():
    conn = sqlite3.connect("school_system.db")
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            class_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT,
            day TEXT,
            subject TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT,
            student_name TEXT,
            subject TEXT,
            grade INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Главное окно
class SchoolManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления учебным процессом")
        self.setGeometry(100, 100, 1000, 700)

        self.conn = sqlite3.connect("school_system.db")
        self.cursor = self.conn.cursor()

        self.init_ui()

    def init_ui(self):
        self.login_widget = LoginWidget(self)
        self.setCentralWidget(self.login_widget)

    def switch_to_teacher_dashboard(self, username):
        self.teacher_dashboard = TeacherDashboard(self, username)
        self.setCentralWidget(self.teacher_dashboard)

    def switch_to_student_dashboard(self, username):
        self.student_dashboard = StudentDashboard(self, username)
        self.setCentralWidget(self.student_dashboard)

# Авторизация и регистрация
class LoginWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_label = QLabel("Роль:")
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(["Учитель", "Ученик"])

        self.login_button = QPushButton("Войти")
        self.register_button = QPushButton("Регистрация")

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.role_label)
        layout.addWidget(self.role_combobox)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combobox.currentText()

        query = "SELECT * FROM users WHERE username = ? AND password = ? AND role = ?"
        self.main_window.cursor.execute(query, (username, password, role))
        user = self.main_window.cursor.fetchone()

        if user:
            if role == "Учитель":
                self.main_window.switch_to_teacher_dashboard(username)
            elif role == "Ученик":
                self.main_window.switch_to_student_dashboard(username)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные данные для входа!")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combobox.currentText()

        if role == "Ученик":
            self.main_window.cursor.execute("SELECT name FROM classes")
            classes = [c[0] for c in self.main_window.cursor.fetchall()]
            if not classes:
                QMessageBox.warning(self, "Ошибка", "Сначала нужно создать классы!")
                return

            class_name, ok = QInputDialog.getItem(self, "Выберите класс", "Класс:", classes, 0, False)
            if not ok:
                return
        else:
            class_name = None

        try:
            query = "INSERT INTO users (username, password, role, class_name) VALUES (?, ?, ?, ?)"
            self.main_window.cursor.execute(query, (username, password, role, class_name))
            self.main_window.conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя уже занято!")


# Панель учителя



class TeacherDashboard(QWidget):
    def __init__(self, main_window, username):
        super().__init__()
        self.main_window = main_window
        self.username = username
        layout = QVBoxLayout()

        self.create_class_button = QPushButton("Создать класс")
        self.add_schedule_button = QPushButton("Добавить расписание")
        self.create_diary_button = QPushButton("Создать дневник")
        self.open_diary_button = QPushButton("Открыть дневник")
        self.logout_button = QPushButton("Выйти")

        layout.addWidget(self.create_class_button)
        layout.addWidget(self.add_schedule_button)
        layout.addWidget(self.create_diary_button)
        layout.addWidget(self.open_diary_button)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

        self.create_class_button.clicked.connect(self.create_class)
        self.add_schedule_button.clicked.connect(self.add_schedule)
        self.create_diary_button.clicked.connect(self.create_diary)
        self.open_diary_button.clicked.connect(self.open_diary)
        self.logout_button.clicked.connect(self.logout)



    def create_class(self):
        class_name, ok = QInputDialog.getText(self, "Создание класса", "Введите название класса:")
        if ok and class_name:
            try:
                query = "INSERT INTO classes (name) VALUES (?)"
                self.main_window.cursor.execute(query, (class_name,))
                self.main_window.conn.commit()
                QMessageBox.information(self, "Успех", f"Класс {class_name} создан!")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", "Класс с таким названием уже существует!")

    def view_classes(self):
        self.main_window.cursor.execute("SELECT * FROM classes")
        classes = self.main_window.cursor.fetchall()
        if classes:
            class_list = "\n".join([f"{c[0]}. {c[1]}" for c in classes])
            QMessageBox.information(self, "Список классов", class_list)
        else:
            QMessageBox.information(self, "Список классов", "Нет созданных классов.")

    def add_schedule(self):
        self.main_window.cursor.execute("SELECT name FROM classes")
        classes = [c[0] for c in self.main_window.cursor.fetchall()]
        if not classes:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте класс.")
            return

        class_name, ok = QInputDialog.getItem(self, "Добавить расписание", "Выберите класс:", classes, 0, False)
        if not ok:
            return

        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        day, ok = QInputDialog.getItem(self, "Выберите день", "День недели:", days, 0, False)
        if not ok:
            return

        subject, ok = QInputDialog.getText(self, "Добавить предмет", "Введите предмет:")
        if ok and subject:
            self.main_window.cursor.execute(
                "INSERT INTO schedule (class_name, day, subject) VALUES (?, ?, ?)",
                (class_name, day, subject)
            )
            self.main_window.conn.commit()
            QMessageBox.information(self, "Успех", "Расписание успешно добавлено!")

    def create_diary(self):
        # Получение списка классов
        self.main_window.cursor.execute("SELECT name FROM classes")
        classes = [c[0] for c in self.main_window.cursor.fetchall()]
        if not classes:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте класс!")
            return

        # Выбор класса
        class_name, ok = QInputDialog.getItem(self, "Создание дневника", "Выберите класс:", classes, 0, False)
        if not ok:
            return

        # Получение списка учеников этого класса
        self.main_window.cursor.execute("SELECT username FROM users WHERE class_name = ?", (class_name,))
        students = [s[0] for s in self.main_window.cursor.fetchall()]
        if not students:
            QMessageBox.warning(self, "Ошибка", "В этом классе пока нет учеников!")
            return

        # Ввод предметов
        subjects, ok = QInputDialog.getText(self, "Добавить предметы", "Введите названия предметов через запятую:")
        if not ok or not subjects:
            return
        subjects = [s.strip() for s in subjects.split(",")]

        # Сохранение дневника в базу данных
        for subject in subjects:
            for student in students:
                self.main_window.cursor.execute(
                    "INSERT OR IGNORE INTO grades (class_name, student_name, subject, grade) VALUES (?, ?, ?, ?)",
                    (class_name, student, subject, None)
                )
        self.main_window.conn.commit()
        QMessageBox.information(self, "Успех",
                                f"Дневник для класса {class_name} создан с предметами: {', '.join(subjects)}")

    def open_diary(self):
        self.main_window.cursor.execute("SELECT name FROM classes")
        classes = [c[0] for c in self.main_window.cursor.fetchall()]
        if not classes:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте класс!")
            return

        class_name, ok = QInputDialog.getItem(self, "Открыть дневник", "Выберите класс:", classes, 0, False)
        if not ok:
            return

        self.main_window.cursor.execute("SELECT DISTINCT student_name FROM grades WHERE class_name = ?", (class_name,))
        students = [s[0] for s in self.main_window.cursor.fetchall()]

        self.main_window.cursor.execute("SELECT DISTINCT subject FROM grades WHERE class_name = ?", (class_name,))
        subjects = [s[0] for s in self.main_window.cursor.fetchall()]

        if not students or not subjects:
            QMessageBox.warning(self, "Ошибка", "Для этого класса нет дневника!")
            return

        # Создание окна дневника
        self.diary_window = QWidget()
        self.diary_window.setWindowTitle(f"Дневник: {class_name}")
        layout = QVBoxLayout()

        # Таблица с данными
        self.diary_table = QTableWidget()
        self.diary_table.setRowCount(len(students))
        self.diary_table.setColumnCount(len(subjects))
        self.diary_table.setHorizontalHeaderLabels(subjects)
        self.diary_table.setVerticalHeaderLabels(students)

        for row, student in enumerate(students):
            for col, subject in enumerate(subjects):
                self.main_window.cursor.execute(
                    "SELECT grade FROM grades WHERE class_name = ? AND student_name = ? AND subject = ?",
                    (class_name, student, subject)
                )
                grade = self.main_window.cursor.fetchone()
                grade = grade[0] if grade else None
                self.diary_table.setItem(row, col, QTableWidgetItem(str(grade) if grade else ""))

        layout.addWidget(self.diary_table)

        # Кнопки управления
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить изменения")
        delete_button = QPushButton("Удалить дневник")
        button_layout.addWidget(save_button)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        self.diary_window.setLayout(layout)
        self.diary_window.show()

        # Сохранение оценок
        save_button.clicked.connect(lambda: self.save_grades(class_name, students, subjects))

        # Удаление дневника
        delete_button.clicked.connect(lambda: self.delete_diary(class_name))

    def save_grades(self, class_name, students, subjects):
        for row in range(self.diary_table.rowCount()):
            student_name = students[row]
            for col in range(self.diary_table.columnCount()):
                subject = subjects[col]
                grade_item = self.diary_table.item(row, col)
                grade = int(grade_item.text()) if grade_item and grade_item.text().isdigit() else None

                if grade is not None:
                    self.main_window.cursor.execute(
                        "INSERT OR REPLACE INTO grades (class_name, student_name, subject, grade) VALUES (?, ?, ?, ?)",
                        (class_name, student_name, subject, grade)
                    )
        self.main_window.conn.commit()
        QMessageBox.information(self, "Успех", "Изменения сохранены!")

    def delete_diary(self, class_name):
        reply = QMessageBox.question(
            self, "Подтверждение", f"Вы уверены, что хотите удалить дневник класса {class_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.cursor.execute("DELETE FROM grades WHERE class_name = ?", (class_name,))
            self.main_window.conn.commit()
            QMessageBox.information(self, "Успех", f"Дневник класса {class_name} удален!")
            self.diary_window.close()

    def logout(self):
        self.main_window.init_ui()


# Панель ученика
class StudentDashboard(QWidget):
        def __init__(self, main_window, username):
            super().__init__()
            self.main_window = main_window
            self.username = username

            layout = QVBoxLayout()
            self.view_schedule_button = QPushButton("Посмотреть расписание")
            self.view_grades_button = QPushButton("Посмотреть оценки")
            self.logout_button = QPushButton("Выйти")

            layout.addWidget(self.view_schedule_button)
            layout.addWidget(self.view_grades_button)
            layout.addWidget(self.logout_button)

            self.setLayout(layout)

            self.view_schedule_button.clicked.connect(self.view_schedule)
            self.view_grades_button.clicked.connect(self.view_grades)
            self.logout_button.clicked.connect(self.logout)

        def view_schedule(self):
            self.main_window.cursor.execute("SELECT class_name FROM users WHERE username = ?", (self.username,))
            class_name = self.main_window.cursor.fetchone()[0]

            self.main_window.cursor.execute("SELECT day, subject FROM schedule WHERE class_name = ?", (class_name,))
            schedule = self.main_window.cursor.fetchall()

            if schedule:
                schedule_text = "\n".join([f"{day}: {subject}" for day, subject in schedule])
                QMessageBox.information(self, "Расписание", schedule_text)
            else:
                QMessageBox.information(self, "Расписание", "Для вашего класса пока нет расписания.")

        def view_diary(self):
            self.main_window.cursor.execute("SELECT class_name FROM users WHERE username = ?", (self.username,))
            class_name = self.main_window.cursor.fetchone()[0]

            self.main_window.cursor.execute(
                "SELECT subject, grade FROM grades WHERE student_name = ? AND class_name = ?",
                (self.username, class_name)
            )
            grades = self.main_window.cursor.fetchall()

            if not grades:
                QMessageBox.information(self, "Дневник", "Ваш дневник пока пуст.")
                return

            # Открытие окна с дневником
            diary_window = QWidget()
            diary_window.setWindowTitle("Ваш дневник")
            layout = QVBoxLayout()

            diary_table = QTableWidget()
            diary_table.setRowCount(1)
            diary_table.setColumnCount(len(grades))
            diary_table.setHorizontalHeaderLabels([g[0] for g in grades])
            diary_table.setVerticalHeaderLabels([self.username])

            for col, (_, grade) in enumerate(grades):
                diary_table.setItem(0, col, QTableWidgetItem(str(grade) if grade is not None else "-"))

            layout.addWidget(diary_table)
            diary_window.setLayout(layout)
            diary_window.show()
        def view_grades(self):
            self.main_window.cursor.execute("SELECT class_name FROM users WHERE username = ?", (self.username,))
            class_name = self.main_window.cursor.fetchone()[0]

            self.main_window.cursor.execute(
                "SELECT subject, grade FROM grades WHERE student_name = ? AND class_name = ?",
                (self.username, class_name)
            )
            grades = self.main_window.cursor.fetchall()

            if grades:
                grades_text = "\n".join([f"{subject}: {grade}" for subject, grade in grades])
                QMessageBox.information(self, "Оценки", grades_text)
            else:
                QMessageBox.information(self, "Оценки", "У вас пока нет оценок.")

        def logout(self):
            self.main_window.init_ui()


# Основная часть программы
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    with open("style.css", "r") as f:
        app.setStyleSheet(f.read())
    window = SchoolManagementApp()
    window.show()
    sys.exit(app.exec())


