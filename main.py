from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
import random

import socket
import logging
import json

import datetime

player = 1

class ClientInterface:
    def __init__(self,idplayer='1'):
        self.idplayer=idplayer
        self.server_address=('localhost',6666)

    def send_command(self,command_str=""):
        global server_address
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_address)
        logging.warning(f"connecting to {self.server_address}")
        try:
            logging.warning(f"sending message ")
            sock.sendall(command_str.encode())
            # Look for the response, waiting until socket is done (no more data)
            data_received="" #empty string
            while True:
                #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
                data = sock.recv(16)
                if data:
                    #data is not empty, concat with previous content
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    # no more data, stop the process by break
                    break
            # at this point, data_received (string) will contain all data coming from the socket
            # to be able to use the data_received as a dict, need to load it using json.loads()
            hasil = json.loads(data_received)
            logging.warning("data received from server:")
            return hasil
        except:
            logging.warning("error during data receiving")
            return False

    def set_location(self,user=1,x=100,y=0):
        player = self.idplayer
        command_str=f"set_location {player} {x} {y}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            return True
        else:
            return False

    def get_location(self,id=1):
        player = id
        command_str=f"get_location {player}"
        hasil = self.send_command(command_str)
        if (hasil['status']=='OK'):
            lokasi = hasil['location'].split(',')
            return (float(lokasi[0]),float(lokasi[1]))
        else:
            return False

    def get_enemy_location(self):
        try:
            print("OKKKKKKKKKKKKKKKK1")
            command_str = f"get_enemy_location 0"
            hasil = self.send_command(command_str)
            print(hasil)
            if(hasil['status'] =='OK'):
                print("OKKKKKKKKKKKKKKKK")
                return hasil['random_x'],hasil['random_speed']
            else:
                return hasil  
        except Exception as ee:
            return False


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.server_address=('localhost',6666)
        self.client_interface = ClientInterface(2)

        self.prev_time = datetime.datetime.now().second

        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        self._score_label = CoreLabel(text="Score: 0", font_size=20)
        self._score_label.refresh()
        self._score = 0

        self.register_event_type("on_frame")

        with self.canvas:
            Rectangle(source="assets/bg-mario.jpg", pos=(0, 0),
                      size=(Window.width, Window.height))
            self._score_instruction = Rectangle(texture=self._score_label.texture, pos=(
                0, Window.height - 50), size=self._score_label.texture.size)

        self.keysPressed = set()
        self._entities = set()

        Clock.schedule_interval(self._on_frame, 0)

        self.sound = SoundLoader.load("assets/music.wav")
        # self.sound.play()

        Clock.schedule_interval(self.spawn_enemies, 0.1)

    def spawn_enemies(self, dt):
        # for i in range(5):
        if(self.prev_time == datetime.datetime.now().second):
            return
        self.prev_time = datetime.datetime.now().second
        print("masuukkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        enemy = self.client_interface.get_enemy_location()
        if(enemy is False):
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            return
        random_x, random_speed = enemy
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        y = Window.height
        self.add_entity(Enemy((random_x, y), random_speed))

    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            return True
        else:
            return False

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                result.add(e)
        return result

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)


class Entity(object):
    def __init__(self):
        self._pos = (0, 0)
        self._size = (50, 50)
        self._source = "bullshit.png"
        self._instruction = Rectangle(
            pos=self._pos, size=self._size, source=self._source)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source


class Bullet(Entity):
    def __init__(self, pos, speed=300):
        super().__init__()
        sound = SoundLoader.load("assets/bullet.wav")
        # sound.play()
        self._speed = speed
        self.pos = pos
        self.source = "assets/bulletbil.png"
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # check for collision/out of bounds
        if self.pos[1] > Window.height:
            self.stop_callbacks()
            game.remove_entity(self)
            return
        for e in game.colliding_entities(self):
            if isinstance(e, Enemy):
                game.add_entity(Explosion(self.pos))
                self.stop_callbacks()
                game.remove_entity(self)
                e.stop_callbacks()
                game.remove_entity(e)
                game.score += 1
                return

        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] + step_size
        self.pos = (new_x, new_y)


class Enemy(Entity):
    def __init__(self, pos, speed=100):
        super().__init__()
        self._speed = speed
        self.pos = pos
        self.source = "assets/boo.png"
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, sender, dt):
        # check for collision/out of bounds
        if self.pos[1] < 0:
            self.stop_callbacks()
            game.remove_entity(self)
            game.score -= 1
            return

        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] - step_size
        self.pos = (new_x, new_y)


class Explosion(Entity):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        sound = SoundLoader.load("assets/explosion.wav")
        self.source = "assets/explosion.png"
        # sound.play()
        Clock.schedule_once(self._remove_me, 0.1)

    def _remove_me(self, dt):
        game.remove_entity(self)


done = False


class Player(Entity):
    def __init__(self,id):
        super().__init__()
        self.source = "assets/pipe.png"
        game.bind(on_frame=self.move_step)
        game.bind(on_frame=self.update)
        self._shoot_event = Clock.schedule_interval(self.shoot_step, 0.5)
        self.pos = (400, 0)
        self.user = id

        self.server_address=('localhost',6666)
        self.client_interface = ClientInterface(player)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)
        self._shoot_event.cancel()

    def shoot_step(self, dt):
        # shoot
        x = self.pos[0]
        y = self.pos[1] + 50
        game.add_entity(Bullet((x, y)))

    def move_step(self, sender, dt):
        # move
        step_size = 200 * dt
        # tmp = self.client_interface.get_location(self.user)
        # if(tmp is False):
        #     return
        newx = 0

        if "a" in game.keysPressed:
            newx = -2
        if "d" in game.keysPressed:
            newx = 2

        # self.pos = (newx, newy)
        self.client_interface.set_location(self.user,newx)
        print("========================================================"+ f'{self.user} {newx}')
        # print (f'TETETETETETE {Window.width} {Window.height}')
        # self.update

    def update(self, sender, dt):
        tmp = self.client_interface.get_location(self.user)
        print (f'{tmp}')
        if(tmp is False):
            return
        x, y = tmp
        self.pos = (x, y)


game = GameWidget()
player1 = Player(1)
player1.pos = (Window.width/3, 0)
game.add_entity(player1)

player2 = Player(2)
player2.pos = (600, 0)
game.add_entity(player2)


class MyApp(App):
    def build(self):
        return game


if __name__ == "__main__":
    app = MyApp()
    app.run()
