from chatbot import ChatBot


class COLORS:
    """
    Константы для ANSI-кодов, для цветного вывода.
    """
    USER = '\033[94m'
    BOT = '\033[92m'
    INFO = '\033[37m'
    ERROR = '\033[91m'
    END = '\033[0m'


def setup_profile(bot: ChatBot) -> None:
    """
    Запрашивает и устанавливает профиль пользователя.
    """

    separator = "─" * 50
    print(f"{COLORS.INFO}{separator}\nНастройка профиля пользователя{COLORS.END}")
    name = input(f"{COLORS.INFO}    Введите ваше имя: {COLORS.END}")
    context_str = input(f"{COLORS.INFO}    Интересы и другая информация, которую бот должен знать: {COLORS.END}")
    bot.set_user_profile(name, context_str)
    print(f"{COLORS.INFO}{separator}{COLORS.END}")


def show_history(bot: ChatBot) -> None:
    """
    Выводит историю текущего диалога.
    """

    if not bot.history:
        print(f"{COLORS.INFO}История диалога пуста.{COLORS.END}\n")
        return
    
    separator = "─" * 50
    print(f"\n{COLORS.INFO}{separator}")
    print("История диалога:")
    print(f"{separator}{COLORS.END}\n")
    
    for message in bot.history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            print(f"{COLORS.USER}Вы:{COLORS.END} {content}\n")
        elif role == "assistant":
            print(f"{COLORS.BOT}Бот:{COLORS.END} {content}\n")
    
    print(f"{COLORS.INFO}{separator}{COLORS.END}\n")


def run_chat_loop(bot: ChatBot) -> None:
    """
    Запускает основной цикл интерактивного диалога с ботом.
    """

    try:
        while True:
            user_text = input(f"{COLORS.USER}Вы:{COLORS.END} ")
            
            if user_text.lower() in ["q", "quit"]:
                break
            
            if user_text.strip() == "/history":
                show_history(bot)
                continue
            
            if not user_text.strip():
                continue
            
            try:
                response = bot.get_response(user_text)
                print(f"\n{COLORS.BOT}Бот:{COLORS.END}\n{response}\n")
            except ConnectionError as e:
                print(f"\n{COLORS.ERROR}Ошибка:{COLORS.END} {e}\n")
            except Exception as e:
                print(f"\n{COLORS.ERROR}Неожиданная ошибка:{COLORS.END} {e}\n")
                
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{COLORS.INFO}Завершение сеанса.{COLORS.END}")


def main() -> None:
    """
    Основная функция для запуска чат-клиента.
    Инициализирует бота, настраивает профиль и запускает цикл диалога.
    """

    bot = ChatBot()
    setup_profile(bot)
    print(f"\n{COLORS.BOT}Бот готов.{COLORS.END} {COLORS.INFO}Для выхода введите 'q' или 'quit'. Для просмотра истории введите '/history'.{COLORS.END}\n")
    run_chat_loop(bot)


if __name__ == "__main__":
    main()
