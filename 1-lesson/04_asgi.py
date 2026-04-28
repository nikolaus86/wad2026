async def app(scope, receive, send):
    assert scope['type'] == 'http'

    response_body = f'Hello, World!\n'

    if scope['method'] == 'POST':
        recv_data = await receive()
        body = recv_data['body']
        
        while recv_data.get('more_body', False):
            recv_data = await receive()
            body += recv_data['body']

        response_body += body.decode()

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'Content-Type', b'text/plain')
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': response_body.encode(),
        'more_body': False
    })


