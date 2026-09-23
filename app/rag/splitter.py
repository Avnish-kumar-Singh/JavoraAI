# """
# Document Splitter

# Splits documents into smaller chunks for embeddings.
# """

# # from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain_text_splitters import RecursiveCharacterTextSplitter

# from app.config.logging_config import logger


# class DocumentSplitter:

#     def __init__(
#         self,
#         chunk_size: int = 500,
#         chunk_overlap: int = 100,
#     ):

#         self.splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             separators=[
#                 "\n\n",
#                 "\n",
#                 ". ",
#                 " ",
#                 ""
#             ],
#         )

#     def split(self, documents):

#         logger.info("Splitting documents...")

#         chunks = self.splitter.split_documents(documents)

#         logger.info(f"Created {len(chunks)} chunks.")

#         return chunks




"""
Document Splitter

Splits documents into meaningful chunks for embeddings.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.logging_config import logger


class DocumentSplitter:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n# ",
                "\n## ",
                "\n### ",
                "\n\n",
                "\n",
                ". ",
                "? ",
                "! ",
                ";",
                " ",
                ""
            ],
            keep_separator=True,
        )

    def split(self, documents):

        logger.info("Splitting documents...")

        chunks = self.splitter.split_documents(documents)

        logger.info(f"Created {len(chunks)} chunks.")

        return chunks