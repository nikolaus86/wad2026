import asyncio
import time

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    
    try:
        request_data = await reader.read(1024)
        request = request_data.decode()
        
        task_name = asyncio.current_task().get_name()
        print(f"Request by {task_name} from {client_address}: {request}")
        
        await asyncio.sleep(3)

        # time.sleep(3)

        response = f"HTTP/1.0 200 OK\n\nHello from async task {task_name}!\n"
        writer.write(response.encode())
        await writer.drain()
        
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(
        handle_client, 
        SERVER_HOST, 
        SERVER_PORT
    )
    
    addr = server.sockets[0].getsockname()
    print(f"Async server listening on {addr[0]}:{addr[1]} ...")
    
    async with server:
        await server.serve_forever()


asyncio.run(main())

