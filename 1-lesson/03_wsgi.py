def simple_app(environ, start_response): # 1
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers) # 2
    yield b'Hello, World!\n' # 3

