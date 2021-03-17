import os
import pathlib
import json
import shutil

def get_data_path():
    return os.path.join(os.getcwd(), "tests", "data")

def get_work_path():
    # Ref: https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
    ret = os.path.join(os.getcwd(), "tests", "tmp")
    pathlib.Path(ret).mkdir(parents=True, exist_ok=True)
    return ret

def clean_work_dir():
    # Ref: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    work_path = get_work_path()
    for file_name in os.listdir(work_path):
        file_path = os.path.join(work_path, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            raise Exception(f'Failed to delete "{file_path}"') from e

# This function compare two json files.
# Note, this is not comparison of any json files, but output of the program only.
def json_files_equal(file_name_1, file_name_2, sort_data = True, ignore_comments = True):
    # Ref: https://stackoverflow.com/questions/7214293/is-the-order-of-elements-in-a-json-list-preserved
    # Ref: https://stackoverflow.com/questions/25851183/how-to-compare-two-json-objects-with-the-same-elements-in-a-different-order-equa

    with open(file_name_1, "r") as f1:
        json_data_1 = json.load(f1)
    with open(file_name_2, "r") as f2:
        json_data_2 = json.load(f2)

    assert isinstance(json_data_1, dict)
    assert isinstance(json_data_2, dict)

    if ignore_comments:
        # Ref: https://stackoverflow.com/questions/5844672/delete-an-element-from-a-dictionary
        del json_data_1["_comment"]
        del json_data_2["_comment"]

    if sort_data:
        json_data_1 = sorted((k, v) for k, v in json_data_1.items())
        json_data_2 = sorted((k, v) for k, v in json_data_2.items())

    ret = json_data_1 == json_data_2
    return ret
    
