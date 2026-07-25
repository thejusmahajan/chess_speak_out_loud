import { parsePgn } from 'chessops/pgn';

const pgn = `[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]

1. e4 e5 2. Nf3 *`;

const games = parsePgn(pgn);
console.log(JSON.stringify(games, null, 2));
