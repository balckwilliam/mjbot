# Neural Network Integration into ot_server.py

## Summary

This document describes the integration of the neural network model into `ot_server.py` to replace random action selection with AI-driven decisions.

## Changes Made

### 1. ot_server.py
- **Modified `react_batch` endpoint** to use the AI agent's discard model instead of random selection
- **Added observation format handling**: Expects observations in shape `[291, 34]` or flattened `[9894]`
- **Implemented intelligent action selection**: Uses neural network Q-values to select the best valid action
- **Added graceful fallback**: Falls back to random selection if observation format is invalid or model fails
- **Updated documentation**: Clarified expected input format in docstring

### 2. mahjong/agent.py
- **Fixed PyTorch 2.9+ compatibility**: Added `weights_only=False` parameter to all `torch.load()` calls
- This allows loading models saved with older PyTorch versions

### 3. online_game/server.py  
- **Fixed PyTorch 2.9+ compatibility**: Added `weights_only=False` to reward model loading

### 4. test_ot_server.py
- **Added comprehensive test**: Created `test_react_batch_with_real_features()` demonstrating neural network integration
- Test generates actual game features and validates model decisions

## How It Works

### Input Format
The server expects observations in the following format:
- **Shape**: Either `[291, 34]` (channels × tiles) or flattened `[9894]`
- **Content**: Game state features extracted using `game.get_feature()`
- **Masks**: Boolean array indicating which actions are valid

### Processing Flow
1. Server receives observation and mask
2. Observation is validated and reshaped if needed
3. Features are converted to PyTorch tensor
4. Discard model processes features and outputs Q-values (probabilities after softmax)
5. Invalid actions are masked out
6. Action with highest Q-value among valid actions is selected
7. Results are returned with Q-values and selected action

### Fallback Behavior
If any error occurs (invalid observation format, model failure, etc.):
- Server logs a warning
- Falls back to random selection from valid actions
- Request still succeeds (graceful degradation)

## Testing

### Verification Steps
1. ✅ Models load successfully with PyTorch 2.9
2. ✅ Neural network makes decisions based on Q-values
3. ✅ Fallback works when invalid observations are provided
4. ✅ Server health endpoint reports AI as loaded
5. ✅ No security vulnerabilities (CodeQL scan passed)

### Example Usage

```python
import numpy as np
import requests
from mahjong.game import MahjongGame

# Generate game features
game = MahjongGame(has_aka=True)
game.new_game(0, 0, 0)
feature = game.get_feature(0)

# Flatten for transmission
obs_flat = feature.flatten().tolist()

# Create mask for all 34 tiles
mask = [True] * 34

# Make request
response = requests.post(
    'http://localhost:5000/react_batch',
    json={'obs': [obs_flat], 'masks': [mask]}
)

result = response.json()
print(f"Selected action: {result['actions'][0]}")
print(f"Q-values: {result['q_out'][0]}")
```

## Model Architecture

The discard model is a ResNet-based 1D convolutional neural network:
- **Input**: `[batch_size, 291, 34]` where 291 is feature channels and 34 is tiles
- **Architecture**: 50 ResNet blocks with 256 channels
- **Output**: `[batch_size, 34]` Q-values for each tile
- **Post-processing**: Softmax to convert to action probabilities

## Performance

The neural network provides intelligent decision-making based on:
- Hand tiles and their composition
- Visible tiles (discards, dora indicators)
- Game state (round, honba, scores)
- Player positions and riichi status
- Other contextual game information

## Future Improvements

Potential enhancements:
- Support for other action types (riichi, chi, pon, kan) beyond discard
- Batch processing optimization
- Model versioning support
- Performance metrics and logging
