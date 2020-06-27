use tonic::{transport::Server, Code, Request, Response, Status};

use game::game_server::{Game, GameServer};
use game::{Map, PlayGameRequest, PlayGameResponse, Size, StartGameRequest, StartGameResponse};

pub mod map;

pub mod game {
    tonic::include_proto!("game");
}

#[derive(Debug, Default)]
struct TestGame {}

#[tonic::async_trait]
impl Game for TestGame {
    async fn start_game(
        &self,
        request: Request<StartGameRequest>,
    ) -> Result<Response<StartGameResponse>, Status> {
        let request = request.into_inner();

        if request.world_size.is_none() {
            return Err(Status::new(
                Code::InvalidArgument,
                "No world size specified",
            ));
        }

        let world_size = request.world_size.unwrap();

        if world_size.width < map::MAP_WIDTH_MIN
            || world_size.width > map::MAP_WIDTH_MAX
            || world_size.height > map::MAP_HEIGHT_MAX
            || world_size.height < map::MAP_HEIGHT_MIN
        {
            return Err(Status::new(Code::InvalidArgument, "Bad world size"));
        }

        let ncells = (world_size.width * world_size.height) as usize;
        let cells = vec![0; ncells];

        let map = game::Map {
            map_size: Some(world_size),
            cells,
        };

        let reply = game::StartGameResponse {
            game_id: 100,
            world_map: Some(map),
        };

        Ok(Response::new(reply))
    }

    async fn play_game(
        &self,
        request: Request<PlayGameRequest>,
    ) -> Result<Response<PlayGameResponse>, Status> {
        println!("Got a request: {:?}", request);

        let reply = game::PlayGameResponse {
            message: "this is a test response".into(),
        };

        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::]:50051".parse()?;
    let game = TestGame::default();

    Server::builder()
        .add_service(GameServer::new(game))
        .serve(addr)
        .await?;

    Ok(())
}
