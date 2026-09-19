from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivy.metrics import dp, sp
from kivy.clock import Clock
import random
import os

if platform == 'android':
    pass
else:
    Window.size = (400, 750)

class ResourceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.textures = {}
        self.sounds = {}
        self.is_reloading = False
        self.pending_callback = None
        
        # ============================================================
        # 1. СПИСОК ВСЕХ ЖЕЛАНИЙ (без дубликатов)
        # ============================================================
        self.all_wishes = [
            "М.К. x2",
            "Б.К. +5",
            "Б.К. +2",
            "ходи 2 раза",
            "сброс 1 цвет",
            "сброс",
            "поменяй карты врагу",
            "+5 карт",
            "пропусти 2 круга",
            "Все +4",
            "Все +2",
            "Б.К. +7",
            "+10 карт",
            "сброс 1 вида цифр",
            "1 цвет все сброс",
            "1 цвет все сброс",
            "сброс 1 вида цифр",
            "сброс",
            "сброс 1 цвет",
        ]
        
        self.current_deck = []
        
        # ============================================================
        # 2. ЗВУКИ ДЛЯ ЖЕЛАНИЙ
        # ============================================================
        self.wish_sounds = {
            "М.К. x2": "mk_x2.mp3",
            "Б.К. +5": "bk_plus_5.mp3",
            "Б.К. +2": "bk_plus_2.mp3",
            "ходи 2 раза": "hodit_2_raza.mp3",
            "сброс 1 цвет": "sbros_1_cvet.mp3",
            "сброс": "sbros.mp3",
            "поменяй карты врагу": "na_vybor.mp3",
            "+5 карт": "plus_5_kart.mp3",
            "пропусти 2 круга": "propusti_2_kruga.mp3",
            "Все +4": "vse_plus_4.mp3",
            "Все +2": "vse_plus_2.mp3",
            "Б.К. +7": "bk_plus_7.mp3",
            "+10 карт": "plus_10_kart.mp3",
            "сброс 1 вида цифр": "sbros_1_cvet_aboba.mp3",
            "1 цвет все сброс": "absxsas.mp3",
        }
        
        self.shuffle_deck()
        self.load_resources()
    
    def shuffle_deck(self, play_sound=True):
        self.current_deck = self.all_wishes.copy()
        random.shuffle(self.current_deck)
        print(f"Колода перемешана! {len(self.current_deck)} карт")
        if play_sound:
            self.play_new_deck_sound()
    
    def play_new_deck_sound(self):
        if 'new_deck' in self.sounds and self.sounds['new_deck']:
            self.sounds['new_deck'].volume = 0.8
            self.sounds['new_deck'].play()
    
    def get_random_wish(self, callback=None):
        if not self.current_deck and not self.is_reloading:
            self.is_reloading = True
            self.pending_callback = callback
            
            self.play_new_deck_sound()
            
            sound_duration = 7
            if 'new_deck' in self.sounds and self.sounds['new_deck']:
                try:
                    sound_duration = self.sounds['new_deck'].get_length()
                    if sound_duration <= 0:
                        sound_duration = 7
                except:
                    sound_duration = 7
            
            Clock.schedule_once(lambda dt: self._do_reload_deck(), sound_duration)
            return None
        elif self.is_reloading:
            return None
            
        wish = self.current_deck.pop()
        print(f"Выпало: {wish} (осталось {len(self.current_deck)})")
        return wish
    
    def _do_reload_deck(self):
        self.is_reloading = False
        self.shuffle_deck(play_sound=False)
        
        if self.pending_callback:
            callback = self.pending_callback
            self.pending_callback = None
            Clock.schedule_once(lambda dt: callback(), 0.1)
    
    def _get_resource_path(self, relative_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, relative_path)
        
        if not os.path.exists(full_path):
            alternatives = [
                os.path.join('/sdcard', relative_path),
                os.path.join('/data/data/org.test.unocounter/files', relative_path),
                os.path.join(os.getcwd(), relative_path),
                relative_path
            ]
            for alt in alternatives:
                if os.path.exists(alt):
                    return alt
        
        return full_path
    
    def load_resources(self):
        # ============================================================
        # 3. ТЕКСТУРЫ
        # ============================================================
        texture_files = {
            'logo': 'assets/textures/logo.png',
            'reverse': 'assets/textures/reverse.png',
            'card_bg': 'assets/textures/card_bg.png',
            'square_green': 'assets/textures/square_green.png',
            'square_gray': 'assets/textures/square_gray.png'
        }
        
        for name, path in texture_files.items():
            full_path = self._get_resource_path(path)
            
            if os.path.exists(full_path):
                try:
                    self.textures[name] = full_path
                    print(f"Загружена текстура: {name}")
                except Exception as e:
                    print(f"Не удалось загрузить {name}: {e}")
                    self.textures[name] = None
            else:
                print(f"Файл не найден: {full_path}")
                self.textures[name] = None
        
        # ============================================================
        # 4. ЗВУКИ ЖЕЛАНИЙ
        # ============================================================
        for wish_text, sound_file in self.wish_sounds.items():
            sound_path = self._get_resource_path(f'assets/sounds/wishes/{sound_file}')
            if os.path.exists(sound_path):
                try:
                    sound = SoundLoader.load(sound_path)
                    if sound:
                        self.sounds[sound_file] = sound
                        self.sounds[sound_file].volume = 0.6
                        print(f"Загружен звук: {sound_file}")
                    else:
                        self.sounds[sound_file] = None
                except Exception as e:
                    print(f"Не удалось загрузить {sound_file}: {e}")
                    self.sounds[sound_file] = None
            else:
                print(f"Файл звука не найден: {sound_path}")
                self.sounds[sound_file] = None
        
        # ============================================================
        # 5. ОСНОВНЫЕ ЗВУКИ
        # ============================================================
        main_sounds = {
            'click': 'assets/sounds/click.mp3',
            'exit': 'assets/sounds/xbox-360-achievement-sound.mp3',
            'reverse': 'assets/sounds/sword-swing-sound.wav',
            'reverse_clockwise': 'assets/sounds/reverse_clockwise.mp3',
            'reverse_counter': 'assets/sounds/reverse_counter.mp3',
            'new_deck': 'assets/sounds/new_deck.mp3',
            'win0': 'assets/sounds/victoryff.swf.mp3',
            'win1': 'assets/sounds/myinstants_0.mp3',
            'win2': 'assets/sounds/myinstants_1.mp3',
            'win3': 'assets/sounds/myinstants_2.mp3',
            'win4': 'assets/sounds/myinstants_3.mp3',
            'win5': 'assets/sounds/myinstants_4.mp3',
            'win6': 'assets/sounds/myinstants_5.mp3',
            'win7': 'assets/sounds/ura-pobeda_Jjs1T4y.mp3',
            'next': 'assets/sounds/click.mp3',
            'spin': 'assets/sounds/click.mp3'
        }
        
        for name, path in main_sounds.items():
            full_path = self._get_resource_path(path)
            
            if os.path.exists(full_path):
                try:
                    sound = SoundLoader.load(full_path)
                    if sound:
                        self.sounds[name] = sound
                        if name in ['click', 'next', 'spin']:
                            self.sounds[name].volume = 0.5
                        elif name in ['reverse', 'reverse_clockwise', 'reverse_counter']:
                            self.sounds[name].volume = 0.6
                        elif name.startswith('win'):
                            self.sounds[name].volume = 0.7
                        elif name == 'new_deck':
                            self.sounds[name].volume = 0.8
                        print(f"Загружен звук: {name}")
                    else:
                        self.sounds[name] = None
                except Exception as e:
                    print(f"Не удалось загрузить {name}: {e}")
                    self.sounds[name] = None
            else:
                print(f"Файл звука не найден: {full_path}")
                self.sounds[name] = None
    
    def get_texture(self, name):
        return self.textures.get(name)
    
    def play_sound(self, name):
        if name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].play()
                return True
            except Exception as e:
                print(f"Ошибка воспроизведения {name}: {e}")
        return False
    
    def play_wish_sound(self, wish_text):
        sound_file = self.wish_sounds.get(wish_text)
        if sound_file and sound_file in self.sounds and self.sounds[sound_file]:
            try:
                self.sounds[sound_file].play()
                return True
            except Exception as e:
                print(f"Ошибка воспроизведения желания: {e}")
        return False
    
    def get_remaining_cards(self):
        return len(self.current_deck)

