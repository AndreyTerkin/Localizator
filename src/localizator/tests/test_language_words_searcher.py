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
    def test_find_words_in_line(self, test_data):
        searcher = LanguageWordsSearcher()
        fragments = searcher.find_words_in_line(test_data[0])
        self.assertTrue(test_data[1] == fragments)

    def test_find_all_text_fragments(self):
        text = [
            '@{\n',
            '\tvar context = (IDbContext)ViewBag.Context;\n',
            '\tvar reportList = new List<string>() { "Отчёт №1", "Другой отчет", "Отчет для отчетности" };\n',
            '}\n',
            '<a href="#" class="btn btn-default btn-xs custom-button" data-id="@order.IdOrder"\n',
            '\tdata-trigger="addsample" title="Создать новую пробу">Добавить пробу\n',
            '</a>\n',
            '@Helpers.DxGrid(Model.Items, settings =>\n',
            '{\n',
            '\tsettings.SettingsText.GroupPanel = "Испытания для пробы";\n',
            '\tettings.Columns.Add(column =>\n',
            '    {\n',
            '    \tcolumn.FieldName = "IdTest2TestPlan";\n',
            '\t\tcolumn.Caption = "Код";\n',
            '\t\tcolumn.Visible = false;\n',
            '\t});\n',
            '\n',
            '\tsettings.Columns.Add(column =>\n',
            '\t{\n',
            '        column.FieldName = "Sample2Test.IdWorkGroup";\n',
            '\t    column.Caption = "Лаборатория / Рабочая группа";\n',
            '    }\n',
            '}\n',
            '<script>',
            '\t$(function () {\n',
            '\t\t$(document).on(\'addsample\', function (e, data) {\n',
            '\t\t\t$.post(\n',
            '\t\t\t\t\'@Url.Action("CreateSample", "Sample")\n',
            '\t\t\t\t{ orderId: data.id }\n',
            '\t\t\t).done(function () {\n',
            '\t\t\t\tdata.control.PerformCallback();\n',
            '\t\t\t}).fail(function () {\n',
            '\t\t\t\talert(\'Произошла ошибка!\');\n',
            '\t\t\t});\n',
            '\t\t});\n',
            '\t});\n',
            '</script>'
        ]
        expected_result = {
            2: [
                (40, 48, 'Отчёт №1'),
                (52, 64, 'Другой отчет'),
                (68, 88, 'Отчет для отчетности')
            ],
            5: [
                (33, 52, 'Создать новую пробу'),
                (54, 68, 'Добавить пробу')
            ],
            9: [
                (37, 56, 'Испытания для пробы')
            ],
            13: [
                (20, 23, 'Код')
            ],
            20: [
                (23, 51, 'Лаборатория / Рабочая группа')
            ],
            32: [
                (11, 28, 'Произошла ошибка!')
            ]
        }
        searcher = LanguageWordsSearcher()
        fragments = searcher.find_all_text_fragments(text)
        self.assertTrue(expected_result == fragments)


if __name__ == '__main__':
    unittest.main()
