from openai import OpenAI
from typing import List, Dict, Any

DEFAULT_MAX_EXCHANGES = 7


class ChatBot:
    """
    Класс для инкапсуляции логики чат-бота.
    Управляет состоянием (профиль пользователя, история диалога) и взаимодействует с языковой моделью через заданный API-клиент.

    Attributes
    ----------
    client : OpenAI
        Клиент для подключения к API-совместимому серверу (например, Ollama).
    model : str
        Имя модели, используемой для генерации ответов.
    max_exchanges : int
        Максимальное количество обменов (пара "вопрос-ответ"),
        хранимых в краткосрочной памяти.
    user_profile : Dict[str, Any]
        Словарь с данными о пользователе для персонализации.
    history : List[Dict[str, str]]
        Список сообщений, составляющий историю текущего диалога.
    """

    def __init__(self, model: str = "llama3:8b", max_exchanges: int = DEFAULT_MAX_EXCHANGES) -> None:
        """
        Инициализирует экземпляр ChatBot.

        Parameters
        ----------
        model : str, optional
            Имя модели для использования (по умолчанию "llama3:8b").
        max_exchanges : int, optional
            Количество последних обменов для хранения в памяти.
            По умолчанию используется значение константы DEFAULT_MAX_EXCHANGES.
        """

        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )

        self.model = model
        self.max_exchanges = max_exchanges
        self.user_profile: Dict[str, Any] = {}
        self.history: List[Dict[str, str]] = []


    def set_user_profile(self, name: str, context_info_str: str) -> None:
        """
        Устанавливает или обновляет профиль пользователя.

        Контекстная информация парсится из строки с разделителем-запятой.

        Parameters
        ----------
        name : str
            Имя пользователя.
        context_info_str : str
            Строка с интересами или любой другой контекстной информацией,
            перечисленной через запятую.
        """

        context_items = [
            item.strip() for item in context_info_str.split(',')
            if item.strip()
        ]

        self.user_profile = {
            "name": name,
            "context_items": context_items
        }


    def _create_system_prompt(self) -> Dict[str, str]:
        """
        Генерирует системное сообщение на основе профиля пользователя.

        Returns
        -------
        Dict[str, str]
            Словарь, представляющий системное сообщение для API.
        """

        if not self.user_profile:
            return {"role": "system", "content": "Ты — полезный ассистент."}

        name = self.user_profile.get('name', 'не указано')
        context_items = self.user_profile.get('context_items', [])
        
        context_str = ", ".join(context_items) if context_items else "не указана"

        prompt = (
            f"Ты — ассистент. Веди диалог, строго учитывая следующие данные о пользователе. Имя: {name}. "
            f"Ключевая информация о нем (интересы, факты): {context_str}. "
            "Всегда обращайся к пользователю по имени. Адаптируй ответы под его интересы, если это уместно."
        )
        return {"role": "system", "content": prompt}


    def get_response(self, user_input: str) -> str:
        """
        Обрабатывает сообщение пользователя и возвращает ответ от модели.

        Метод обновляет историю диалога, формирует полный контекст
        (системное сообщение + история) и выполняет запрос к модели.

        Parameters
        ----------
        user_input : str
            Текстовое сообщение от пользователя.

        Returns
        -------
        str
            Текстовый ответ, сгенерированный моделью.
        
        Raises
        ------
        ConnectionError
            Если не удается подключиться к серверу Ollama.
        Exception
            При других ошибках API.
        """

        self.history.append({"role": "user", "content": user_input})
        self.history = self.history[-self.max_exchanges * 2:]

        system_message = self._create_system_prompt()
        messages_to_send = [system_message] + self.history

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages_to_send
            )
            answer = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": answer})
            return answer
            
        except Exception as e:
            self.history = self.history[:-1]
            error_msg = (
                f"Ошибка при обращении к модели: {str(e)}\n"
                "Убедитесь, что Ollama запущен (docker start ollama) "
                f"и модель {self.model} загружена."
            )
            raise ConnectionError(error_msg)


    def clear_history(self) -> None:
        """
        Сбрасывает историю диалога.
        """

        self.history = []