class PlayerCard(BoxLayout):
    def __init__(self, player_id, direction_indicator, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(260)
        
        self.player_id = player_id
        self.direction_indicator = direction_indicator
        self.app_instance = app_instance
        self.exits = 0
        self.max_cards = 7
        self.is_active = False
        self.is_winner = False
        
        self.resource_manager = ResourceManager()
        
        with self.canvas.before:
            Color(0.15, 0.2, 0.3, 0.3)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        top_layout = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5))
        
        self.name_input = TextInput(
            text=f'Игрок {player_id + 1}',
            font_size=sp(20),
            multiline=False,
            size_hint_x=0.5,
            background_color=(0.3, 0.3, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[dp(10), dp(10)]
        )
        top_layout.add_widget(self.name_input)
        
        self.active_label = Label(
            text='',
            font_size=sp(22),
            size_hint_x=0.3,
            color=(0, 1, 0, 1),
            bold=True
        )
        top_layout.add_widget(self.active_label)
        
        self.delete_btn = Button(
            text='Удалить',
            font_size=sp(16),
            size_hint_x=0.2,
            background_color=(0.6, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.delete_btn.bind(on_press=self.delete_player)
        top_layout.add_widget(self.delete_btn)
        
        self.add_widget(top_layout)
        
        info_layout = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))
        
        self.exit_dots = BoxLayout(spacing=dp(4), size_hint_x=0.5)
        self.exit_dots_layout = BoxLayout(orientation='vertical')
        self.exit_dots_label = Label(
            text='Выходы:',
            font_size=sp(14),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=dp(20)
        )
        self.exit_dots_layout.add_widget(self.exit_dots_label)
        
        dots_row = BoxLayout(spacing=dp(6), size_hint_x=1)
        self.dot_widgets = []
        for i in range(self.max_cards):
            dot = Image(
                source=self.resource_manager.get_texture('square_gray'),
                size_hint=(None, None),
                size=(dp(29), dp(28)),
                allow_stretch=True,
                keep_ratio=False
            )
            self.dot_widgets.append(dot)
            dots_row.add_widget(dot)
        self.exit_dots_layout.add_widget(dots_row)
        
        info_layout.add_widget(self.exit_dots_layout)
        
        penalty_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        penalty_layout.add_widget(Label(
            text='возьми еще:',
            font_size=sp(14),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=dp(20)
        ))
        self.penalty_label = Label(
            text='7 карт',
            font_size=sp(24),
            bold=True,
            color=(0.8, 0.9, 1, 1)
        )
        penalty_layout.add_widget(self.penalty_label)
        
        info_layout.add_widget(penalty_layout)
        self.add_widget(info_layout)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        
        self.exit_btn = Button(
            text='ВЫШЕЛ',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=sp(20),
            bold=True,
            size_hint_x=0.7
        )
        self.exit_btn.bind(on_press=self.player_exit)
        btn_layout.add_widget(self.exit_btn)
        
        self.reset_btn = Button(
            text='Сброс',
            background_color=(0.3, 0.3, 0.3, 1),
            font_size=sp(18),
            size_hint_x=0.3
        )
        self.reset_btn.bind(on_press=self.reset_player)
        btn_layout.add_widget(self.reset_btn)
        
        self.add_widget(btn_layout)
        self.btn_layout = btn_layout
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def delete_player(self, instance):
        if len(self.app_instance.players_container.children) <= 2:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
            content.add_widget(Label(
                text='Должно остаться минимум 2 игрока!',
                font_size=sp(22),
                color=(1, 1, 1, 1)
            ))
            btn = Button(text='OK', size_hint_y=None, height=dp(50), font_size=sp(20))
            popup = Popup(title='Внимание', content=content, size_hint=(0.8, 0.3))
            btn.bind(on_press=popup.dismiss)
            content.add_widget(btn)
            popup.open()
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        content.add_widget(Label(
            text=f'Удалить {self.name_input.text}?',
            font_size=sp(24),
            color=(1, 1, 1, 1)
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        yes_btn = Button(text='Да', background_color=(0.8, 0.2, 0.2, 1), font_size=sp(20))
        no_btn = Button(text='Нет', background_color=(0.3, 0.3, 0.3, 1), font_size=sp(20))
        
        popup = Popup(title='Удалить игрока?', content=content, size_hint=(0.8, 0.3))
        
        def confirm_delete(instance):
            self.app_instance.remove_player(self)
            popup.dismiss()
            self.resource_manager.play_sound('click')
        
        yes_btn.bind(on_press=confirm_delete)
        no_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        popup.open()
    
    def player_exit(self, instance):
        if self.is_winner:
            return
        
        self.exits += 1
        self.update_display()
        self.resource_manager.play_sound('exit')
        
        if self.exits >= self.max_cards:
            self.is_winner = True
            wit_pere = random.randint(1,7)
            if wit_pere == 1:
                self.resource_manager.play_sound('win0')
            elif wit_pere == 2:
                self.resource_manager.play_sound('win1')
            elif wit_pere == 3:
                self.resource_manager.play_sound('win2')
            elif wit_pere == 4:
                self.resource_manager.play_sound('win3')
            elif wit_pere == 5:
                self.resource_manager.play_sound('win4')
            elif wit_pere == 6:
                self.resource_manager.play_sound('win5')
            elif wit_pere == 7:
                self.resource_manager.play_sound('win6')
            self.show_win_popup()
            self.hide_exit_button()
    
    def hide_exit_button(self):
        self.exit_btn.opacity = 0
        self.exit_btn.disabled = True
        self.exit_btn.size_hint_x = 0.01
        self.reset_btn.size_hint_x = 0.99
        self.reset_btn.background_color = (0.2, 0.6, 0.2, 1)
        self.reset_btn.text = 'Сброс победителя'
        self.reset_btn.font_size = sp(18)

    def show_exit_button(self):
        self.exit_btn.opacity = 1
        self.exit_btn.disabled = False
        self.exit_btn.size_hint_x = 0.7
        self.reset_btn.size_hint_x = 0.3
        self.reset_btn.background_color = (0.3, 0.3, 0.3, 1)
        self.reset_btn.text = 'Сброс'
        self.reset_btn.font_size = sp(18)
    
    def show_win_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        content.add_widget(Label(
            text=f'{self.name_input.text} ПОБЕДИЛ!',
            font_size=sp(36),
            color=(1, 0.8, 0, 1),
            bold=True
        ))
        btn = Button(text='OK', size_hint_y=None, height=dp(60), font_size=sp(22))
        popup = Popup(title='ПОБЕДА', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def reset_player(self, instance):
        self.exits = 0
        self.is_winner = False
        self.update_display()
        self.show_exit_button()
        self.resource_manager.play_sound('click')
    
    def update_display(self):
        for i, dot in enumerate(self.dot_widgets):
            if i < self.exits:
                dot.text = '█'
                dot.color = (0, 1, 0, 0.8)
            else:
                dot.text = '↘️'
                dot.color = (0.3, 0.3, 0.3, 0.5)
        
        penalty = self.max_cards - self.exits
        if penalty > 0:
            self.penalty_label.text = f'{penalty} карт'
            self.penalty_label.color = (0.8, 0.9, 1, 1)
        elif penalty == 0:
            self.penalty_label.text = 'ПОБЕДА'
            self.penalty_label.color = (1, 1, 0, 1)
        else:
            self.penalty_label.text = '!'
            self.penalty_label.color = (1, 0, 0, 1)
    
    def set_active(self, active):
        self.is_active = active
        if active and not self.is_winner:
            self.active_label.text = 'ХОД'
            self.active_label.color = (0, 1, 0, 1)
            self.resource_manager.play_sound('next')
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.2, 0.7, 0.2, 0.4)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        elif active and self.is_winner:
            self.active_label.text = ''
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.8, 0.7, 0.2, 0.4)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        else:
            self.active_label.text = ''
            if self.is_winner:
                self.canvas.before.clear()
                with self.canvas.before:
                    Color(0.8, 0.7, 0.2, 0.2)
                    self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            else:
                self.canvas.before.clear()
                with self.canvas.before:
                    Color(0.2, 0.3, 0.5, 0.3)
                    self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])

