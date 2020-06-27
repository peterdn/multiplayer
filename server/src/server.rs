use tonic::{transport::Server, Request, Response, Status};

use game::game_server::{Game, GameServer};
use game::{PlayGameRequest, PlayGameResponse};

pub mod game {
    tonic::include_proto!("game");
}

#[derive(Debug, Default)]
struct TestGame {}

#[tonic::async_trait]
impl Game for TestGame {
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
