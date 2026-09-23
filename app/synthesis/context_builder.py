# """
# Context Builder

# Cleans and merges retrieved chunks before sending them to the LLM.
# """


# class ContextBuilder:

#     def build(self, documents):

#         unique_chunks = []
#         seen = set()

#         for doc in documents:

#             text = doc.page_content.strip()

#             if not text:
#                 continue

#             if text in seen:
#                 continue

#             seen.add(text)
#             unique_chunks.append(text)

#         return "\n\n".join(unique_chunks)



"""
Context Builder

Cleans, removes duplicates, and limits the retrieved
context before sending it to the LLM.
"""


class ContextBuilder:

    # Maximum characters to send to the LLM
    MAX_CONTEXT_LENGTH = 2500

    def build(self, documents):

        unique_chunks = []
        seen = set()
        current_length = 0

        for doc in documents:

            text = doc.page_content.strip()

            # Skip empty chunks
            if not text:
                continue

            # Skip duplicate chunks
            if text in seen:
                continue

            # Stop if adding this chunk exceeds the limit
            if current_length + len(text) > self.MAX_CONTEXT_LENGTH:
                break

            seen.add(text)
            unique_chunks.append(text)
            current_length += len(text)

        return "\n\n".join(unique_chunks)