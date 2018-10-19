import os
import collections

from src.comment_remover.comment_remover import CommentRemover
from src.localizator.code_editor import CodeEditor
from src.localizator.resource_file_manager import XMLEditor
from src.localizator.language_words_searcher import LanguageWordsSearcher


class Localizator:
    def __init__(self, project_file):
        self._project_folder = os.path.dirname(project_file)
        self._project_file = project_file

    def localize_datamodel(self, init_dir, entity_type, black_list):
        if not os.path.exists(init_dir):
            return

        if os.path.isfile(init_dir) and init_dir.endswith('.cs'):
            self.localize_datamodel_file(init_dir, entity_type)

        folders = os.listdir(init_dir)
        for item in folders:
            if item in black_list:
                continue

            item = os.path.join(init_dir, item)
            if os.path.isdir(item):
                self.localize_datamodel(item, entity_type, black_list)
            elif os.path.isfile(item) and item.endswith('.cs'):
                file = os.path.join(self._project_folder, item)
                self.localize_datamodel_file(file, entity_type)

    def localize_datamodel_file(self, file, entity_type):
        file_path_relate_to_proj = os.path.relpath(file, self._project_folder)
        related_path = os.path.dirname(file_path_relate_to_proj)
        # deleted_rows, deleted_fragments = self._remove_comments(file)
        code_editor = CodeEditor(related_path)
        entity_name = code_editor.add_resources_to_entity(file, entity_type)
        # self._restore_comments(file, deleted_rows, deleted_fragments)
        if entity_name is None:
            return
        # TODO: check if resources already created
        properties = code_editor.properties
        XMLEditor.create_resources(self._project_file, related_path, entity_name, properties)
        print('-' * 20)

    def localize_view_file(self, root_directory, file, output_projects):
        file_path_relate_to_root = os.path.relpath(file, root_directory)
        additional_path = os.path.dirname(file_path_relate_to_root)
        file_name = os.path.basename(file)
        entity_name = os.path.splitext(file_name)[0]
        resource_namespace = 'Resources.{0}.{1}'.format(additional_path.replace('\\', '.'), entity_name)

        deleted_rows, deleted_fragments = self._remove_comments(file)
        # TODO: sometimes there is no changes in file where it really are
        properties = self._replace_literal_constants_by_resources(file, resource_namespace)
        self._restore_comments(file, deleted_rows, deleted_fragments)
        if len(properties) == 0:
            print('There is no text to replace')
            return
        # Create resources
        for proj in output_projects:
            proj_directory = os.path.dirname(proj)
            target_folder = os.path.join(proj_directory, 'Resources', additional_path, entity_name)
            XMLEditor.create_resource_file(properties, target_folder)
            XMLEditor.generate_strong_type_resource_classes(target_folder, resource_namespace)
            # Connect resources to project
            XMLEditor.add_resources_to_project(proj, additional_path, resource_namespace, entity_name)
        # TODO: handle cases (like in Sample/Test.cshtml):
        # 1) string.Format("Текст {0} другой текст", arg0);
        # 2) ViewContext.Writer.Write(@"<div class=""alert"">Текст {0} продолжение текста</div>", arg0);

    @staticmethod
    def _remove_comments(file):
        f = open(file, 'r+', encoding='utf-8-sig')
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

    # TODO: take in account that after resource insertion indexes are differ and restoring can be applied to wrong position
    @staticmethod
    def _restore_comments(file, deleted_rows, deleted_fragments):
        f = open(file, 'r+', encoding='utf-8-sig')
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

    @staticmethod
    def _replace_literal_constants_by_resources(file, namespace):
        f = open(file, 'r+', encoding='utf-8-sig')
        text = f.readlines()
        searcher = LanguageWordsSearcher()
        text_fragments = searcher.find_all_text_fragments(text)
        properties = []
        counter = 0
        for row_index in text_fragments:
            fragments_in_reverse_order = sorted(text_fragments[row_index], key=lambda tup: tup[0], reverse=True)
            for fragment in fragments_in_reverse_order:
                property_name = 'Property{0}'.format(counter)
                resource_insertion = '{0}.{1}.{2}'.format(namespace, 'Resource', property_name)
                if not Localizator._is_text_among_razor(text[row_index], fragment):
                    resource_insertion = '@' + resource_insertion
                if Localizator._is_text_as_string_constant(text[row_index], fragment):
                    offset = 1
                else:
                    offset = 0
                text[row_index] = text[row_index][:fragment[0]-offset] +\
                                  resource_insertion +\
                                  text[row_index][fragment[1]+offset:]
                properties.append((property_name, fragment[2]))
                counter += 1
        f.seek(0)
        f.truncate()
        for line in text:
            f.write(line)
        return properties

    '''
    There is a chance of wrong result
    '''
    @staticmethod
    def _is_text_among_razor(line, fragment):
        if '>' in line[fragment[0]-2:fragment[0]] or '<' in line[fragment[1]:fragment[1]+2]\
                or Localizator._check_if_row_is_empty_without_fragment(line, fragment[0], fragment[1]):
            return False
        return True

    '''
    There is a chance of wrong result
    '''
    @staticmethod
    def _is_text_as_string_constant(line, fragment):
        if '"' in line[fragment[0]-1:fragment[0]] and '"' in line[fragment[1]:fragment[1]+1]:
            return True
        return False

    @staticmethod
    def _check_if_row_is_empty_without_fragment(line, start_fragment_index, last_fragment_index):
        if start_fragment_index >= last_fragment_index:
            # something goes wrong
            return False
        line_for_check = line[:start_fragment_index] + line[last_fragment_index:]
        line_length = len(line_for_check)
        if line_for_check.count(' ') + line_for_check.count('\t') + line_for_check.count('\n') == line_length:
            return True
        return False
