"""Limite de corpo aplicado antes do parser JSON, inclusive em streaming."""
from starlette.responses import JSONResponse

MAX_BODY_BYTES = 128 * 1024


class BodySizeLimit:
    def __init__(self, app, limit=MAX_BODY_BYTES):
        self.app, self.limit = app, limit

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        length = dict(scope.get('headers', [])).get(b'content-length')
        if length is not None:
            try:
                length = int(length)
                if length < 0: raise ValueError()
            except ValueError:
                return await JSONResponse({'detail':'Content-Length inválido.'},status_code=400)(scope,receive,send)
            if length > self.limit:
                return await JSONResponse({'detail':'A requisição excede o limite de 128 KB.'},status_code=413)(scope,receive,send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect': return
            part = message.get('body', b'')
            size += len(part)
            if size > self.limit:
                return await JSONResponse({'detail':'A requisição excede o limite de 128 KB.'},status_code=413)(scope,receive,send)
            chunks.append(part)
            if not message.get('more_body', False): break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type':'http.request','body':b''.join(chunks),'more_body':False}
            return await receive()

        return await self.app(scope,replay,send)
