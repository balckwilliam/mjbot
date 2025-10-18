# Neural Network Integration Guide

## Overview

The MJAPI server now includes infrastructure for integrating the neural network model (AiAgent) for decision-making in mahjong games. This document explains the current implementation and what's needed for full integration.

## Current Implementation

### Added Components

1. **Tile Conversion Functions**
   - `mjai_tile_to_tenhou_id(mjai_tile)`: Converts MJAI tile notation (e.g., "1m", "5pr") to Tenhou tile IDs (0-135)
   - `tenhou_id_to_mjai_tile(tenhou_id)`: Converts Tenhou tile IDs back to MJAI notation

2. **tsumogiri Field**
   - The `dahai` response now includes the `tsumogiri` field (required by MJAI protocol)
   - This field is `True` when the discarded tile is the same as the just-drawn tile
   - Properly tracked in the game state

3. **Neural Network Preparation**
   - The `make_dahai_decision` function now converts tiles to Tenhou format
   - Infrastructure is in place to call `bot.discard(state, tiles)` method
   - Currently uses random selection as full state building is not yet implemented

## Tile Format Conversion

### MJAI Format
- Number tiles: `1m` to `9m` (manzu), `1p` to `9p` (pinzu), `1s` to `9s` (souzu)
- Honor tiles: `1z` to `7z` (winds and dragons)
- Red tiles: `5mr`, `5pr`, `5sr` (red dora)

### Tenhou Format
- Tile IDs: 0-135
  - 0-35: Manzu (0-3 = 1m, 4-7 = 2m, ..., 32-35 = 9m)
  - 36-71: Pinzu (36-39 = 1p, 40-43 = 2p, ..., 68-71 = 9p)
  - 72-107: Souzu (72-75 = 1s, 76-79 = 2s, ..., 104-107 = 9s)
  - 108-135: Honor tiles (108-111 = 1z/East, ..., 132-135 = 7z/Red dragon)
- Red tiles: 16 (5mr), 52 (5pr), 88 (5sr)

## Neural Network Model Requirements

The AiAgent expects:

1. **State Array**: numpy array of shape `[291, 34]`
   - 291 features tracking various game aspects
   - 34 tile types
   
2. **Tile List**: List of Tenhou tile IDs representing the current hand

### State Features (291 total)

The state encoding requires tracking:

1. **Hand tiles** (34 features): Count of each tile type in hand
2. **Discards** (34 × 4 = 136 features): Each player's discarded tiles
3. **Melds** (varies): Exposed melds (chi, pon, kan)
4. **Dora indicators** (34 features): Current dora
5. **Game context**:
   - Round wind (bakaze)
   - Seat wind
   - Round number (kyoku)
   - Honba count
   - Riichi declarations
   - Current scores

See `dataset/data.py` and `mahjong/game.py` for the complete state encoding implementation.

## Integration Steps (TODO)

To fully integrate the neural network model, the following work is needed:

### 1. State Tracking Enhancement

Extend the `game_state` dictionary in `mjapi_server.py` to track:

```python
game_state = {
    'seat': int,           # Player seat (0-3)
    'hand': list,          # Current hand (MJAI format)
    'tsumo_pai': str,      # Just-drawn tile
    'all_discards': [[], [], [], []],  # All players' discards
    'all_melds': [[], [], [], []],     # All players' melds
    'dora_markers': [],    # List of dora indicators
    'riichi_declarations': [False, False, False, False],
    'scores': [int, int, int, int],
    'bakaze': str,         # Round wind
    'kyoku': int,          # Round number
    'honba': int,          # Honba count
}
```

### 2. State Encoding Function

Create a function to convert the MJAI game state to the neural network's expected format:

```python
def build_nn_state(game_state: dict, seat: int) -> np.ndarray:
    """
    Build the 291×34 state array from MJAI game state
    
    Args:
        game_state: MJAI game state dictionary
        seat: Current player's seat (0-3)
    
    Returns:
        numpy array of shape [291, 34]
    """
    # TODO: Implement state encoding
    # See dataset/data.py for reference implementation
    pass
```

### 3. Update make_dahai_decision

Replace the random selection with actual neural network call:

```python
# Convert to Tenhou format
tenhou_hand = [mjai_tile_to_tenhou_id(t) for t in hand]

# Build state array
state = build_nn_state(game_state, game_state['seat'])

# Use neural network to select tile
selected_tenhou_id, confidence = bot.discard(state, tenhou_hand)

# Convert back to MJAI format
selected_pai = tenhou_id_to_mjai_tile(selected_tenhou_id)
```

### 4. Message Processing Updates

Update the message processing in `process_mjai_message` to track additional state:

- Track all player discards (not just own)
- Track all melds
- Track riichi declarations
- Update dora markers on `dora` messages

### 5. Other Actions

Extend neural network integration to other decision points:

- **Riichi decision**: Use `bot.riichi_decision(state)`
- **Chi decision**: Use `bot.chi_decision(state)`
- **Pon decision**: Use `bot.pon_decision(state)`
- **Kan decision**: Use `bot.kan_decision(state)`
- **Ron decision**: Use `bot.agari_decision(agents, agari_action)`

## Testing

After full integration, test with:

1. **Unit tests**: Test state encoding with known game states
2. **Integration tests**: Test with real game sequences
3. **Model accuracy**: Compare decisions with training data
4. **Performance**: Ensure response times are acceptable (<1s per decision)

## References

- `dataset/data.py`: State encoding implementation
- `mahjong/game.py`: Full game state management
- `mahjong/agent.py`: AiAgent class and model interfaces
- `online_game/server.py`: Reference server with full integration
- `docs/mjai_protocol.md`: MJAI protocol specification

## Current Limitations

1. **Random selection**: Currently uses random tile selection
2. **No state building**: Game state features are not yet constructed
3. **Single decision type**: Only handles discard decisions
4. **No reactions**: Cannot use neural network for pon/chi/kan/ron decisions

## Performance Considerations

Full neural network integration will require:

- PyTorch installed (`pip install torch`)
- Model files in `model/saved/` directory
- GPU recommended for faster inference (but CPU works too)
- ~10-50ms per decision on modern hardware

## Example Usage

Once fully integrated, the bot will:

1. Receive game state via MJAI protocol
2. Convert to internal representation
3. Call neural network model
4. Return decision with confidence score
5. Continue playing optimally based on trained model

The trained model (if available) can be downloaded and placed in:
- `model/saved/discard-model/best.pt`
- `model/saved/riichi-model/best.pt`
- `model/saved/chi-model/best.pt`
- `model/saved/pon-model/best.pt`
- `model/saved/kan-model/best.pt`
