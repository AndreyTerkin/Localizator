import os

from src.comment_remover.comment_remover import CommentRemover

from src.localizator.code_editor import CodeEditor
from src.localizator.resource_file_manager import XMLEditor
from src.localizator.entity_type import EntityType


def localize_datamodel_file(project_file, project_folder, entity_file, entity_type):
    file = os.path.join(project_folder, entity_file)
    file_path_relate_to_proj = os.path.relpath(file, project_folder)
    related_path = os.path.dirname(file_path_relate_to_proj)

    code_editor = CodeEditor(related_path)
    entity_name = code_editor.add_resources_to_entity(file, entity_type)
    if entity_name is None:
        return
    # TODO: check if resources already created
    properties = code_editor.properties
    XMLEditor.create_resources(project_folder, project_file, related_path, entity_name, properties)
    print('-' * 20)


def localize_view_file():
    pass


if __name__ == "__main__":
    project_file = "DataModel.csproj"
    project_folder = "C:\\Projects\\EAE.LIMS\\DataModel"

    entity_type = EntityType.Class
    entity_file = "Classes\\Equipment\\Software.cs"
    # entity_type = EntityType.Enum
    # entity_file = "Enums\\WorkflowDocumentTypes.cs"

    # "\\Classes\\References\\DocumentCategory.cs"
    localize_datamodel_file(project_file, project_folder, entity_file, entity_type)
    print('Done')
    pass
