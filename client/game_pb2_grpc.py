# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import game_pb2 as game__pb2


class GameStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StartGame = channel.unary_unary(
                '/game.Game/StartGame',
                request_serializer=game__pb2.StartGameRequest.SerializeToString,
                response_deserializer=game__pb2.StartGameResponse.FromString,
                )
        self.PlayGame = channel.unary_unary(
                '/game.Game/PlayGame',
                request_serializer=game__pb2.PlayGameRequest.SerializeToString,
                response_deserializer=game__pb2.PlayGameResponse.FromString,
                )


class GameServicer(object):
    """Missing associated documentation comment in .proto file."""

    def StartGame(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PlayGame(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GameServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StartGame': grpc.unary_unary_rpc_method_handler(
                    servicer.StartGame,
                    request_deserializer=game__pb2.StartGameRequest.FromString,
                    response_serializer=game__pb2.StartGameResponse.SerializeToString,
            ),
            'PlayGame': grpc.unary_unary_rpc_method_handler(
                    servicer.PlayGame,
                    request_deserializer=game__pb2.PlayGameRequest.FromString,
                    response_serializer=game__pb2.PlayGameResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'game.Game', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Game(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def StartGame(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/game.Game/StartGame',
            game__pb2.StartGameRequest.SerializeToString,
            game__pb2.StartGameResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PlayGame(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/game.Game/PlayGame',
            game__pb2.PlayGameRequest.SerializeToString,
            game__pb2.PlayGameResponse.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
