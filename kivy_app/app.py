from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import httpx

API_BASE_URL = "http://127.0.0.1:8000"

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        layout.add_widget(Label(text="Welcome to Notes and Timers App", font_size=24))

        notes_button = Button(text="Manage Notes")
        notes_button.bind(on_press=self.switch_to_notes)
        layout.add_widget(notes_button)

        timers_button = Button(text="Manage Timers")
        timers_button.bind(on_press=self.switch_to_timers)
        layout.add_widget(timers_button)

        search_button = Button(text="Search Note by ID")  # New button for search screen
        search_button.bind(on_press=self.switch_to_search)
        layout.add_widget(search_button)

        self.add_widget(layout)

    def switch_to_notes(self, *args):
        self.manager.current = 'notes'

    def switch_to_timers(self, *args):
        self.manager.current = 'timers'
    
    def switch_to_search(self, *args):  # New method for navigation to SearchNoteScreen
        self.manager.current = 'search'

class NotesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_note_id = None  # To keep track of the note being updated
        self.layout = BoxLayout(orientation='vertical')

        back_button = Button(text="Back to Home")
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        self.scrollview = ScrollView(size_hint=(1, None), size=(self.width, 400))
        self.notes_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.notes_list.bind(minimum_height=self.notes_list.setter('height'))
        self.scrollview.add_widget(self.notes_list)

        self.refresh_button = Button(text="Refresh Notes")
        self.refresh_button.bind(on_press=lambda x: Clock.schedule_once(self.refresh_notes))
        self.layout.add_widget(self.refresh_button)

        self.title_input = TextInput(hint_text="Title")
        self.content_input = TextInput(hint_text="Content", multiline=True)
        self.layout.add_widget(self.title_input)
        self.layout.add_widget(self.content_input)

        add_note_button = Button(text="Add Note")
        add_note_button.bind(on_press=lambda x: Clock.schedule_once(self.add_note))
        self.layout.add_widget(add_note_button)

        update_note_button = Button(text="Update Note")
        update_note_button.bind(on_press=lambda x: Clock.schedule_once(self.update_note))
        self.layout.add_widget(update_note_button)

        self.layout.add_widget(self.scrollview)
        self.add_widget(self.layout)

        Clock.schedule_once(self.refresh_notes)

    def refresh_notes(self, *args):
        self.notes_list.clear_widgets()
        try:
            response = httpx.get(f"{API_BASE_URL}/notes/")
            if response.status_code == 200:
                notes = response.json()
                for note in notes:
                    note_button = Button(
                        text=f"{note['id']}: {note['title']}\n{note['content']}",
                        size_hint_y=None,
                        height=100
                    )
                    note_button.bind(on_press=lambda btn, note=note: self.select_note(note))
                    self.notes_list.add_widget(note_button)
        except httpx.RequestError as e:
            self.notes_list.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=50))

    def add_note(self, *args):
        title = self.title_input.text
        content = self.content_input.text
        try:
            response = httpx.post(f"{API_BASE_URL}/notes/", json={"title": title, "content": content})
            if response.status_code == 201:
                self.title_input.text = ""
                self.content_input.text = ""
                self.selected_note_id = None  # Clear selected note
                Clock.schedule_once(self.refresh_notes)
        except httpx.RequestError as e:
            self.notes_list.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=50))

    def update_note(self, *args):
        if not self.selected_note_id:
            self.notes_list.add_widget(Label(text="Select a note to update first.", size_hint_y=None, height=50))
            return

        title = self.title_input.text
        content = self.content_input.text
        try:
            response = httpx.put(
                f"{API_BASE_URL}/notes/{self.selected_note_id}/",
                json={"title": title, "content": content}
            )
            if response.status_code == 200:
                self.title_input.text = ""
                self.content_input.text = ""
                self.selected_note_id = None  # Clear selected note
                Clock.schedule_once(self.refresh_notes)
        except httpx.RequestError as e:
            self.notes_list.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=50))

    def select_note(self, note):
        self.selected_note_id = note['id']
        self.title_input.text = note['title']
        self.content_input.text = note['content']

    def go_back(self, *args):
        self.manager.current = 'home'



