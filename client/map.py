import grpc

import game_pb2
import game_pb2_grpc


def get_map():
    channel = grpc.insecure_channel('localhost:50051')
    stub = game_pb2_grpc.GameStub(channel)

    world_size = game_pb2.Size(width=30, height=30)
    request = game_pb2.StartGameRequest(world_size=world_size)

    response = stub.StartGame(request)
    response_world_size = response.world_map.map_size

    assert(world_size == response_world_size)

    cells = response.world_map.cells
    assert(len(cells) == world_size.width * world_size.height)
    idx = 0
    output = ''
    for y in range(world_size.height):
        for x in range(world_size.width):
            if cells[idx] == 0:
                output += '.'
            else:
                output += '#'
            idx += 1
        output += '\n'
    return output.splitlines()
