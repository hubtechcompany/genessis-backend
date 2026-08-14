# from pathlib import Path

# from load import load_book
# from splitter import split_documents
# from embedding import create_embedding

# from database import supabase


# BOOKS_DIR = Path("books")


# def ingest_book(file_path):

#     print(f"\nLoading: {file_path.name}")

#     # 1. Load
#     documents = load_book(file_path)

#     print(f"Pages/documents loaded: {len(documents)}")

#     # 2. Split
#     chunks = split_documents(documents)

#     print(f"Chunks created: {len(chunks)}")

#     # Book ID
#     book_id = file_path.stem

#     # 3. Process chunks
#     rows = []

#     for index, chunk in enumerate(chunks):

#         content = chunk.page_content.strip()

#         if not content:
#             continue

#         embedding = create_embedding(content)

#         page = chunk.metadata.get("page")

#         chapter = None

#         if page is not None:
#             chapter = f"Page {page + 1}"

#         rows.append({
#             "book_id": book_id,
#             "filename": file_path.name,
#             "title": file_path.stem,
#             "chapter": chapter,
#             "chunk_number": index,
#             "content": content,
#             "embedding": embedding
#         })

#     # 4. Insert
#     if rows:

#         response = (
#             supabase
#             .table("documents")
#             .insert(rows)
#             .execute()
#         )

#         print(
#             f"Inserted {len(response.data)} chunks"
#         )


# def ingest_all_books():

#     files = list(BOOKS_DIR.glob("*.pdf"))

#     files += list(BOOKS_DIR.glob("*.docx"))

#     print(f"Found {len(files)} books")

#     for file_path in files:

#         try:

#             ingest_book(file_path)

#         except Exception as e:

#             print(
#                 f"ERROR processing "
#                 f"{file_path.name}: {e}"
#             )


# if __name__ == "__main__":

#     ingest_all_books()