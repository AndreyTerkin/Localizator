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
        remover = CommentRemover(single_row_sign='//')
        remover.remove_single_row_comment(text)
        self.assertTrue(text == expected_result)

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
            # text before and after comments must remain
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
        remover = CommentRemover(multi_row_sign_left='/*', multi_row_sign_right='*/')
        remover.remove_multi_row_comment(text)
        self.assertTrue(text == expected_result)


if __name__ == '__main__':
    unittest.main()
