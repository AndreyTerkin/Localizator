import os
import collections

from src.comment_remover.comment_remover import CommentRemover
from src.localizator.code_editor import CodeEditor
from src.localizator.resource_file_manager import XMLEditor
from src.localizator.language_words_searcher import LanguageWordsSearcher


class Localizator():
    def __init__(self, project_folder, project_file):
        self._project_folder = project_folder
        self._project_file = project_file

    def localize_datamodel(self, init_dir, entity_type, black_list):
        if not os.path.exists(init_dir):
            return

        if os.path.isfile(init_dir) and init_dir.endswith('.cs'):
            self._localize_datamodel_file(init_dir, entity_type)

        folders = os.listdir(init_dir)
        for item in folders:
            if item in black_list:
                continue

            item = os.path.join(init_dir, item)
            if os.path.isdir(item):
                self.localize_datamodel(item, entity_type, black_list)
            elif os.path.isfile(item) and item.endswith('.cs'):
                file = os.path.join(self._project_folder, item)
                self._localize_datamodel_file(file, entity_type)

    def _localize_datamodel_file(self, file, entity_type):
        file_path_relate_to_proj = os.path.relpath(file, self._project_folder)
        related_path = os.path.dirname(file_path_relate_to_proj)

        code_editor = CodeEditor(related_path)
        entity_name = code_editor.add_resources_to_entity(file, entity_type)
        if entity_name is None:
            return
        # TODO: check if resources already created
        properties = code_editor.properties
        XMLEditor.create_resources(self._project_folder, self._project_file, related_path, entity_name, properties)
        print('-' * 20)

    def localize_view_file(self, file):
        # Store and remove comments
        deleted_rows, deleted_fragments = self._remove_comments(file)
        # Find all words in Russian # Create resource files and fill them
        self._replace_literal_constants_by_resources(file)
        # Replace them by constructions with Resources
        # Restore deleted comments
        self._restore_comments(file, deleted_rows, deleted_fragments)
        # TODO: handle cases (like in Sample/Test.cshtml):
        # 1) string.Format("Текст {0} другой текст", arg0);
        # 2) ViewContext.Writer.Write(@"<div class=""alert"">Текст {0} продолжение текста</div>", arg0);
        pass

    def _remove_comments(self, file):
        f = open(file, 'r+')
        text = f.readlines()
        comment_remover = CommentRemover(single_row_sign='//',
                                         multi_row_sign_left='/*',
                                         multi_row_sign_right='*/')
        comment_remover.add_multi_row_comment_sign(left='@*', right='*@')
        comment_remover.add_multi_row_comment_sign(left='<!--', right='-->')
        comment_remover.remove_all_comments(text)
        f.seek(0)
        f.truncate()
        for line in text:
            f.write(line)
        return comment_remover.deleted_rows_map,\
               comment_remover.deleted_row_fragments

    def _restore_comments(self, file, deleted_rows, deleted_fragments):
        f = open(file, 'r+')
        text = f.readlines()
        sorted_dict = collections.OrderedDict(sorted(deleted_rows.items()))
        for deleted_row in sorted_dict:
            text.insert(deleted_row, sorted_dict[deleted_row])
        for deleted_fragment in deleted_fragments:
            for chunk in deleted_fragments[deleted_fragment]:
                text[deleted_fragment] = text[deleted_fragment][:chunk] + \
                                         deleted_fragments[deleted_fragment][chunk] + text[deleted_fragment][chunk:]
        f.seek(0)
        f.truncate()
        for line in text:
            f.write(line)

    def _replace_literal_constants_by_resources(self, file):
        f = open(file, 'r+', encoding='utf-8-sig')
        text = f.readlines()
        f.close()
        searcher = LanguageWordsSearcher()
        text_fragments = searcher.find_all_text_fragments(text)
        properties = self._extract_list_of_properties(text_fragments)
        xml_editor = XMLEditor()
        xml_editor.create_resource_file(properties, "C:\\Projects\\Scripts\\Localizator\\samples")

    def _extract_list_of_properties(self, text_fragments):
        properties = []
        counter = 0
        for row_index in text_fragments:
            for fragment in text_fragments[row_index]:
                properties.append(('Property{0}'.format(counter), fragment[2]))
                counter += 1
        return properties
