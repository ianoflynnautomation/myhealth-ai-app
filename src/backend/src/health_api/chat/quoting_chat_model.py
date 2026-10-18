from health_api.documents.memory_corpus import StoredChunk

NO_STORED_ANSWER = "No stored document answers that."


def quote(citations: list[StoredChunk]) -> str:
    if not citations:
        return NO_STORED_ANSWER
    return citations[0].text
