from health_api.documents.memory_corpus import StoredChunk


def quote(citations: list[StoredChunk]) -> str:
    return citations[0].text
