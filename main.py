import radio
from microbit import *
from random import randint

radio.on()
display.show(Image.YES)
clients = []
available_images = ["0101011111111110111000100", "0000001010000001000101110", "0001100011111111111101010", "0010001110111110111001010", "0111010101111111111110101", "1100001000010000111001010", "0111010101111110111001110", "0111011111001001010011100", "0010000110001011110011100"]
image_without_pair = None
image_up = None
score = 0
is_game_started = False
is_game_won = False


def on_wrong_match():
    global score
    display.show(Image.NO)
    sleep(1000)
    display.show(str(score))


def on_match(client1, client2):
    global score
    display.show(Image.YES)
    score += 1
    sleep(500)
    display.show(Image(str(score)))
    client1.on_matched()
    client2.on_matched()
    check_for_win()


def start_game():
    global score
    global is_game_started
    global is_game_won
    is_game_started = True
    display.show(score)


def check_for_win():
    global is_game_won
    global score
    global clients
    if score == len(clients) / 2:
        display.show("You win!")
        is_game_won = True


class Client:
    display_image = None
    state = "DOWN"

    def __init__(self, display_image):
        self.display_image = display_image

    def is_match(self, client):
        if self.state == client.state:
            if self.display_image == client.display_image:
                on_match(self, client)
            else:
                on_wrong_match()

    def on_flip(self):
        if self.state == "MATCHED":
            return
        elif self.state == "DOWN":
            self.state = "UP"
        else:
            self.state = "DOWN"

    def on_matched(self):
        self.state = "MATCHED"

    def is_up(self):
        if self.state == "UP":
            return True
        return False


while True:
    if is_game_won:
        break
    if not is_game_started:
        display.show(str(len(clients)))
        if button_a.is_pressed():
            start_game()
        incoming = radio.receive()
        if incoming == "needID":
            if image_without_pair is not None:
                radio.send(str(len(clients)))
                clients.insert(len(clients), Client(image_without_pair))
                radio.send(str(image_without_pair))
                image_without_pair = None
            else:
                image_pos = randint(0, len(available_images) - 1)  # Select random image
                radio.send(str(len(clients)))  # Sends ID over radio
                clients.insert(len(clients), Client(available_images[image_pos]))  # Create instance of client class with selected image
                radio.send(str(available_images[image_pos]))  # send image over radio
                image_without_pair = available_images[image_pos]  # Marks that the selected image needs a pair
                available_images.pop(image_pos)  # remove the image from the list of available images
    else:
        incoming = radio.receive()
        if incoming is not None:
            receivedNumber = int(incoming)
            if not clients[receivedNumber].is_up():
                if image_up is None:
                    clients[receivedNumber].on_flip()
                    display.show(Image.ARROW_N)
                    image_up = clients[receivedNumber]
                else:
                    clients[receivedNumber].on_flip()
                    clients[receivedNumber].is_match(image_up)
                    image_up = None
            else:
                clients[receivedNumber].on_flip()

