import asyncio
from functools import partial

from messages import *
from exceptions import *
from message_protocol import MessageProtocol
from message_handler import MessageHandler


# ------------------------------------------------------------------------------
class ServerProtocol(MessageProtocol):
    messages = commands

    def __init__(self, cmd_queue, sender):
        super().__init__(cmd_queue)
        sender.register_protocol(self)

# ------------------------------------------------------------------------------
class CommandReceiver(MessageHandler):
    def __init__(self, loop, cmd_queue, resp_queue):
        super().__init__(loop, cmd_queue)
        self.resp_queue = resp_queue

    def handle_message(self, command):
        """Overridden method called by message handler task
        """
        if command.code == ShutdownCommand.code:
            print('Received shutdown')
            self.stop()
        elif command.code == StepCommand.code:
            print('Step')
        elif command.code == ContinueCommand.code:
            print('Continue')
        elif command.code == SetBreakpointCommand.code:
            print('Breakpoint at {:#0x}'.format(command.address))
        elif command.code == ReadRegisterCommand.code:
            regid = command.register
            print('Read register {}'.format(ReadRegisterCommand.decode_register(regid)))
            resp = ReadRegisterResponse(regid, 42)
            self.resp_queue.put_nowait(resp)
        elif command.code == ReadMemoryCommand.code:
            print('Read memory at {:#0x}'.format(command.address))
            values = bytes([42] * command.length)
            resp = ReadMemoryResponse(command.address, values)
            self.resp_queue.put_nowait(resp)
        else:
            print('Unrecognized command {}'.format(command))

class ResponseSender(MessageHandler):
    def __init__(self, loop, resp_queue, protocols=[]):
        super().__init__(loop, resp_queue)
        self.protocols = protocols

    def register_protocol(self, protocol):
        self.protocols.append(protocol)

    def handle_message(self, response):
        for protocol in self.protocols:
            protocol.send_message(response)


loop = asyncio.get_event_loop()

cmd_queue = asyncio.Queue()
resp_queue = asyncio.Queue()

receiver = CommandReceiver(loop, cmd_queue, resp_queue)
sender = ResponseSender(loop, resp_queue)

# Set up the listening server. This will enqueue commands as they arrive.
coro = loop.create_server(partial(ServerProtocol, cmd_queue, sender),
                          '127.0.0.1', 8888, reuse_address=True)
server = loop.run_until_complete(coro)


receiver_task = receiver.start()
sender_task = sender.start()

receiver.register_shutdown_callback(lambda: server.close())
receiver.register_shutdown_callback(lambda: sender.stop())
sender.register_shutdown_callback(lambda: loop.stop())


print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Shutdown signal received')
    receiver_task.cancel()
    sender_task.cancel()
finally:
    tasks = asyncio.Task.all_tasks(loop=loop)
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.stop()
    loop.close()
