import unittest
from ddt import ddt, data
from src.localizator.language_words_searcher import LanguageWordsSearcher


@ddt
class LanguageWordsSearcherTest(unittest.TestCase):
    @data(
        (
            '<text class="style">Тут к№акой-то те(к)ст</text><p>Тут снова:текст, с. другими: знакам!и препи?нания</p>',
            [
                (20, 41, 'Тут к№акой-то те(к)ст'),
                (51, 100, 'Тут снова:текст, с. другими: знакам!и препи?нания')
            ]
        ),
        (
            '\t\t\t    { Name = "Название", ErrorMessage = "Тут произошла шибка!" , SuccessMessage ="Добавление прошло успешно" }',
            [
                (17, 25, 'Название'),
                (44, 64, 'Тут произошла шибка!'),
                (85, 110, 'Добавление прошло успешно')
            ]
        ),
        (
            '    <p>На этом тексте  кончается строка\n',
            [(7, 39, 'На этом тексте  кончается строка')]
        )
    )
    def test_find_words_in_line(self, data):
        searcher = LanguageWordsSearcher()
        fragments = searcher.find_words_in_line(data[0])
        self.assertTrue(data[1] == fragments)


if __name__ == '__main__':
    unittest.main()