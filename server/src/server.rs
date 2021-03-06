use tonic::{transport::Server, Code, Request, Response, Status};

use game::game_server::{Game, GameServer};
use game::{
    GameStateUpdate, Map, PlayGameRequest, PlayGameResponse, PlayerState, Position, Size,
    StartGameRequest, StartGameResponse,
};

use rand::Rng;
use std::sync::Mutex;

pub mod map;

pub mod game {
    tonic::include_proto!("game");
}

#[derive(Debug)]
struct GameState {
    id: i32,
    map: Map,
    players: Vec<PlayerState>,
}

impl GameState {}

#[derive(Debug)]
struct TestGame {
    games: Mutex<Vec<GameState>>,
}

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
        let mut cells = vec![0; ncells];

        // Create some random walls
        let mut rng = rand::thread_rng();
        let nwalls = rng.gen_range(10, 40);
        for _w in 0..nwalls {
            let vertical = rng.gen_range(0, 2) == 0;
            if vertical {
                let len = rng.gen_range(4, world_size.height / 2);
                let x = rng.gen_range(0, world_size.width);
                let y = rng.gen_range(0, world_size.height - len);
                for i in 0..len {
                    let idx = ((y + i) * world_size.width + x) as usize;
                    cells[idx] = 1;
                }
            } else {
                let len = rng.gen_range(4, world_size.width / 2);
                let x = rng.gen_range(0, world_size.width - len);
                let y = rng.gen_range(0, world_size.height);
                for i in 0..len {
                    let idx = (y * world_size.width + x + i) as usize;
                    cells[idx] = 1;
                }
            }
        }

        // Generate player position
        let mut playerx = 0;
        let mut playery = 0;
        loop {
            playerx = rng.gen_range(0, world_size.width);
            playery = rng.gen_range(0, world_size.height);
            let idx = (playery * world_size.width + playerx) as usize;
            if cells[idx] == 0 {
                break;
            }
        }

        let player = PlayerState {
            player_id: 0,
            position: Some(Position {
                x: playerx,
                y: playery,
                facing: 2,
            }),
        };

        let map = game::Map {
            map_size: Some(world_size.clone()),
            cells,
        };

        {
            let mut games = self.games.lock().unwrap();
            let ngames = { (*games).len() };
            (*games).push(GameState {
                id: ngames as i32,
                map: map.clone(),
                players: vec![player],
            });
            println!("Created game id: {}", ngames);
        }

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
        let request = request.into_inner();

        println!("Got a request for game id: {}", request.game_id);

        let world_map = {
            let games = self.games.lock().unwrap();
            (*games)[request.game_id as usize].map.clone()
        };

        let players = {
            let games = self.games.lock().unwrap();
            (*games)[request.game_id as usize].players.clone()
        };

        let reply = game::PlayGameResponse {
            player_id: 0,
            game_state: Some(game::GameStateUpdate {
                world_map: Some(world_map),
                players: players,
            }),
        };

        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::]:50051".parse()?;
    let game = TestGame {
        games: Mutex::new(vec![]),
    };

    Server::builder()
        .add_service(GameServer::new(game))
        .serve(addr)
        .await?;

    Ok(())
}
