import unittest
from src.comment_remover.comment_remover import CommentRemover
from src.comment_remover.multi_line_comment_signs import CommentSign


class CommentRemoverTest(unittest.TestCase):
    def test_single_row_comment_remove(self):
        text = [
            '  123 f/ fd /* fds */\n',
            ' , \t // some text \t\n',
            '\t \t  // dffffw\n',
            '///dewfrr'
        ]
        expected_result = [
            '  123 f/ fd /* fds */\n',
            ' , \t \n'
        ]
        deleted_rows = {
            2: '\t \t  // dffffw\n',
            3: '///dewfrr'
        }
        deleted_row_fragments = {
            1: {
                5: '// some text \t'
            }
        }
        remover = CommentRemover(single_row_sign='//')
        remover.remove_single_row_comment(text)
        remover.remove_marked_rows(text)
        self.assertTrue(text == expected_result)
        self.assertTrue(remover.deleted_rows_map == deleted_rows)
        self.assertTrue(remover.deleted_row_fragments == deleted_row_fragments)

    def test_multi_row_comment_remove(self):
        text = [
             '\ttext without comment\n',
             '    /*[Attribute]*/class declaration\n',
             # all commented lines must be removed (first one will be empty)
             '    /* bla-bla 12\n',
             '\tsome //text\n',
             '\tsome another text*/\n',
             # all commented lines must be removed (last one will be empty)
             '/* commented text\n',
             'hey!*/ \n',
             # text before and '''  '''after comments must remain
             'something here /* commented text\n',
             '\tstill commented text\n',
             'again commented*/ something important\n',
             # remove 2 times commented text
            '\t/*commented*/ not-commented /*commented again */ visible text\n',
             # remove 1 comment on several rows and again in last row
            'start here /* start comment here\n',
            'end comment here*/ middle text /*some comment again*/ one more text /*last comment*/ end of text\n',
            # new line symbol must remain
            '/*123456789*/\n',
            'text /*commented text*/',
        ]
        expected_result = [
            '\ttext without comment\n',
            '    class declaration\n',
            'something here \n',
            ' something important\n',
            '\t not-commented  visible text\n',
            'start here \n',
            ' middle text  one more text  end of text\n',
            'text '
        ]
        deleted_rows = {
            2: '    /* bla-bla 12\n',
            3: '\tsome //text\n',
            4: '\tsome another text*/\n',
            5: '/* commented text\n',
            6: 'hey!*/ \n',
            8: '\tstill commented text\n',
            13: '/*123456789*/\n'
        }
        deleted_row_fragments = {
            1: {
                4: '/*[Attribute]*/'
            },
            7: {
                15: '/* commented text'
            },
            9: {
                0: 'again commented*/'
            },
            10: {
                1: '/*commented*/',
                29: '/*commented again */'
            },
            11: {
                11: '/* start comment here'
            },
            12: {
                0: 'end comment here*/',
                31: '/*some comment again*/',
                68: '/*last comment*/'
            },
            14: {
                5: '/*commented text*/'
            }
        }

        multi_row_comment_signs = [
            { CommentSign.Left: '/*', CommentSign.Right: '*/' }
        ]
        remover = CommentRemover()
        remover.remove_multi_row_comment(text, multi_row_comment_signs[0])
        remover.remove_marked_rows(text)
        self.assertTrue(text == expected_result)
        self.assertTrue(remover.deleted_rows_map == deleted_rows)
        self.assertTrue(remover.deleted_row_fragments == deleted_row_fragments)

    def test_remove_all_comments_from_file(self):
        in_file = open('file_with_comments.txt', 'r')
        text = in_file.readlines()
        # in_file.close

        out_file = open('expected_result.txt', 'r')
        expected_result = out_file.readlines()
        # out_file.close

        # TODO: restore deleted text after removing

        remover = CommentRemover(single_row_sign='//', multi_row_sign_left='/*', multi_row_sign_right='*/')
        remover.add_multi_row_comment_sign(left='@*', right='*@')
        remover.add_multi_row_comment_sign(left='<!--', right='-->')
        remover.remove_all_comments(text)

        result = open('result.txt', 'w')
        for line in text:
            result.write(line)
        result.close()
        self.assertTrue(text == expected_result)


if __name__ == '__main__':
    unittest.main()
