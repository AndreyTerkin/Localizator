from src.localizator.entity_type import EntityType
from src.localizator.localizator import Localizator


if __name__ == "__main__":
    init_class_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Classes"
    init_enum_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Enums"

    project_file = "DataModel.csproj"
    project_folder = "C:\\Projects\\EAE.LIMS\\DataModel"

    entity_type = EntityType.Class
    # entity_type = EntityType.Enum

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

    localizator = Localizator(project_folder, project_file)
    # localizator.localize_datamodel(init_class_dir, entity_type, black_list)

    file = "C:\\Projects\\EAE.LIMS\\EAE.LIMS\\Views\\Reports\\Reports.cshtml"
    # file = "C:\\Projects\\Scripts\\Localizator\\src\\comment_remover\\file_with_comments.txt"
    localizator.localize_view_file(file)

    print('Done')
    pass
