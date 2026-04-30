import os
import tempfile
import speech_recognition as sr
import pygame
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
from menu import MENU

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
pygame.mixer.init()

LANG_CONFIG = {
    "uk": {
        "gtts_lang": "uk",
        "sr_lang": "uk-UA",
        "listening_msg": "[ Слухаю... ]",
        "not_heard": "Вибачте, не почув вас. Будь ласка, спробуйте ще раз.",
        "groq_error": "Виникла помилка зв'язку. Спробуйте ще раз.",
        "goodbye": "До побачення! Будемо раді бачити вас знову в нашій кав'ярні!",
        "exit_words": ["до побачення", "вихід", "вийти", "закінчити", "все дякую", "дякую до побачення"],
    },
    "en": {
        "gtts_lang": "en",
        "sr_lang": "en-US",
        "listening_msg": "[ Listening... ]",
        "not_heard": "Sorry, I didn't catch that. Please try again.",
        "groq_error": "A connection error occurred. Please try again.",
        "goodbye": "Goodbye! We hope to see you again at our café!",
        "exit_words": ["goodbye", "exit", "quit", "bye", "that's all", "thank you bye"],
    },
}


def speak(text: str, lang: str = "uk") -> None:
    print(f"[Бот]: {text}")
    cfg = LANG_CONFIG[lang]
    tts = gTTS(text=text, lang=cfg["gtts_lang"], slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp_path = f.name
    tts.save(tmp_path)
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    try:
        os.unlink(tmp_path)
    except OSError:
        pass


def listen(lang: str = "uk") -> str:
    cfg = LANG_CONFIG[lang]
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(cfg["listening_msg"])
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=12)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = recognizer.recognize_google(audio, language=cfg["sr_lang"])
        print(f"[Користувач]: {text}")
        return text.lower()
    except (sr.UnknownValueError, sr.RequestError):
        return ""


def choose_language() -> str:
    speak(
        "Вітаємо у кав'ярні Затишок! "
        "Щоб обрати українську мову — скажіть «українська». "
        "To choose English — say «English».",
        lang="uk",
    )

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[ Очікую вибір мови... ]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return "uk"

    for lang_code in ["uk-UA", "en-US"]:
        try:
            text = recognizer.recognize_google(audio, language=lang_code).lower()
            print(f"Почуто: {text}")
            if any(w in text for w in ["english", "англійська", "english language"]):
                return "en"
            if any(w in text for w in ["українська", "украинская", "ukraine", "ukrainian"]):
                return "uk"
        except Exception:
            continue

    return "uk"


def build_system_prompt(lang: str) -> str:
    menu_data = MENU[lang]
    cafe_name = menu_data["cafe_name"]

    lines = []
    for category, items in menu_data["categories"].items():
        lines.append(f"\n{category.upper()}:")
        for item, info in items.items():
            lines.append(f"  • {item} — {info['price']} грн: {info['description']}")
    menu_str = "\n".join(lines)

    if lang == "uk":
        return f"""Ти — голосовий помічник кав'ярні "{cafe_name}". \
Ти допомагаєш людям зі слабким зором або повною сліпотою зручно і швидко обирати страви та напої з меню.

ПОВНЕ МЕНЮ:
{menu_str}

Правила поведінки:
- Відповідай КОРОТКО (2-4 речення). Голос — не текст, довгі відповіді важко сприймати.
- Завжди називай ціну при описі позиції.
- Якщо користувач не знає що обрати — запропонуй 1-2 популярні позиції з категорії.
- Якщо запитують про категорії — перелічи їх коротко.
- При підтвердженні замовлення — назви замовлені позиції, загальну суму та побажай смачного.
- Будь терплячим, ввічливим та уважним — користувач може мати труднощі зі сприйняттям.
- Відповідай ВИКЛЮЧНО українською мовою."""
    else:
        return f"""You are a voice assistant for "{cafe_name}". \
You help people with visual impairments or blindness easily choose food and drinks from the menu.

FULL MENU:
{menu_str}

Behavior rules:
- Answer BRIEFLY (2-4 sentences). Voice is not text — long answers are hard to follow.
- Always mention the price when describing an item.
- If the user doesn't know what to choose — suggest 1-2 popular items from a category.
- If asked about categories — list them briefly.
- When confirming an order — repeat the items, give the total price, and wish them bon appétit.
- Be patient, polite and attentive — the user may have difficulty perceiving information.
- Respond ONLY in English."""


def run_bot() -> None:
    lang = choose_language()

    if lang == "uk":
        speak(
            "Ви обрали українську мову. "
            "Я ваш голосовий помічник. "
            "Запитайте мене про меню, категорії або конкретну страву.",
            lang="uk",
        )
    else:
        speak(
            "You selected English. "
            "I am your voice assistant. "
            "Ask me about the menu, categories, or any specific dish.",
            lang="en",
        )

    cfg = LANG_CONFIG[lang]
    history = [{"role": "system", "content": build_system_prompt(lang)}]

    while True:
        user_text = listen(lang)

        if not user_text:
            speak(cfg["not_heard"], lang)
            continue

        if any(w in user_text for w in cfg["exit_words"]):
            speak(cfg["goodbye"], lang)
            break

        history.append({"role": "user", "content": user_text})

        try:
            response = client.chat.completions.create(
                messages=history,
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=300,
            )
            reply = response.choices[0].message.content.strip()
            history.append({"role": "assistant", "content": reply})
            speak(reply, lang)
        except Exception as e:
            print(f"[Groq error]: {e}")
            speak(cfg["groq_error"], lang)


if __name__ == "__main__":
    run_bot()