class DirectionIndicator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(110)
        self.padding = dp(10)
        self.spacing = dp(5)
        
        self.direction = 1
        self.resource_manager = ResourceManager()
        self.spinning = False
        
        self.wish_btn = Button(
            text='РУЛЕТКА',
            size_hint_x=1,
            size_hint_y=None,
            height=dp(50),
            font_size=sp(24),
            bold=True,
            background_color=(0.8, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.wish_btn.bind(on_press=self.spin_wheel)
        self.add_widget(self.wish_btn)
        
        self.reverse_btn = Button(
            text='ПО ЧАСОВОЙ',
            size_hint_x=1,
            size_hint_y=None,
            height=dp(45),
            font_size=sp(18),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal='',
            background_color=(0.8, 0.3, 0, 1)
        )
        self.reverse_btn.bind(on_press=self.reverse_direction)
        self.add_widget(self.reverse_btn)
    
    def update_counter(self):
        remaining = self.resource_manager.get_remaining_cards()
        if remaining == 0:
            self.wish_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.wish_btn.text = 'КОЛОДА ПУСТА'
        else:
            self.wish_btn.background_color = (0.8, 0.6, 0.2, 1)
            self.wish_btn.text = 'РУЛЕТКА'
    
    def reverse_direction(self, instance):
        self.direction *= -1
        self.update_display()
        
        if self.direction == 1:
            self.resource_manager.play_sound('reverse_counter')
        else:
            self.resource_manager.play_sound('reverse_clockwise')
    
    def update_display(self):
        if self.direction == 1:
            self.reverse_btn.text = 'ПО ЧАСОВОЙ'
            self.reverse_btn.background_color = (0.8, 0.3, 0, 1)
        else:
            self.reverse_btn.text = 'ПРОТИВ ЧАСОВОЙ'
            self.reverse_btn.background_color = (0.2, 0.3, 0.8, 1)
    
    def spin_wheel(self, instance):
        if self.spinning:
            return
        
        self.spinning = True
        
        def after_reload():
            wish_text = self.resource_manager.get_random_wish()
            if wish_text:
                self.start_animation(wish_text)
            else:
                self.spinning = False
            self.update_counter()
        
        wish_text = self.resource_manager.get_random_wish(after_reload)
        
        if wish_text is None:
            self.update_counter()
            return
        
        self.start_animation(wish_text)
    
    def start_animation(self, wish_text):
        self.wish_btn.text = 'КРУТИМ...'
        self.resource_manager.play_sound('spin')
        
        spin_texts = ['КРУТИМ...', 'ВЕРТИМ...', 'МЕНЯЕМ...', 'ВРАЩАЕМ...', 'ГОТОВО...']
        self.animation_count = 0
        
        def update_animation(dt):
            self.animation_count += 1
            if self.animation_count < 10:
                idx = self.animation_count % len(spin_texts)
                self.wish_btn.text = spin_texts[idx]
                Clock.schedule_once(update_animation, 0.1)
            else:
                self.show_result(wish_text)
                self.update_counter()
        
        Clock.schedule_once(update_animation, 0.1)
    
    def show_result(self, wish_text):
        self.wish_btn.text = 'РУЛЕТКА'
        self.resource_manager.play_wish_sound(wish_text)
        
        remaining = self.resource_manager.get_remaining_cards()
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        content.add_widget(Label(
            text='РУЛЕТКА ЖЕЛАНИЙ',
            font_size=sp(26),
            color=(1, 0.8, 0, 1),
            bold=True,
            size_hint_y=None,
            height=dp(45),
            halign='center'
        ))
        
        content.add_widget(Label(
            text=wish_text,
            font_size=sp(28),
            color=(1, 1, 1, 1),
            bold=True,
            size_hint_y=None,
            height=dp(60),
            halign='center'
        ))
        
        content.add_widget(Label(
            text=f'Осталось карт: {remaining}',
            font_size=sp(16),
            color=(0.6, 0.8, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        ))
        
        btn = Button(
            text='Закрыть',
            size_hint_y=None,
            height=dp(50),
            font_size=sp(20),
            background_color=(0.2, 0.6, 0.2, 1)
        )
        
        popup = Popup(
            title='Желание',
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=True
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        
        self.spinning = False
    
    def get_current_player(self, total_players, current_index):
        next_index = current_index + self.direction
        if next_index < 0:
            next_index = total_players - 1
        elif next_index >= total_players:
            next_index = 0
        return next_index

class UNOCounterApp(App):
    def build(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                activity.setRequestedOrientation(10)
            except:
                pass
        
        self.current_player_index = 0
        self.players_container = None
        self.direction_indicator = None
        self.resource_manager = ResourceManager()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        title_layout = BoxLayout(size_hint_y=None, height=dp(70))
        
        with title_layout.canvas.before:
            Color(0.8, 0.6, 0.2, 0.2)
            self.title_rect = RoundedRectangle(pos=title_layout.pos, size=title_layout.size, radius=[dp(15)])
        title_layout.bind(pos=self.update_title_rect, size=self.update_title_rect)
        
        title = Label(
            text='UNO СЧЕТЧИК',
            font_size=sp(28),
            bold=True,
            color=(1, 0.8, 0, 1)
        )
        title_layout.add_widget(title)
        main_layout.add_widget(title_layout)
        
        self.direction_indicator = DirectionIndicator()
        main_layout.add_widget(self.direction_indicator)
        
        scroll = ScrollView(size_hint=(1, 1))
        self.players_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.players_container.bind(minimum_height=self.players_container.setter('height'))
        scroll.add_widget(self.players_container)
        main_layout.add_widget(scroll)
        
        control_layout = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(10)
        )
        
        add_btn = Button(
            text='Добавить',
            font_size=sp(16),
            background_color=(0.2, 0.6, 0.2, 1),
            size_hint_x=0.35
        )
        add_btn.bind(on_press=self.add_player)
        control_layout.add_widget(add_btn)
        
        reset_all_btn = Button(
            text='Сброс',
            font_size=sp(16),
            background_color=(0.6, 0.2, 0.2, 1),
            size_hint_x=0.25
        )
        reset_all_btn.bind(on_press=self.reset_all)
        control_layout.add_widget(reset_all_btn)
        
        next_btn = Button(
            text='Следующий',
            font_size=sp(16),
            background_color=(0, 0.5, 0.8, 1),
            size_hint_x=0.4
        )
        next_btn.bind(on_press=self.next_player)
        control_layout.add_widget(next_btn)
        
        main_layout.add_widget(control_layout)
        
        self.add_player(None)
        self.add_player(None)
        
        self.current_player_index = 0
        self.update_active_player()
        
        self.resource_manager.play_sound('click')
        
        return main_layout
    
    def update_title_rect(self, instance, value):
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size
    
    def add_player(self, instance):
        player_id = len(self.players_container.children)
        player_card = PlayerCard(player_id, self.direction_indicator, self)
        self.players_container.add_widget(player_card)
        self.update_player_names()
    
    def remove_player(self, player_card):
        self.players_container.remove_widget(player_card)
        self.update_player_names()
    
    def update_player_names(self):
        children = list(reversed(self.players_container.children))
        for i, child in enumerate(children):
            child.player_id = i
            child.name_input.text = f'Игрок {i + 1}'
    
    def reset_all(self, instance):
        for child in self.players_container.children:
            child.reset_player(None)
        
        self.direction_indicator.direction = 1
        self.direction_indicator.update_display()
        self.direction_indicator.wish_btn.text = 'РУЛЕТКА'
        self.direction_indicator.wish_btn.background_color = (0.8, 0.6, 0.2, 1)
        
        self.current_player_index = 0
        self.update_active_player()
        
        self.resource_manager.play_sound('click')
        self.resource_manager.shuffle_deck(play_sound=False)
        self.direction_indicator.update_counter()
    
    def next_player(self, instance):
        total_players = len(self.players_container.children)
        if total_players == 0:
            return
        
        self.current_player_index = self.direction_indicator.get_current_player(
            total_players,
            self.current_player_index
        )
        self.update_active_player()
        self.resource_manager.play_sound('next')
    
    def update_active_player(self):
        if self.players_container is None:
            return
        
        for child in self.players_container.children:
            child.set_active(False)
        
        if self.players_container.children:
            players = list(reversed(self.players_container.children))
            if 0 <= self.current_player_index < len(players):
                players[self.current_player_index].set_active(True)

if __name__ == '__main__':
    UNOCounterApp().run()