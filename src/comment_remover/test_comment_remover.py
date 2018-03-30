import unittest
from src.comment_remover.comment_remover import CommentRemover


class CommentRemoverTest(unittest.TestCase):
    def test_single_row_comment_remove(self):
        text = [
            '  123 f/ fd /* fds */',
            ' , \t // some text \t',
            '\t \t  // dffffw',
            '///dewfrr'
        ]
        expected_result = [
            '  123 f/ fd /* fds */',
            ' , \t '
        ]
        deleted_rows = {
            2: '\t \t  // dffffw',
            3: '///dewfrr'
        }
        deleted_row_fragments = {
            1: {
                5: '// some text \t'
            }
        }
        remover = CommentRemover(text, single_row_sign='//')
        remover.remove_single_row_comment()
        self.assertTrue(text == expected_result)
        self.assertTrue(remover.deleted_rows_map == deleted_rows)
        self.assertTrue(remover.deleted_row_fragments == deleted_row_fragments)

    def test_multi_row_comment_remove(self):
        text = [
             '\ttext without comment\n',
             '    /*[Attribute]*/class declaration',
             # TODO: text with several occurrences of multi row comment in same line
             # all commented lines must be removed (first one will be empty)
             '    /* bla-bla 12',
             '\tsome //text',
             '\tsome another text*/',
             # all commented lines must be removed (last one will be empty)
             '/* commented text',
             'hey!*/ ',
             # text before and '''  '''after comments must remain
             'something here /* commented text',
             '\tstill commented text',
             'again commented*/ something important',
             # remove 2 times commented text
            '\t/*commented*/ not-commented /*commented again */ visible text',
             # remove 1 comment on several rows and again in last row
            'start here /* start comment here',
            'end comment here*/ middle text /*some comment again*/ one more text /*last comment*/ end of text'
        ]
        expected_result = [
            '\ttext without comment\n',
            '    class declaration',
            'something here ',
            ' something important',
            '\t not-commented  visible text',
            'start here ',
            ' middle text  one more text  end of text'
        ]
        deleted_rows = {
            2: '    /* bla-bla 12',
            3: '\tsome //text',
            4: '\tsome another text*/',
            5: '/* commented text',
            6: 'hey!*/ ',
            8: '\tstill commented text',
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
            }
        }
        remover = CommentRemover(text, multi_row_sign_left='/*', multi_row_sign_right='*/')
        remover.remove_multi_row_comment()
        self.assertTrue(text == expected_result)
        self.assertTrue(remover.deleted_rows_map == deleted_rows)
        self.assertTrue(remover.deleted_row_fragments == deleted_row_fragments)


if __name__ == '__main__':
    unittest.main()