class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        back_button = Button(text="Back to Home")
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        self.scrollview = ScrollView(size_hint=(1, None), size=(self.width, 400))
        self.timers_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.timers_list.bind(minimum_height=self.timers_list.setter('height'))
        self.scrollview.add_widget(self.timers_list)

        self.refresh_button = Button(text="Refresh Timers")
        self.refresh_button.bind(on_press=lambda x: Clock.schedule_once(self.refresh_timers))
        self.layout.add_widget(self.refresh_button)

        self.task_name_input = TextInput(hint_text="Task Name")
        self.start_time_input = TextInput(hint_text="Start Time (YYYY-MM-DD HH:MM:SS)")
        self.end_time_input = TextInput(hint_text="End Time (YYYY-MM-DD HH:MM:SS)")
        self.layout.add_widget(self.task_name_input)
        self.layout.add_widget(self.start_time_input)
        self.layout.add_widget(self.end_time_input)

        add_timer_button = Button(text="Add Timer")
        add_timer_button.bind(on_press=lambda x: Clock.schedule_once(self.add_timer))
        self.layout.add_widget(add_timer_button)

        self.layout.add_widget(self.scrollview)
        self.add_widget(self.layout)

        Clock.schedule_once(self.refresh_timers)

    def refresh_timers(self, *args):
        self.timers_list.clear_widgets()
        try:
            response = httpx.get(f"{API_BASE_URL}/timers/")
            if response.status_code == 200:
                timers = response.json()
                for timer in timers:
                    timer_label = Label(
                        text=f"{timer['id']}: {timer['task_name']}\n{timer['start_time']} - {timer['end_time']}\nDuration: {timer['duration']}",
                        size_hint_y=None,
                        height=100
                    )
                    self.timers_list.add_widget(timer_label)
        except httpx.RequestError as e:
            self.timers_list.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=50))

    def add_timer(self, *args):
        task_name = self.task_name_input.text
        start_time = self.start_time_input.text
        end_time = self.end_time_input.text
        try:
            response = httpx.post(f"{API_BASE_URL}/timers/", json={"task_name": task_name, "start_time": start_time, "end_time": end_time})
            if response.status_code == 201:
                self.task_name_input.text = ""
                self.start_time_input.text = ""
                self.end_time_input.text = ""
                Clock.schedule_once(self.refresh_timers)
        except httpx.RequestError as e:
            self.timers_list.add_widget(Label(text=f"Error: {e}", size_hint_y=None, height=50))
    
    def go_back(self, *args):
        self.manager.current = 'home'

class SearchNoteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Back button to return to HomeScreen
        back_button = Button(text="Back to Home")
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

        # Input field for note ID
        self.note_id_input = TextInput(hint_text="Enter Note ID", multiline=False)
        self.layout.add_widget(self.note_id_input)

        # Search button
        search_button = Button(text="Search Note")
        search_button.bind(on_press=self.search_note)
        self.layout.add_widget(search_button)

        # Label to display search result
        self.result_label = Label(text="Search result will appear here", size_hint_y=None, height=200)
        self.layout.add_widget(self.result_label)

        self.add_widget(self.layout)

    def search_note(self, *args):
        note_id = self.note_id_input.text.strip()
        if not note_id.isdigit():
            self.result_label.text = "Please enter a valid note ID."
            return

        try:
            response = httpx.get(f"{API_BASE_URL}/notes/{note_id}/")
            if response.status_code == 200:
                note = response.json()
                self.result_label.text = f"ID: {note['id']}\nTitle: {note['title']}\nContent: {note['content']}"
            else:
                self.result_label.text = "Note not found."
        except httpx.RequestError as e:
            self.result_label.text = f"Error: {e}"

    def go_back(self, *args):
        self.manager.current = 'home'


class NotesTimersApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(NotesScreen(name='notes'))
        sm.add_widget(TimerScreen(name='timers'))
        sm.add_widget(SearchNoteScreen(name='search'))  # Add the SearchNoteScreen
        return sm


if __name__ == "__main__":
    NotesTimersApp().run()
