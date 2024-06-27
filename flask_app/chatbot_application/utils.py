import csv
from collections import Counter

class UncasedDict(dict):
    # Case-insensitive dictionary
    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.lower()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.lower()
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        if isinstance(key, str):
            key = key.lower()
        return super().get(key, default)

    def __contains__(self, key):
        if isinstance(key, str):
            key = key.lower()
        return super().__contains__(key)

def get_first_source_doc_title(result):
    """
    The 'result' variable is the object returned from the Langchain call.
    """
    #print(result['source_documents'])
    source_path = result['source_documents'][0].metadata["source"][15:-4] # Doc Path of the file
    pascal_case_source_title = ''.join(x for x in source_path.title() if not x.isspace())
    formatted_source_title = ''.join(e for e in pascal_case_source_title if e.isalnum())
    return formatted_source_title

def get_first_source_webpage_title(result):
    """
    The 'result' variable is the object returned from the Langchain call.
    """
    return result['source_documents'][0].metadata["source"][15:-4]


def generate_mapping(mapping_file):
    mapping = UncasedDict()
    with open(mapping_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["Child Class"]] = row["URL"]
    return mapping


def generate_screening_tool_mapping(mapping_file):
    mapping_screening_tool = UncasedDict()
    with open(mapping_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            screening_tools = row["Screening Tool Name"]
            screening_tools_urls = row["ST URLS"]
            if screening_tools.strip() != "":
                screening_tools_list = [toolname.strip() for toolname in screening_tools.split("|")]
                screening_tools_urls_list = [url.strip() for url in screening_tools_urls.split("|")]
                mapping_screening_tool[row["Child Class"]] = (screening_tools_list, screening_tools_urls_list)

    return mapping_screening_tool


def has_confident_source(result):
    """
       The 'result' variable is the object returned from the Langchain call.
    """
    source_counter = Counter([result['source_documents'][i].metadata["source"][15:-4] for i in range(30)])

    return source_counter.most_common(1)[0][1] >= 5 # True if at least 7 chunks are from the same first source