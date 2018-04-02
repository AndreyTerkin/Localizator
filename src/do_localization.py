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

    localizator = Localizator()
    localizator.localize_datamodel(project_file, project_folder, init_class_dir, entity_type, black_list)

    print('Done')
    pass
