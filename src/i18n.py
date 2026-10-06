"""Interface language (English or Russian) for the GUI and messages shown to the user.

The choice is stored in .local/settings.json; the GUI passes it to the worker process
through LEXIREAD_UI_LANG so that pipeline errors arrive in the same language.
"""

import json
import os
from pathlib import Path

LANGUAGES = ("en", "ru")
ENV = "LEXIREAD_UI_LANG"
SETTINGS = Path(__file__).resolve().parent.parent / ".local" / "settings.json"

# Names of text languages in the grammatical forms the Russian templates need.
LANGUAGE_FORMS = {
    "ru": {
        "en": {"gen": "английского", "acc": "английский", "nom": "Английский"},
        "es": {"gen": "испанского", "acc": "испанский", "nom": "Испанский"},
        "el": {"gen": "греческого", "acc": "греческий", "nom": "Греческий"},
    },
    "en": {
        "en": {"gen": "English", "acc": "English", "nom": "English"},
        "es": {"gen": "Spanish", "acc": "Spanish", "nom": "Spanish"},
        "el": {"gen": "Greek", "acc": "Greek", "nom": "Greek"},
    },
}

TEXT = {
    # Main window
    "btn.help": ("Help", "Справка"),
    "lbl.help": ("About the app and how to use it", "Описание и инструкция по работе с приложением"),
    "btn.browse": ("Choose file", "Выберите файл"),
    "tip.browse": (
        "Choose a book or subtitles in a foreign language: TXT, EPUB, FB2, DOCX, PDF, SRT, VTT, ASS",
        "Выберите книгу или субтитры на иностранном языке: TXT, EPUB, FB2, DOCX, PDF, SRT, VTT, ASS",
    ),
    "lbl.text_language": ("Text language", "Язык текста"),
    "tip.text_language": ("Choose the language the text is written in", "Выберите язык, на котором написан текст"),
    "chk.llm": (" Translate with LLM", " Перевод через LLM"),
    "tip.llm": (
        "LLM translation needs an OpenAI API key. Enter the key; it will be saved to .local/api-key.bin",
        "Для перевода через LLM нужен OpenAI API key. Введите API key. Он будет сохранен в .local/api-key.bin",
    ),
    "chk.known": (" Exclude known words", " Исключить известные слова"),
    "tip.known": (
        "Known words will not be included in the final word list and study cards",
        "Известные слова не будут включаться в итоговый список слов и в карточки для изучения",
    ),
    "lbl.advanced": ("Advanced settings", "Расширенные настройки"),
    "lbl.coverage": ("Text coverage, %", "Покрытие текста, %"),
    "tip.coverage": (
        "Share of the text that the selected most frequent words must cover",
        "Определяет долю текста, которую должны покрывать отобранные наиболее частотные слова",
    ),
    "lbl.specificity": ("Specificity threshold", "Порог специфичности"),
    "tip.specificity": (
        "How many times more often a word occurs in this text than in other texts",
        "Во сколько раз слово встречается в анализируемом тексте чаще, чем в других текстах",
    ),
    "lbl.occurrences": ("Minimum occurrences", "Минимум вхождений в тексте"),
    "tip.occurrences": (
        "How many times a word must occur in the text to get into the list",
        "Минимальное количество раз, которое слово должно встретиться в тексте, чтобы оно попало в словарь",
    ),
    "btn.start": ("Start analysis", "Начать анализ"),
    "tip.start": (
        "Analyzes the text and creates a word list and study cards",
        "Запускает анализ текста. В результате будут сформированы список слов и карточки для изучения",
    ),
    "btn.list": ("Open word list", "Открыть список слов"),
    "btn.table": ("Summary table", "Сводная таблица"),
    "btn.cards": ("Open cards", "Открыть карточки"),
    "btn.folder": ("Results folder", "Папка с результатами"),
    "btn.cancel": ("Cancel", "Отмена"),
    "menu.cut": ("Cut", "Вырезать"),
    "menu.copy": ("Copy", "Копировать"),
    "menu.paste": ("Paste", "Вставить"),
    "menu.select_all": ("Select all", "Выделить всё"),
    "err.already_running": ("The analysis is already running.", "Анализ уже запущен."),
    "btn.save": ("Save", "Сохранить"),
    # Status line
    "status.ready": ("Status: Set up the analysis", "Статус: Настройка параметров анализа"),
    "status.preparing": ("Status: Preparing the analysis…", "Статус: Подготовка анализа…"),
    "status.error": ("Status: Error", "Статус: Ошибка"),
    "status.done": ("Status: Done. Lemmas: {lemmas}.", "Статус: Обработка завершена. Лемм: {lemmas}."),
    "status.done_cards": (" Cards: {cards}.", " Карточек: {cards}."),
    "status.progress": (
        "Status: {stage} · step {completed} of {total} · {elapsed} elapsed",
        "Статус: {stage} · {completed} из {total} этапов · выполняется {elapsed}",
    ),
    "time.min_sec": ("{minutes} min {seconds:02d} s", "{minutes} мин {seconds:02d} сек"),
    "time.sec": ("{seconds} s", "{seconds} сек"),
    "status.installing": ("Status: Installing {gen} components…", "Статус: Установка компонентов {gen} языка…"),
    "status.installed": ("Status: {nom} installed", "Статус: {nom} язык установлен"),
    "status.not_installed": ("Status: {nom} not installed", "Статус: {nom} язык не установлен"),
    # Pipeline stages
    "stage.preprocess": ("Preparing text", "Подготовка текста"),
    "stage.nlp": ("Analyzing text", "Анализ текста"),
    "stage.aggregate": ("Counting words", "Подсчёт слов"),
    "stage.reference": ("Word frequencies", "Оценка частот"),
    "stage.postprocess": ("Building dictionary", "Подготовка словаря"),
    "stage.grammar": ("Grammar forms", "Грамматические формы"),
    "stage.ipa": ("Transcription", "Транскрипция"),
    "stage.translate": ("Translation", "Перевод"),
    "stage.validate": ("Checking results", "Проверка результатов"),
    "stage.export": ("Tables", "Таблицы"),
    "stage.cards": ("Cards", "Карточки"),
    # Dialogs
    "help.title": ("Help — LexiRead Greek", "Справка — LexiRead Greek"),
    "help.heading": ("Help", "Справка"),
    "help.video": ("Video guide", "Видеоинструкция"),
    "tip.video": ("Video guide to the original WordByHeart app on YouTube", "Видеоинструкция оригинального приложения WordByHeart на YouTube"),
    "tip.github": ("Project repository and license", "Ссылка на репозиторий проекта и лицензию"),
    "install.title": ("Installing {gen}", "Установка {gen} языка"),
    "install.prompt": (
        "Building word lists for {gen} texts requires additional components",
        "Для создания списка слов для {gen} языка необходимо установить дополнительные библиотеки",
    ),
    "install.button": ("Install {acc}", "Установить {acc}"),
    "install.error_title": ("Installing {acc}", "Установка: {acc}"),
    "install.start_failed": ("Could not start the installer.", "Не удалось запустить установку."),
    "install.failed": (
        "Could not install the additional components. Details are saved in logs/setup.log.",
        "Не удалось установить дополнительные компоненты. Подробности сохранены в logs/setup.log.",
    ),
    "api.heading": ("Enter your OpenAI API key", "Введите OpenAI API key"),
    "api.saved_to": ("The key will be saved to:\n{path}", "Ключ будет сохранён в:\n{path}"),
    "api.enter": ("Enter an API key.", "Введите API key."),
    "api.save_failed": ("Could not save the API key.", "Не удалось сохранить API key."),
    "api.required": ("Enter an API key or turn off LLM translation.", "Введите API key или отключите перевод через модель."),
    "api.windows_only": (
        "Saving the key is supported only on Windows; the key is used for this run only.",
        "Сохранение ключа поддерживается только в Windows; используйте ключ для этого запуска.",
    ),
    "dialog.browse_title": ("Choose a book or subtitles", "Выберите текст книги"),
    "dialog.books": ("Books and subtitles", "Книги и субтитры"),
    "dialog.all_files": ("All files", "Все файлы"),
    "err.settings_title": ("Settings", "Настройки"),
    "err.settings": (
        "Coverage: 0 to 100%. Threshold: a whole number from 1 to 1000; 0 turns off selection by specificity. "
        "Occurrences: a whole number from 1 to 1,000,000.",
        "Покрытие: от 0 до 100%. Порог: целое число от 1 до 1000; 0 отключает отбор по специфичности. "
        "Количество вхождений: целое число от 1 до 1 000 000.",
    ),
    "err.start_title": ("Could not start", "Не удалось начать"),
    "err.file_access": ("Could not open or save a file. Check access permissions.", "Не удалось открыть или сохранить файл. Проверьте права доступа."),
    "err.results_title": ("Results", "Результаты"),
    "err.open_result": (
        "Could not open the result. Check that the file exists and a program is installed for it.",
        "Не удалось открыть результат. Проверьте, что файл существует и для него установлена программа.",
    ),
    "close.title": ("Stop the analysis?", "Остановить анализ?"),
    "close.text": ("The analysis is still running. Stop it and close the window?", "Обработка ещё идёт. Остановить её и закрыть окно?"),
    # Configuration
    "cfg.choose_file": ("Choose an existing file: {formats}.", "Выберите существующий файл: {formats}."),
    "cfg.empty_file": ("The selected file is empty.", "Выбранный файл пуст."),
    "cfg.choose_language": ("Choose English, Español or Ελληνικά.", "Выберите English, Español или Ελληνικά."),
    "cfg.no_template": (
        "The card template was not found. Restore table.docx in the application folder.",
        "Не найден шаблон карточек. Восстановите ваш table.docx в корне приложения.",
    ),
    "cfg.no_known": (
        "The known-words list was not found. Turn off excluding known words.",
        "Не найден список известных слов. Отключите исключение известных слов.",
    ),
    # Worker and process errors
    "err.encoding": ("Could not read the text. Save the TXT file in UTF-8.", "Не удалось прочитать текст. Сохраните TXT в кодировке UTF-8."),
    "err.nlp": ("Text analysis failed. Run INSTALL.bat to check the NLP model.", "Не удалось выполнить анализ текста. Запустите INSTALL.bat для проверки NLP-модели."),
    "err.ipa": ("Transcription failed. Run INSTALL.bat to check eSpeak NG.", "Не удалось создать транскрипцию. Запустите INSTALL.bat для проверки eSpeak NG."),
    "err.translate": (
        "LLM translation failed. Check the API key, model access and the internet connection.",
        "Не удалось выполнить перевод через модель. Проверьте API key, доступ к модели и интернет.",
    ),
    "err.permission": (
        "No access to a file. Close open tables and cards and run again.",
        "Нет доступа к файлу. Закройте открытые таблицы и карточки и повторите запуск.",
    ),
    "err.generic": ("Processing failed. Details are saved in logs/lexiread.log.", "Не удалось завершить обработку. Подробности сохранены в logs/lexiread.log."),
    "err.process_stopped": (
        "The processing stopped. Run INSTALL.bat to check the installation.",
        "Процесс обработки остановлен. Запустите INSTALL.bat для проверки установки.",
    ),
    "err.action_failed": ("The action failed. Details: logs/lexiread.log.", "Не удалось выполнить действие. Подробности: logs/lexiread.log."),
    "err.app_start": (
        "Could not start LexiRead Greek. Run INSTALL.bat to repair the installation.",
        "Не удалось запустить LexiRead Greek. Запустите INSTALL.bat для восстановления установки.",
    ),
    # Source files
    "fmt.unsupported": ("The {suffix} format is not supported. Supported: {formats}", "Формат {suffix} не поддерживается. Поддерживаются: {formats}"),
    "fmt.corrupt": ("The file {name} is damaged or is not {kind}.", "Файл {name} повреждён или не является {kind}."),
    "fmt.no_text": ("No text was found in {name}.", "В файле {name} не найден текст."),
    "fmt.encrypted": ("The PDF {name} is password-protected.", "PDF {name} защищён паролем."),
    "fmt.pdf_broken": ("Could not read the PDF {name}: the file is damaged.", "Не удалось прочитать PDF {name}: файл повреждён."),
    "fmt.scan": (
        "The PDF {name} has almost no text layer; it is probably a scan. "
        "Recognize the text (OCR) and save the book as TXT, EPUB or a PDF with text.",
        "В PDF {name} почти нет текстового слоя — вероятно, это скан. "
        "Распознайте текст (OCR) и сохраните книгу в TXT, EPUB или PDF с текстом.",
    ),
    "fmt.garbled": (
        "The text of the PDF {name} comes out as wrong characters (fonts without a Unicode map). "
        "Open the file in Calibre or Word and save it as TXT or EPUB.",
        "Текст PDF {name} извлекается неверными символами (шрифты без таблицы Unicode). "
        "Откройте файл в Calibre или Word и сохраните как TXT или EPUB.",
    ),
    # Installer (scripts/setup.py)
    "setup.downloaded": ("Downloaded {done:.1f} MB", "Загружено {done:.1f} МБ"),
    "setup.downloaded_of": (" of {total:.1f} MB ({share:.0%})", " из {total:.1f} МБ ({share:.0%})"),
    "setup.kill_failed": ("Could not stop the process tree {pid}", "Не удалось завершить дерево процесса {pid}"),
    "setup.pip_timeout": ("Updating pip timed out; using the installed version.", "Превышено время обновления pip; используется установленная версия."),
    "setup.pip_warning": ("Warning: pip could not be updated. Installation continues with pip {version}.", "Предупреждение: pip не удалось обновить. Установка продолжится с pip {version}."),
    "setup.libs_ready": ("Libraries are already installed.", "Библиотеки уже установлены."),
    "setup.libs_failed": ("Could not install the dependencies. Check the connection to PyPI and free disk space.", "Не удалось установить зависимости. Проверьте подключение к PyPI и свободное место."),
    "setup.repairing": ("Repairing damaged libraries...", "Восстановление повреждённых библиотек..."),
    "setup.repair_failed": ("Could not repair the libraries. Details: logs/setup.log.", "Не удалось восстановить библиотеки. Подробности: logs/setup.log."),
    "setup.imports_failed": ("Import checks fail. Details: logs/setup.log.", "Не проходят проверки импортов. Подробности: logs/setup.log."),
    "setup.conflict": ("Dependency conflict detected: logs/setup.log.", "Обнаружен конфликт зависимостей: logs/setup.log."),
    "setup.model_ready": ("{model}: ready.", "{model}: готово."),
    "setup.model_installing": ("Installing/repairing {model}...\nThe model is large. Download progress is shown below.", "Установка/восстановление {model}...\nМодель имеет большой размер. Ход загрузки будет показан ниже."),
    "setup.model_failed": ("Could not install {model}. Check access to github.com/explosion/spacy-models.", "Не удалось установить {model}. Проверьте доступ к github.com/explosion/spacy-models."),
    "setup.model_broken": ("The model {model} does not load. Details: logs/setup.log.", "Модель {model} не загружается. Подробности: logs/setup.log."),
    "setup.unsafe_redirect": ("The eSpeak download was redirected to an insecure URL.", "Загрузка eSpeak перенаправлена на небезопасный URL."),
    "setup.espeak_ready": ("eSpeak NG: transcription checked.", "eSpeak NG: транскрипция проверена."),
    "setup.espeak_system": ("Install eSpeak NG system-wide; automatic installation is for Windows only.", "Установите системный eSpeak NG; автоматическая установка предназначена для Windows."),
    "setup.espeak_download": ("Downloading the official eSpeak NG 1.52.0...", "Загрузка официального eSpeak NG 1.52.0..."),
    "setup.espeak_failed": (
        "Could not unpack/run eSpeak NG automatically. Open .local/downloads/espeak-ng-1.52.0.msi for a standard "
        "installation (Windows may ask for administrator rights), then run INSTALL.bat again.",
        "Не удалось распаковать/запустить eSpeak NG автоматически. Откройте .local/downloads/espeak-ng-1.52.0.msi "
        "для стандартной установки (Windows может запросить права администратора), затем повторите INSTALL.bat.",
    ),
    "setup.kaikki_failed": ("Could not install Kaikki. Check the internet connection and run INSTALL.bat again.", "Не удалось установить Kaikki. Проверьте интернет и повторите INSTALL.bat."),
    "setup.check_help": ("Checks only, without downloading or installing", "Проверки без скачивания и установки"),
    "setup.deps_not_ready": ("Python dependencies are not ready.", "Не готовы Python-зависимости."),
    "setup.model_not_ready": ("The model {model} is not ready.", "Не готова модель {model}."),
    "setup.espeak_not_ready": ("eSpeak NG is not ready.", "Не готов eSpeak NG."),
    "setup.language_not_ready": ("Language resources are not installed: {language}.", "Не установлены ресурсы языка: {language}."),
    "setup.use_installer": ("Use INSTALL.bat: setup must run inside .venv.", "Используйте INSTALL.bat: установка должна выполняться внутри .venv."),
    "setup.step_libs": ("Checking libraries", "Проверка библиотек"),
    "setup.step_model": ("Checking the NLP model", "Проверка NLP-модели"),
    "setup.step_espeak": ("Checking eSpeak NG", "Проверка eSpeak NG"),
    "setup.step_kaikki": ("Installing Kaikki dictionaries", "Установка словарей Kaikki"),
    "setup.step_gui": ("[7/7] Checking the interface...", "[7/7] Проверка интерфейса..."),
    "setup.gui_failed": ("Could not open the GUI. Check Tcl/Tk.", "Не удалось открыть GUI. Проверьте Tcl/Tk."),
    "setup.error": ("Error: {error}", "Ошибка: {error}"),
}

