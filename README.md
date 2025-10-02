# School Management System (Tkinter + PyQt5)

This project is a **School Management System** built with Python, using both **Tkinter** and **PyQt5** interfaces on top of an **SQLite database**.
It allows you to manage **Students, Instructors, and Courses** with full CRUD operations, JSON save/load, and DB backup.

---

## 🚀 How to Run

### 1. Tkinter Interface

The Tkinter GUI provides a simple tabbed interface for students, instructors, and courses.
Run:

```bash
python -m src.ui_tk.main_tkinter
```

or, from the project root:

```bash
python -m src.main
```

and choose **`tk`** when prompted.

---

### 2. PyQt5 Interface

The PyQt5 GUI provides a modern tabbed interface with buttons and tables.
Run:

```bash
python -m src.ui_qt.qt_app
```

or, from the project root:

```bash
python -m src.main
```

and choose **`qt`** when prompted.

---

## 📂 Features

* **Students**: Add, update, delete, register in courses
* **Instructors**: Add, update, delete, assign to courses
* **Courses**: Add, edit, delete, assign instructors, enroll students
* **Persistence**:

  * SQLite backend (`school.db`)
  * JSON snapshots (`school.json`)
  * Database backup option
* **Dual UI Options**: Run either Tkinter or PyQt5 interface

---

## 📖 Documentation

Full project documentation is generated with **Sphinx** and available in `docs/_build/html`.
Open `index.html` in your browser, or rebuild using:

```bash
cd docs
make html
```

