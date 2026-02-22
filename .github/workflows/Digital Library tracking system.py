import json
import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window

os.environ['KIVY_GL_BACKEND'] = 'sdl2'  # For better compatibility

Window.size = (900, 700)

class Book:
    def __init__(self, book_id, title, author, status="available", borrowed_by=None, **kwargs):
        self.book_id = str(book_id)
        self.title = str(title)
        self.author = str(author)
        self.status = status
        self.borrowed_by = borrowed_by

    def to_dict(self):
        return self.__dict__

class Member:
    def __init__(self, member_id, name, email, **kwargs):
        self.member_id = str(member_id)
        self.name = str(name)
        self.email = str(email)

    def to_dict(self):
        return self.__dict__

class DigitalLibrary:
    def __init__(self, file="library_data.json"):
        self.file = file
        self.books = {}
        self.members = {}
        self.history = []
        self.load()

    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    data = json.load(f)
                    for item in data.get('books', []):
                        b = Book(**item)
                        self.books[b.book_id] = b
                    self.history = data.get('history', [])
            except Exception as e:
                print(f"Error loading data: {e}")
                self.books = {}
                self.history = []
        
        members_file = "members_data.json"
        if os.path.exists(members_file):
            try:
                with open(members_file, "r") as f:
                    for item in json.load(f):
                        m = Member(**item)
                        self.members[m.member_id] = m
            except Exception as e:
                print(f"Error loading members: {e}")
                self.members = {}
        
        if not self.books:
            self.books['B101'] = Book('B101', 'The Alchemist', 'Paulo Coelho')
            self.save()
        if not self.members:
            self.members['M001'] = Member('M001', 'John Doe', 'john@example.com')
            self.save_members()

    def save(self):
        data = {'books': [b.to_dict() for b in self.books.values()], 'history': self.history}
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def save_members(self):
        with open("members_data.json", "w") as f:
            json.dump([m.to_dict() for m in self.members.values()], f, indent=2)

    def add_book(self, b_id, title, author):
        try:
            if not b_id or not title:
                return "Error: ID and Title required."
            if b_id in self.books:
                return "Error: Book ID already exists."
            if not all(c.isalpha() or c.isspace() for c in title):
                return "Error: Title must contain only letters and spaces."
            if not all(c.isalpha() or c.isspace() for c in author):
                return "Error: Author must contain only letters and spaces."
            
            self.books[b_id] = Book(b_id, title, author)
            self.history.append(f"{datetime.now()}: Added book '{title}' by {author}")
            self.save()
            return f"Success: '{title}' added."
        except Exception as e:
            return f"Exception: {str(e)}"

    def borrow_book(self, b_id, member_id):
        try:
            if b_id not in self.books:
                return "Error: Book not found."
            if not member_id:
                return "Error: Member ID required."
            
            book = self.books[b_id]
            if book.status != "available":
                return f"Error: Book is currently {book.status}."
            
            book.status = "borrowed"
            book.borrowed_by = member_id
            self.history.append(f"{datetime.now()}: '{book.title}' borrowed by {member_id}")
            self.save()
            return f"Success: '{book.title}' borrowed by {member_id}."
        except Exception as e:
            return f"Exception: {str(e)}"

    def return_book(self, b_id):
        try:
            if b_id not in self.books:
                return "Error: Book not found."
            
            book = self.books[b_id]
            if book.status != "borrowed":
                return "Error: This book is not currently borrowed."
            
            member = book.borrowed_by
            book.status = "available"
            book.borrowed_by = None
            self.history.append(f"{datetime.now()}: '{book.title}' returned from {member}")
            self.save()
            return f"Success: '{book.title}' returned from {member}."
        except Exception as e:
            return f"Exception: {str(e)}"

    def remove_book(self, b_id):
        try:
            if b_id not in self.books:
                return "Error: Book not found."
            
            book = self.books[b_id]
            if book.status == "borrowed":
                return "Error: Cannot remove a borrowed book."
            
            del self.books[b_id]
            self.history.append(f"{datetime.now()}: Removed book '{book.title}'")
            self.save()
            return f"Success: '{book.title}' removed."
        except Exception as e:
            return f"Exception: {str(e)}"

    def add_member(self, m_id, name, email):
        try:
            if not m_id or not name:
                return "Error: ID and Name required."
            if m_id in self.members:
                return "Error: Member ID already exists."
            
            self.members[m_id] = Member(m_id, name, email)
            self.history.append(f"{datetime.now()}: Added member '{name}'")
            self.save_members()
            return f"Success: '{name}' added."
        except Exception as e:
            return f"Exception: {str(e)}"

    def get_all_books(self):
        if not self.books:
            return "Library is empty."
        report = "--- Library Inventory ---\n"
        for b in self.books.values():
            status_icon = "✅" if b.status == "available" else f"❌ ({b.borrowed_by})"
            report += f"[{b.book_id}] {b.title} by {b.author}: {status_icon}\n"
        return report

    def get_all_members(self):
        if not self.members:
            return "No members."
        report = "--- Members ---\n"
        for m in self.members.values():
            report += f"[{m.member_id}] {m.name} - {m.email}\n"
        return report

    def get_history(self):
        if not self.history:
            return "No history."
        return "\n".join(self.history[-20:])  # Last 20 entries

    def export_to_csv(self):
        try:
            with open('library_export.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Type', 'ID', 'Title/Author/Name', 'Status/Details', 'Timestamp'])
                for b in self.books.values():
                    writer.writerow(['Book', b.book_id, f"{b.title} by {b.author}", b.status, ''])
                for m in self.members.values():
                    writer.writerow(['Member', m.member_id, m.name, m.email, ''])
                for h in self.history:
                    writer.writerow(['History', '', '', h, ''])
            return "Exported to library_export.csv"
        except Exception as e:
            return f"Export error: {str(e)}"

