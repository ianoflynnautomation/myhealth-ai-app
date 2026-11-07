# HTTP contract

This is the only API definition (Constitution III). `002-chat-ui` and `003-local-runtime` consume it unchanged. A change here starts as a spec change in `001-app-shell`.

JSON on the wire is camelCase. Page numbers are 1-based.

## `GET /health`

`200`

```json
{ "status": "ok" }
```

## `POST /documents`

`multipart/form-data` with one file field named `file`. The file must be a PDF.

`201` the first time those bytes are stored. `200` when the same bytes were already stored.

```json
{
  "id": "sha256-hex",
  "sourceFile": "example.pdf",
  "pageCount": 1,
  "chunkCount": 1
}
```

Safe to retry. The same bytes return the existing document.

## `GET /documents`

`200`

```json
{ "documents": [ { "id": "sha256-hex", "sourceFile": "example.pdf", "pageCount": 1, "chunkCount": 1 } ] }
```

No chunk text.

## `POST /chat`

JSON body:

```json
{
  "messages": [
    { "role": "user", "content": "What is the DemoMarker value?" }
  ]
}
```

`messages` must be non-empty. Each item has a `role` of `user` or `assistant` and a non-empty `content`. The last message is from `user`. Unknown fields are rejected.

`200` when a stored chunk matches:

```json
{
  "outputText": "DemoMarker value is 10 units.",
  "citations": [
    {
      "id": "sha256-hex:1",
      "sourceFile": "example.pdf",
      "sourcePage": 1,
      "content": "DemoMarker value is 10 units."
    }
  ]
}
```

`200` when the store is empty or nothing matches:

```json
{ "outputText": "No stored document answers that.", "citations": [] }
```

Writes nothing.

## Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Last message must be from the user.",
    "details": {}
  }
}
```

| Status | Code | When | Message the page shows |
| --- | --- | --- | --- |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | Chat body is not JSON, or the upload is not a PDF | `Upload must be a PDF.` for an upload |
| 422 | `VALIDATION_ERROR` | JSON fails the schema, the PDF is empty, or the stub parser finds no text layer | `PDF has no text layer.` for a scan in the stub profile |
| 500 | `INTERNAL_ERROR` | Anything else. Fixed message. No stack trace in the body. | `Internal server error.` |

## Route flags

`GET /health` is always registered. `POST /documents` and `GET /documents` are registered when `documents_enabled` is true. `POST /chat` is registered when `chat_enabled` is true. The module-level app reads `DOCUMENTS_ENABLED` and `CHAT_ENABLED`. `1`, `true` or `yes` turns a route on, and any other set value turns it off. Unset means on.
