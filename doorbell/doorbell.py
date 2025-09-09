from gpiozero import Button, Buzzer, LED, TonalBuzzer
from gpiozero.tones import Tone
from picamera import PiCamera
from datetime import datetime
import telebot
from telebot import types
import RPi.GPIO as GPIO
import time
import face_recognition
import threading
import pickle

bot_token = '<bot_token>'
bot = telebot.TeleBot(bot_token)
chat_id = "6191480141"

known_face_encodings = []
known_face_names = []

# Lade die gespeicherten Modellgewichte fÃ¼r die Gesichtserkennung
with open("./persons/known_faces.pkl", "rb") as f:
    known_face_encodings, known_face_names = pickle.load(f)

print("Models loaded")

button = Button(17)
camera = PiCamera()
tone_1 = Tone('A4')
tone_2 = Tone('E4')
buzzer = TonalBuzzer(pin=19)
RELAY_PIN = 26

green_led = LED(18)
red_led = LED(23)

GPIO.setup(RELAY_PIN, GPIO.OUT)

@bot.callback_query_handler(func=lambda call: call.data in ["open_door", "ignore"])
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "open_door":
        print("Opening")
        openDoor()
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption="Opened the door")
    elif call.data == "ignore":
        print("Ignoring")
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption="Did not open the door")
        keepDoorClosed()

def capture():
    buzzer.play(tone_1)
    time.sleep(0.5)
    buzzer.play(tone_2)
    timestamp = datetime.now().isoformat()
    image_path = './pi/%s.jpg' % timestamp
    camera.capture(image_path)

    image_encoding = face_recognition.face_encodings(face_recognition.load_image_file(image_path))
    
    if len(image_encoding) > 0:
        for i, known_encoding in enumerate(known_face_encodings):
            result_person = face_recognition.compare_faces([known_encoding], image_encoding[0])
            if result_person[0]:
                person_detected = known_face_names[i]
                break
            else:
                person_detected = "Unknown"
    else:
        person_detected = "No face detected"

    markup = types.InlineKeyboardMarkup()
    open_button = types.InlineKeyboardButton(text="Open Door", callback_data="open_door")
    ignore_button = types.InlineKeyboardButton(text="Ignore", callback_data="ignore")
    markup.row(open_button, ignore_button)

    with open(image_path, 'rb') as image_file:
        if person_detected != "Unknown" and person_detected != "No face detected":
             bot.send_photo(chat_id, image_file, caption=f'{person_detected} rang. Opened the door.')
             openDoor()
        else:
            bot.send_photo(chat_id, image_file, caption=f'{person_detected} is ringing', reply_markup=markup)

def stop():
    buzzer.stop()

button.when_pressed = capture
button.when_released = stop

def openDoor():
    green_led.on()
    for i in range(15):
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(0.02)
    green_led.off()

def keepDoorClosed():
    red_led.on()
    time.sleep(10)
    red_led.off()

bot.polling()