# --- Kivy Frontend Logic ---

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.library = DigitalLibrary()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(text="Digital Library Login", font_size=24, size_hint_y=None, height=50, halign='center')
        layout.add_widget(title)
        
        # Username
        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.username_input)
        
        # Password
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(text="Login", size_hint_y=None, height=50, background_color=(0.2, 0.6, 1, 1))
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)
        
        # Status
        self.status_label = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if username == "Niroop" and password == "Niroop2507":
            self.manager.current = 'main'
        else:
            self.status_label.text = "Invalid credentials"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.library = DigitalLibrary()
    
    def show_popup(self, title, message):
        content = Label(text=message, halign='center', valign='middle')
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4), auto_dismiss=True)
        popup.open()
    
    def do_add_book(self):
        b_id = self.ids.book_id_input.text.strip()
        title = self.ids.title_input.text.strip()
        author = self.ids.author_input.text.strip()
        
        result = self.library.add_book(b_id, title, author)
        if "Error" in result or "Exception" in result:
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
            self.ids.book_id_input.text = ""
            self.ids.title_input.text = ""
            self.ids.author_input.text = ""
    
    def do_borrow_book(self):
        b_id = self.ids.borrow_book_id.text.strip()
        m_id = self.ids.borrow_member_id.text.strip()
        
        result = self.library.borrow_book(b_id, m_id)
        if "Error" in result or "Exception" in result:
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
            self.ids.borrow_book_id.text = ""
            self.ids.borrow_member_id.text = ""
    
    def do_return_book(self):
        b_id = self.ids.return_book_id.text.strip()
        
        result = self.library.return_book(b_id)
        if "Error" in result or "Exception" in result:
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
            self.ids.return_book_id.text = ""
    
    def do_remove_book(self):
        b_id = self.ids.remove_book_id.text.strip()
        
        result = self.library.remove_book(b_id)
        if "Error" in result or "Exception" in result:
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
            self.ids.remove_book_id.text = ""
    
    def do_add_member(self):
        m_id = self.ids.member_id_input.text.strip()
        name = self.ids.member_name_input.text.strip()
        email = self.ids.member_email_input.text.strip()
        
        result = self.library.add_member(m_id, name, email)
        if "Error" in result or "Exception" in result:
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
            self.ids.member_id_input.text = ""
            self.ids.member_name_input.text = ""
            self.ids.member_email_input.text = ""
    
    def show_all_books(self):
        result = self.library.get_all_books()
        self.ids.status_label.text = result
    
    def show_all_members(self):
        result = self.library.get_all_members()
        self.ids.status_label.text = result
    
    def show_history(self):
        result = self.library.get_history()
        self.ids.status_label.text = result
    
    def export_csv(self):
        result = self.library.export_to_csv()
        if "error" in result.lower():
            self.show_popup("Error", result)
        else:
            self.ids.status_label.text = result
    
    def do_logout(self):
        self.manager.current = 'login'

class LibraryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == "__main__":
    print("Starting Digital Library App...")
    try:
        LibraryApp().run()
    except Exception as e:
        print(f"Error running the app: {e}")
        print("Ensure Kivy is installed. For Spyder, check graphics backend settings.")