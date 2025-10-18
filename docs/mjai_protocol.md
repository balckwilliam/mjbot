# MJAI Protocol Reference

## Overview

MJAI (Mahjong AI) Protocol is a JSON-based protocol for mahjong game communication. This document describes the protocol implementation in mjbot.

## Message Structure

All messages follow this basic structure:
```json
{
    "type": "message_type",
    ...additional fields...
}
```

## Core Message Types

### Game Flow Messages

#### start_game
Indicates the start of a game.

**Required fields:**
- `type`: "start_game"
- `id`: Player seat number (0-3)

**Example:**
```json
{
    "type": "start_game",
    "id": 0
}
```

#### start_kyoku
Indicates the start of a round (kyoku).

**Required fields:**
- `type`: "start_kyoku"
- `bakaze`: Round wind ("E", "S", "W", "N")
- `kyoku`: Round number (1-4)
- `honba`: Honba count (bonus counter)
- `oya`: Dealer seat (0-3)
- `scores`: Array of 4 player scores
- `dora_marker`: Initial dora indicator tile
- `tehais`: Initial hands for all players (array of 4 arrays)

**Example:**
```json
{
    "type": "start_kyoku",
    "bakaze": "E",
    "kyoku": 1,
    "honba": 0,
    "oya": 0,
    "scores": [25000, 25000, 25000, 25000],
    "dora_marker": "5z",
    "tehais": [
        ["1m", "2m", "3m", ...],
        [...],
        [...],
        [...]
    ]
}
```

#### tsumo
Indicates a player draws a tile.

**Required fields:**
- `type`: "tsumo"
- `actor`: Player seat (0-3)
- `pai`: Tile drawn

**Optional fields:**
- `can_act`: Boolean indicating if the player can take action

**Example:**
```json
{
    "type": "tsumo",
    "actor": 0,
    "pai": "5p",
    "can_act": true
}
```

#### dahai
Indicates a player discards a tile.

**Required fields:**
- `type`: "dahai"
- `actor`: Player seat (0-3)
- `pai`: Tile discarded

**Optional fields:**
- `tsumogiri`: Boolean indicating if discarded immediately after draw
- `can_act`: Boolean indicating if other players can react

**Example:**
```json
{
    "type": "dahai",
    "actor": 0,
    "pai": "9m"
}
```

### Action Messages

#### reach / riichi
Declares riichi.

**Required fields:**
- `type`: "reach"
- `actor`: Player seat (0-3)

#### pon
Calls pon (triplet).

**Required fields:**
- `type`: "pon"
- `actor`: Player seat (0-3)
- `target`: Player seat being called from (0-3)
- `pai`: Tile being called
- `consumed`: Array of tiles consumed from hand

#### chi
Calls chi (sequence).

**Required fields:**
- `type`: "chi"
- `actor`: Player seat (0-3)
- `target`: Player seat being called from (0-3)
- `pai`: Tile being called
- `consumed`: Array of tiles consumed from hand

#### daiminkan
Declares open kan.

**Required fields:**
- `type`: "daiminkan"
- `actor`: Player seat (0-3)
- `pai`: Tile being called
- `consumed`: Array of tiles consumed

#### ankan
Declares closed kan.

**Required fields:**
- `type`: "ankan"
- `actor`: Player seat (0-3)
- `consumed`: Array of 4 tiles

#### kakan
Adds to an existing pon to make a kan.

**Required fields:**
- `type`: "kakan"
- `actor`: Player seat (0-3)
- `pai`: Tile being added
- `consumed`: Array of tiles involved

#### hora
Declares win.

**Required fields:**
- `type`: "hora"
- `actor`: Player seat (0-3)

**Optional fields:**
- `target`: Player seat whose discard was used (for ron)
- `deltas`: Score changes
- `ura_markers`: Ura dora indicators (for riichi win)

### End Messages

#### ryukyoku
Indicates a draw.

**Required fields:**
- `type`: "ryukyoku"

**Optional fields:**
- `reason`: Reason for draw
- `tenpais`: Array of players in tenpai
- `deltas`: Score changes

#### end_kyoku
Indicates the end of a round.

**Required fields:**
- `type`: "end_kyoku"

#### end_game
Indicates the end of the game.

**Required fields:**
- `type`: "end_game"

### Special Messages

#### dora
Reveals a new dora indicator.

**Required fields:**
- `type`: "dora"
- `dora_marker`: New dora indicator tile

#### none
Indicates no action taken.

**Required fields:**
- `type`: "none"

## Tile Notation

### Number Tiles
- Manzu (characters): `1m` - `9m`
- Pinzu (dots): `1p` - `9p`
- Souzu (bamboo): `1s` - `9s`

### Honor Tiles
- Winds and dragons: `1z` - `7z`
  - `1z`: East (東)
  - `2z`: South (南)
  - `3z`: West (西)
  - `4z`: North (北)
  - `5z`: White dragon (白)
  - `6z`: Green dragon (發)
  - `7z`: Red dragon (中)

### Red Tiles (Aka Dora)
- `5mr`: Red 5 manzu
- `5pr`: Red 5 pinzu
- `5sr`: Red 5 souzu

## Implementation Notes

### Seat/Player ID
- Player seats are numbered 0-3
- The bot's seat is determined by:
  1. The `id` field in `/mjai/start` request
  2. The `id` field in `start_game` message
  3. Defaults to 0 if not specified

### State Management
- The server maintains game state per session
- State includes:
  - Current hand
  - Player seat
  - Game phase (kyoku started, etc.)
  - Dora markers
  - Scores

### Error Handling
- Missing required fields are logged but don't crash the server
- Invalid message structures are skipped
- Batch processing continues even if individual messages fail

## API Usage

### Single Message
```bash
POST /mjai/act
Authorization: Bearer {token}

{
    "seq": 0,
    "data": {
        "type": "tsumo",
        "actor": 0,
        "pai": "5p",
        "can_act": true
    }
}
```

### Batch Messages
```bash
POST /mjai/batch
Authorization: Bearer {token}

[
    {
        "seq": 0,
        "data": {
            "type": "start_game",
            "id": 0
        }
    },
    {
        "seq": 1,
        "data": {
            "type": "start_kyoku",
            ...
        }
    },
    ...
]
```

## References

- [MJAI Protocol Specification](https://mjai.app/docs/mjai-protocol)
- [MahjongCopilot Integration](MJAPI_SERVER.md)

## Version History

- **2025-10-18**: Initial documentation
  - Added core message types
  - Documented required fields
  - Added tile notation reference
  - Included implementation notes
