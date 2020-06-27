import grpc

import game_pb2
import game_pb2_grpc


def get_map(game_id):
    channel = grpc.insecure_channel('localhost:50051')
    service = game_pb2_grpc.GameStub(channel)

    if game_id is None:
        world_size = game_pb2.Size(width=30, height=30)
        request = game_pb2.StartGameRequest(world_size=world_size)
        response = service.StartGame(request)
        game_id = response.game_id
        world_map = response.world_map
    else:
        request = game_pb2.PlayGameRequest(game_id=game_id)
        response = service.PlayGame(request)
        world_map = response.game_state.world_map

    world_size = world_map.map_size

    cells = world_map.cells
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
    return output.splitlines(), game_id
