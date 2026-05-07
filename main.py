from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
import urllib.request
import json
import threading

GROQ_API_KEY = "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"

class AegisApp(App):
    def build(self):
        self.title = "Aegis Messenger"
        root = BoxLayout(orientation='vertical', padding=10, spacing=8)
        title = Label(
            text="Aegis Messenger",
            size_hint_y=None, height=50,
            font_size=20, bold=True, color=(0,1,.7,1)
        )
        root.add_widget(title)
        scroll = ScrollView(size_hint=(1, 1))
        self.chat_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=6, padding=6
        )
        self.chat_layout.bind(
            minimum_height=self.chat_layout.setter('height')
        )
        scroll.add_widget(self.chat_layout)
        root.add_widget(scroll)
        self.scroll = scroll
        input_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.text_input = TextInput(
            hint_text="Напиши сообщение...",
            multiline=False, size_hint_x=.8
        )
        self.text_input.bind(on_text_validate=self.send)
        send_btn = Button(
            text="OK", size_hint_x=.2,
            background_color=(0,.8,.5,1)
        )
        send_btn.bind(on_press=self.send)
        input_row.add_widget(self.text_input)
        input_row.add_widget(send_btn)
        root.add_widget(input_row)
        return root

    def add_message(self, text, is_user=True):
        color = (0.1,0.6,1,1) if is_user else (0,1,0.6,1)
        prefix = "Ты: " if is_user else "AI: "
        lbl = Label(
            text=prefix + text,
            size_hint_y=None, height=40,
            color=color, halign='left'
        )
        self.chat_layout.add_widget(lbl)
        self.scroll.scroll_to(lbl)

    def send(self, *args):
        msg = self.text_input.text.strip()
        if not msg: return
        self.add_message(msg, is_user=True)
        self.text_input.text = ""
        threading.Thread(target=self.ask_groq, args=(msg,)).start()

    def ask_groq(self, msg):
        try:
            payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role":"user","content": msg}]
            }).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
                reply = data["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Ошибка: {e}"
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.add_message(reply, False))

AegisApp().run()