HELP = {
    "en": """        LexiRead Greek (Learn by reading) is a modified version of the WordByHeart app (by Egor Tatarnikov) with support for Greek. It prepares the vocabulary you need to read a particular book or watch a particular series in a foreign language.
        The app turns a text into a ready set of words to learn and review.


        Quick start

        1. Choose a book or subtitles file: TXT, EPUB, FB2, DOCX, PDF with text, SRT, VTT, ASS (demo_el.txt is already selected for a test run).
        2. Click "Start analysis".
        3. Open "Word list", "Cards", "Summary table" and "Results folder".

        The word list contains the words to learn for comfortable reading of the book in a foreign language.

        Cards are the words from the list laid out in an 8 x 3 table, 24 cards per sheet. The file is prepared for double-sided printing: print the front sides of all sheets first, then turn the paper over and print the back sides. After cutting you get double-sided cards for learning and reviewing words.

        The summary table contains the lemmas and word forms recognized in the text with their frequency, translations, transcription, grammar information and notes. It is useful for further analysis of the text.

        The results folder keeps all output files.


        Detailed instructions

        1. Choose a file with a text in a foreign language. Books: TXT, EPUB, FB2 (including .fb2.zip), DOCX, PDF with a text layer. Subtitles: SRT, VTT, ASS/SSA. For TXT files UTF-8 is recommended; other common encodings, including Windows-1253 for Greek, are detected automatically. Scanned PDFs without recognized text are not supported.

        2. Choose the language of the text. The app supports Greek, English and Spanish.

        3. By default words are translated with the local Kaikki dictionary. LLM translation can be turned on if needed; it requires an OpenAI API key.

        4. If you have lists of words you already know, put them into the dictionaries in the application folder (my_dictionary_el.xlsx for Greek, my_dictionary_en.xlsx for English, my_dictionary_es.xlsx for Spanish). A few words are already there as an example.
        A word from your dictionary found in the book is not translated and is not included in the word lists and study cards. It still stays in the summary table.

        5. Advanced settings limit the selection of words with "Text coverage", "Specificity threshold" and "Minimum occurrences".
        Defaults:

        Text coverage: 90%. The list includes the most frequent words that together cover 90% of the text. Range: 0 to 100.

        Specificity threshold: 20. The list also includes words outside the coverage range that occur in this text 20 or more times more often than in other texts on average. Handy for diving into subject areas with many special terms. Range: 1 to 1000. With 0 specificity is not used.

        Minimum occurrences: 4. A word must occur in the text at least four times to get into the list, even if it meets the coverage or specificity settings. Range: 1 to 1,000,000.

        6. Click "Start analysis". Processing time depends on the size of the text and the translation method. With Kaikki it usually takes a few minutes; LLM translation can take much longer, especially for a large book.

        7. Study the results.


        How it works

        After you choose a text, the app processes it in several stages.

        Preprocessing. The text is loaded, cleaned and prepared. For Greek, old encodings are read, polytonic spelling is converted to monotonic and elisions are expanded. A long text is split into small chunks so that even a large book can be processed.

        NLP analysis. The spaCy model finds sentences, words, base forms (lemmas), parts of speech and grammatical features. For Greek, lemmas are checked against Wiktionary word forms (Kaikki).

        Frequency analysis. The app collects lemmas, word forms and usage examples, and counts word frequencies and text coverage.

        Specificity. The frequency of a word in this text is compared with its usual frequency in the language (the wordfreq library). Specificity shows how much more often the word occurs in this text, which highlights words especially important for it.

        Postprocessing. The results are cleaned and merged so that words appear in a form convenient for learning.

        Grammar. The app adds information useful for learning. For Greek nouns these are the article, genitive and plural; for adjectives the three genders; for verbs the aorist.

        Transcription (IPA). eSpeak NG creates the transcriptions.

        Translation. By default words are translated with the local Kaikki dictionary. LLM translation is possible: the model receives the word with its usage examples, part of speech and word forms, so translations follow the context.

        Validation. The app checks the results and marks possible problems, such as a missing translation or transcription, a doubtful word form or an analysis error. Such words go into a separate list for review.

        Results. The app creates summary tables with the dictionary, translations, transcription and grammar, as well as the word list and study cards.


        The idea

        The project grew out of a practical method: instead of the abstract goal of "learning a language", you set a concrete task — to read a book or watch a series.
        Learning a limited set of words that really matter for the chosen text lets you get to content in the foreign language sooner.
        Reading favorite books and watching series in the original is enjoyable, gives a sense of progress and keeps you motivated to go on learning.
""",
    "ru": """        LexiRead Greek (Learn by reading) – изменённая версия приложения WordByHeart (автор – Egor Tatarnikov) с поддержкой греческого языка. Это приложение для подготовки лексики к изучению, необходимой для прочтения конкретной книги или просмотра сериала на иностранном языке.
        Приложение создает из текста готовый набор слов для изучения и повторения.


        Краткая инструкция

        1. Выберите файл книги или субтитров: TXT, EPUB, FB2, DOCX, PDF с текстом, SRT, VTT, ASS (для тестового запуска уже выбран файл demo_el.txt).
        2. Нажмите «Начать анализ».
        3. Откройте «Список слов», «Карточки», «Сводную таблицу» и «Папку с результатами».

        Список слов – это слова, которые нужно выучить для комфортного чтения книги на иностранном языке.

        Карточки – это слова из списка, размещенные на листе в таблице 8х3. Один лист содержит 24 карточки. Файл подготовлен для двусторонней печати. Сначала распечатайте лицевые стороны всех листов, затем переверните бумагу и распечатайте обратные стороны. После разрезания получатся двусторонние карточки для изучения и повторения слов.

        Сводная таблица содержит леммы и словоформы, распознанные программой в тексте, а также их частоту, переводы, транскрипцию, грамматическую информацию и примечания. Она удобна для дополнительного анализа текста.

        В папке с результатами хранятся все результирующие файлы.


        Подробная инструкция

        1. Выберите файл с текстом на иностранном языке. Книги: TXT, EPUB, FB2 (в том числе .fb2.zip), DOCX, PDF с текстовым слоем. Субтитры: SRT, VTT, ASS/SSA. Для TXT рекомендуется кодировка UTF-8; другие распространённые кодировки, в том числе Windows-1253 для греческого, распознаются автоматически. PDF-сканы без распознанного текста не поддерживаются.

        2. Выберите язык, на котором написан текст. Приложение поддерживает греческий, английский и испанский языки.

        3. По умолчанию перевод слов выполняется через локальный словарь Kaikki. При необходимости можно включить перевод через языковую модель (LLM). Для этого потребуется API key OpenAI.

        4. Если у вас имеются списки слов, которые вы уже знаете, перенесите их в словари в папке приложения (my_dictionary_el.xlsx – для греческого, my_dictionary_en.xlsx – для английского, my_dictionary_es.xlsx – для испанского). Для примера в словари уже внесено несколько слов.
        Если слово из вашего словаря будет найдено в книге, оно не будет переводиться и не будет включаться в итоговые списки и карточки слов для изучения. При этом такие слова останутся в сводной таблице.

        5. Расширенные настройки. Установите ограничения для выбора слов параметрами «Покрытие текста», «Порог специфичности» и «Минимум вхождений в тексте».
        По умолчанию заданы следующие параметры:

        Покрытие текста – 90%. В список для изучения войдут наиболее частые слова, которые суммарно покрывают 90% текста. Допустимый диапазон значений: 0 - 100

        Порог специфичности – 20. Дополнительно в список войдут слова, которые не входят в диапазон покрытия текста, но встречаются в тексте в 20 и более раз чаще, чем в среднем в других текстах. Удобный инструмент для быстрого погружения в предметные области, где встречается много специализированной лексики и терминов. Допустимый диапазон значений: 1 - 1000. При значении 0 специфичность не учитывается для формирования списка слов к изучению.

        Минимум вхождений в тексте – 4. Слово должно встретиться в тексте не менее четырёх раз, чтобы попасть в список для изучения, даже если оно соответствует настройкам покрытия или специфичности. Допустимый диапазон значений: 1 - 1000000

        6. Нажмите «Начать анализ». Обработка текста зависит от его размера и выбранного способа перевода. При переводе через Kaikki она обычно занимает несколько минут. Перевод через LLM может занять существенно больше времени, особенно для большой книги.

        7. Изучите результат анализа.


        Описание работы приложения

        После выбора текста на иностранном языке программа выполняет обработку текста в несколько этапов.

        Предобработка. Исходный текст загружается, очищается и подготавливается к анализу. Для греческого читаются старые кодировки, политоника переводится в монотонику, раскрывается элизия. Длинный текст разбивается на небольшие фрагменты (чанки), чтобы программа могла корректно обработать даже большую книгу.

        NLP-анализ. Для проведения NLP-анализа используется модель spaCy. Она выделяет предложения, слова, начальные формы слов (леммы), части речи и грамматические признаки. Для греческого леммы проверяются по словоформам Викисловаря (Kaikki).

        Частотный анализ. Программа собирает леммы, словоформы, примеры использования слов, подсчитывает частоту слов и их покрытие текста.

        Оценка специфичности. Частота слова в данном тексте сравнивается с его обычной частотой в языке (библиотека wordfreq). Параметр «специфичность» показывает, насколько чаще слово встречается в этом тексте, и помогает выделить слова, особенно важные для конкретного текста.

        Постобработка текста. Программа очищает и объединяет результаты анализа, чтобы слова отображались в удобном для изучения виде.

        Грамматическое дополнение. Программа добавляет сведения, полезные для изучения слов. Для греческих существительных – артикль, родительный падеж и множественное число, для прилагательных – три рода, для глаголов – аорист.

        Транскрипция (IPA). Для создания транскрипций используется eSpeak NG.

        Перевод. Перевод слов по умолчанию выполняется через локальный словарь Kaikki. Имеется возможность подключить перевод через LLM: в модель передаётся не только слово, но и примеры его использования в тексте, часть речи и словоформы, что позволяет переводить слова с учётом контекста.

        Валидация результата. Программа проверяет результаты обработки и отмечает возможные проблемы. Например, если программа находит отсутствующий перевод или транскрипцию, сомнительную форму слова, неоднозначность или ошибку автоматического анализа, то такие слова попадают в отдельный список для проверки.

        Подготовка результатов. Программа создаёт итоговые таблицы со словарём, переводами, транскрипцией и грамматической информацией, а также список слов и карточки для изучения.


        Описание идеи

        Проект вырос из практической методики, где вместо абстрактной цели «выучить язык» ставится конкретная задача - прочитать книгу или посмотреть сериал.
        Изучение ограниченного набора слов, которые действительно важны для понимания выбранного текста, позволяет быстрее перейти к контенту на иностранном языке.
        Чтение любимых книг и просмотр сериалов в оригинале приносят удовольствие, дают ощущение прогресса и поддерживают мотивацию к дальнейшему изучению языка.
""",
}


def _system_language():
    """Russian for a Russian Windows interface, English otherwise."""
    try:
        import ctypes

        return "ru" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x19 else "en"
    except (AttributeError, OSError):
        return "ru" if os.environ.get("LANG", "").lower().startswith("ru") else "en"


def _load():
    if os.environ.get(ENV) in LANGUAGES:
        return os.environ[ENV]
    try:
        saved = json.loads(SETTINGS.read_text(encoding="utf-8")).get("ui_language")
    except (OSError, ValueError):
        saved = None
    return saved if saved in LANGUAGES else _system_language()


_current = None


def get_language():
    global _current
    if _current is None:
        _current = _load()
    return _current


def set_language(language, save=True):
    global _current
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported interface language: {language}")
    _current = language
    os.environ[ENV] = language
    if save:
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8")) if SETTINGS.is_file() else {}
        except (OSError, ValueError):
            settings = {}
        settings["ui_language"] = language
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


def t(key, **values):
    text = TEXT[key][LANGUAGES.index(get_language())]
    return text.format(**values) if values else text


def language_forms(code):
    return LANGUAGE_FORMS[get_language()][code]


def help_text():
    return HELP[get_language()]
