
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader
)


def load_book(file_path):

    path = Path(file_path)

    if path.suffix.lower() == ".pdf":

        loader = PyPDFLoader(str(path))

    elif path.suffix.lower() == ".docx":

        loader = Docx2txtLoader(str(path))

    else:

        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )

    return loader.load()


# from pathlib import Path
# from langchain_community.document_loaders import PyPDFLoader

# books = Path("books").glob("*.pdf")

# all_documents = []

# for book in books:

#     print(f"Loading: {book.name}")

#     loader = PyPDFLoader(str(book))

#     documents = loader.load()

#     all_documents.extend(documents)

# print(f"Total pages: {len(all_documents)}")

