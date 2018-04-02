import os

from src.comment_remover.comment_remover import CommentRemover

from src.localizator.code_editor import CodeEditor
from src.localizator.resource_file_manager import XMLEditor
from src.localizator.entity_type import EntityType


def localize_datamodel(project_file, project_folder, init_dir, entity_type, black_list):
    if not os.path.exists(init_dir):
        return

    if os.path.isfile(init_dir) and init_dir.endswith('.cs'):
        localize_datamodel_file(project_file, project_folder, init_dir, entity_type)

    folders = os.listdir(init_dir)
    for item in folders:
        if item in black_list:
            continue

        item = os.path.join(init_dir, item)
        if os.path.isdir(item):
            localize_datamodel(project_file, project_folder, item, entity_type, black_list)
        elif os.path.isfile(item) and item.endswith('.cs'):
            file = os.path.join(project_folder, item)
            localize_datamodel_file(project_file, project_folder, file, entity_type)


def localize_datamodel_file(project_file, project_folder, target_file, entity_type):
    file_path_relate_to_proj = os.path.relpath(target_file, project_folder)
    related_path = os.path.dirname(file_path_relate_to_proj)

    code_editor = CodeEditor(related_path)
    entity_name = code_editor.add_resources_to_entity(target_file, entity_type)
    if entity_name is None:
        return
    # TODO: check if resources already created
    properties = code_editor.properties
    XMLEditor.create_resources(project_folder, project_file, related_path, entity_name, properties)
    print('-' * 20)


def localize_view_file():
    pass


def remove_comments():
    f = open('C:\\Projects\\Scripts\\Localizator\\samples\\file_with_comments.cshtml', 'r')
    # f = open('C:\\Projects\\Scripts\\Localizator\\samples\\test.txt', 'r+')
    text = f.readlines()
    comment_remover = CommentRemover(single_row_sign='//',
                                     multi_row_sign_left='/*',
                                     multi_row_sign_right='*/')
    comment_remover.remove_all_comments(text)

    f = open('C:\\Projects\\Scripts\\Localizator\\samples\\edited_file.cshtml', 'w')
    for line in text:
        f.write(line)


if __name__ == "__main__":
    init_class_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Classes"
    init_enum_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Enums"

    project_file = "DataModel.csproj"
    project_folder = "C:\\Projects\\EAE.LIMS\\DataModel"

    entity_type = EntityType.Class
    # entity_type = EntityType.Enum
    # entity_file = "Enums\\WorkflowDocumentTypes.cs"

    black_list = [
        'References',
        'Reference',
        'Sample',
        'Orders',
        'Equipment.cs',
        'ReportHeader.cs',
        'SpecificationTestComponent.cs',
        'DynamicTableRecord.cs',
        '_Customized\AdmRole.cs'
    ]

    localize_datamodel(project_file, project_folder, init_class_dir, entity_type, black_list)

    print('Done')
    pass
