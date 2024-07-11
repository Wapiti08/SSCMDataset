from docx import Document
from faker import Faker
import random
import pyautogui

random.seed(43)

def create_doc():
    doc = Document()
    fake = Faker()
    
    # fack name
    name = fake.name()
    address = fake.address()
    doc.add_heading(f"{name}: {address}")

    times = random.random(5, 20)
    for _ in range(times):
        # fake context
        text = fake.text()
        sentence = fake.sentence()
        doc.add_paragraph(sentence, styple="ListBullet")
        doc.add_paragraph(text)

    doc.save("{name}.docx")


def automate_gui():
    pyautogui.moveTo(100, 100, duration=1)
    pyautogui.click()
    pyautogui.write("Automating office work with Python", interval=0.1)
    pyautogui.press("enter")


if __name__ == "__main__":
    create_doc()
    automate_gui()