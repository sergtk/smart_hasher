import os

def get_data_path():
    return os.path.join(os.getcwd(), "tests", "data")

def get_work_path():
    return os.path.join(os.getcwd(), "tests", "tmp")

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
            raise Exception(f'Failed to delete "{file_path}"', e)
