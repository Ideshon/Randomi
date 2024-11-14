# Randomi

Text randomizer.

## Functions

$RANDWORDS(min, max, word1, word2, ...)
This function will accept minimum, maximum and a list of words from which to select a random number. 

$MULTIPLY(word, count) 
This function will repeat the word the required number of times. 

Delimeter changes the "|" to the specified character.
Function delimiter changes "," to the specified character.

Try not to use service symbols.

The Synonyms command - {variant1 | variant2 | variant3} - inserts one of the variants into the resulting string. If you want to skip the text, use the "empty" option - {|variant} Mixin command = [ text 1 | text 2 | text 3] - will randomly mix these options.

You can use the separator in mixin - [+,+text 1|text2 ] - you will get text2,text1. The separator can be any character or set of characters: [+==+ a|b] - a==b or b==a If you want to get a special character in your result ({, }, [, ], |, +) - use a backslash for it - {, }, [, ], |, +

All these commands can be mixed and nested in all combinations: 'start {aa|bb|{cc1|cc2}} or [a1|{word1|word2}|a3| [aa1|aa2|aa3]]' You can use special predefined randomization functions in templates - {random integer =$RANDINT(1.10), uuid = $UUID, now= $NOW(%Y-%M-%d)}. The result will be = 'random integer = 4, uuid = 8ae6bdf4-d321-40f6-8c3c-81d20b158acb, now = 2017-08-01' You can define your own randomization functions and use them in templates.

## Other
~~Automatic removal of extra spaces, commas and new lines. A double line makes a new line in the output.~~

Font size, bold font, reset formatting.

Resizing windows.

Saving and loading. 

Auto-save on exit.

Search and replace in the text.

# Randomi

Рандомизатор текста.

## Функции

$RANDWORDS(min, max, word1, word2, ...) 
Эта функция будет принимать минимум, максимум и список слов, из которых нужно выбрать случайное количество. 

$MULTIPLY(word, count) 
Эта функция будет повторять слово нужное количество раз. 

Delimeter меняет "|" на указанный символ.
Function delimeter меняет "," на указанный символ.

Старайтесь не использовать служебные символы.

Команда "Синонимы" - {variant1 | variant2 | variant3} - вставляет один из вариантов в результирующую строку. Если вы хотите пропустить текст - используйте вариант "пусто" - {|variant} Команда Mixin = [ текст 1 | текст 2 | текст 3] - будет случайным образом миксовать эти варианты.

Вы можете использовать разделитель в mixin - [+,+text 1|text2 ] - вы получите text2,text1. Разделитель может быть любым символом или набором символов: [+==+ a|b] - a==b или b==a Если вы хотите получить специальный символ в вашем результате ({, }, [, ], |, +) - используйте обратный слеш для него - {, }, [, ], |, +

Все эти команды могут быть смешаны и вложены во все комбинации: 'начало {aa|bb|{cc1|cc2}} или [a1|{word1|word2}|a3| [aa1|aa2|aa3]]' Вы можете использовать специальные предопределенные функции рандомизации в шаблонах - {случайное целое = $RANDINT(1,10), uuid = $UUID, сейчас = $NOW(%Y-%M-%d)}. Результат будет = 'случайное целое = 4, uuid = 8ae6bdf4-d321-40f6-8c3c-81d20b158acb, сейчас = 2017-08-01' Вы можете определить свои собственные функции рандомизации и использовать их в шаблонах

## Прочее
~~Автоматическое удаление лишних пробелов, запятых и новых строк. Двойная строка делает новую строку в выводе.~~

Размер шрифта, жирный шрифт, сброс форматирования.

Изменения размеров окон.

Сохранение и загрузка. 

Автосохранение при выходе.

Поиск и замена в тексте.
