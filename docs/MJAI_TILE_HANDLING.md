# MJAI Tile Handling Documentation

## Overview

This document explains how MJAI tile notation is handled in the mjapi_server, including validation, conversion, and display functions.

## MJAI Tile Notation

### Standard Format

MJAI uses a string-based tile notation:

#### Number Tiles
- **Manzu (萬子/characters)**: `1m` through `9m`
- **Pinzu (饼子/dots)**: `1p` through `9p`
- **Souzu (索子/bamboo)**: `1s` through `9s`

#### Honor Tiles
- `1z`: East wind (東)
- `2z`: South wind (南)
- `3z`: West wind (西)
- `4z`: North wind (北)
- `5z`: White dragon (白) **← Important: This is valid!**
- `6z`: Green dragon (發)
- `7z`: Red dragon (中)

#### Red Tiles (Aka Dora)
- `5mr`: Red 5 manzu
- `5pr`: Red 5 pinzu
- `5sr`: Red 5 souzu

### Alternate Format

Some MJAI clients use single-character notation for honor tiles:
- `E` → `1z` (East)
- `S` → `2z` (South)
- `W` → `3z` (West)
- `N` → `4z` (North)
- `P` → `5z` (White dragon)
- `F` → `6z` (Green dragon)
- `C` → `7z` (Red dragon)

The server automatically normalizes these to standard MJAI format.

## Common Misconception: "MJAI doesn't have z"

**This is incorrect!** MJAI absolutely supports 'z' tiles (honor tiles). The notation `1z` through `7z` is the standard MJAI way to represent the 7 honor tiles (4 winds + 3 dragons).

If you encounter a KeyError with '5z' or any other 'z' tile, it's likely because:
1. MJAI tiles (strings like '5z') are being used where Tenhou tile IDs (integers 0-135) are expected
2. The tile is being used as a dictionary key in code that expects integer indices

## Utility Functions

### `validate_mjai_tile(mjai_tile: str) -> bool`

Validates if a string is a valid MJAI tile notation.

```python
validate_mjai_tile('5z')   # True - White dragon
validate_mjai_tile('P')    # True - Alternate format for White dragon
validate_mjai_tile('1m')   # True - 1 manzu
validate_mjai_tile('10m')  # False - Invalid number
validate_mjai_tile('invalid')  # False - Not a tile
```

### `mjai_tile_to_tenhou_id(mjai_tile: str) -> int`

Converts MJAI tile notation to internal Tenhou tile ID (0-135).

```python
mjai_tile_to_tenhou_id('5z')   # 124 - White dragon
mjai_tile_to_tenhou_id('P')    # 124 - Same (normalized first)
mjai_tile_to_tenhou_id('1m')   # 0 - 1 manzu
mjai_tile_to_tenhou_id('5pr')  # 52 - Red 5 pinzu
```

Tenhou ID ranges:
- 0-35: Manzu (characters)
- 36-71: Pinzu (dots)
- 72-107: Souzu (bamboo)
- 108-135: Honor tiles
- Special: 16 (5mr), 52 (5pr), 88 (5sr) for red tiles

### `tenhou_id_to_mjai_tile(tenhou_id: int) -> str`

Converts Tenhou tile ID back to MJAI tile notation.

```python
tenhou_id_to_mjai_tile(124)  # '5z' - White dragon
tenhou_id_to_mjai_tile(0)    # '1m' - 1 manzu
tenhou_id_to_mjai_tile(52)   # '5pr' - Red 5 pinzu
```

### `normalize_tile_format(tile: str) -> str`

Normalizes alternate single-character honor tiles to standard MJAI format.

```python
normalize_tile_format('P')   # '5z'
normalize_tile_format('E')   # '1z'
normalize_tile_format('5z')  # '5z' (already normalized)
normalize_tile_format('1m')  # '1m' (non-honor tiles pass through)
```

### `mjai_tile_to_display_string(mjai_tile: str) -> str`

Converts MJAI tile notation to Chinese display string.

```python
mjai_tile_to_display_string('5z')   # '白' - White dragon
mjai_tile_to_display_string('P')    # '白' - Same (normalized first)
mjai_tile_to_display_string('1m')   # '一萬' - 1 manzu
mjai_tile_to_display_string('5pr')  # '赤五饼' - Red 5 pinzu
mjai_tile_to_display_string('1z')   # '東' - East wind
```

## Debugging

When debug mode is enabled (`-d` flag), the server logs tile operations:

```
DEBUG:__main__:Dora marker: 5z (白)
DEBUG:__main__:Initial hand for seat 0: ['1m', '2m', '3m', ...]
DEBUG:__main__:Drew tile: 5p (五饼)
DEBUG:__main__:Converted 5z -> 124 (白)
```

This helps identify any tile handling issues.

## Error Handling

### Invalid Tiles

Invalid tiles are logged but don't crash the server:

```python
# In start_kyoku handler
if validate_mjai_tile(dora_marker):
    game_state['dora_marker'] = dora_marker
    logger.debug(f"Dora marker: {dora_marker} ({mjai_tile_to_display_string(dora_marker)})")
else:
    logger.warning(f"Invalid dora_marker: {dora_marker}")
    game_state['dora_marker'] = dora_marker  # Store anyway but log warning
```

### Conversion Failures

When converting hand tiles fails, the server continues with other tiles:

```python
for mjai_tile in hand:
    try:
        tenhou_id = mjai_tile_to_tenhou_id(mjai_tile)
        tenhou_hand.append(tenhou_id)
    except ValueError as e:
        logger.warning(f"Failed to convert tile {mjai_tile}: {e}")
        # Continue with other tiles
```

## Testing

Run the comprehensive tile handling test:

```bash
python3 test_5z_handling.py
```

This tests:
- ✓ '5z' validation
- ✓ '5z' to Tenhou ID conversion (124)
- ✓ '5z' display as '白'
- ✓ 'P' normalization to '5z'
- ✓ Round-trip conversion
- ✓ All 7 honor tiles (1z-7z)
- ✓ '5z' in hand processing
- ✓ '5z' as dora marker

## Best Practices

1. **Always validate** tiles from external sources before using them
2. **Use conversion functions** when interfacing between MJAI and Tenhou formats
3. **Don't mix formats**: Use MJAI notation in the API layer, Tenhou IDs internally
4. **Log conversions** in debug mode to help diagnose issues
5. **Handle both formats**: Support standard (`5z`) and alternate (`P`) notation

## Common Pitfalls

### ❌ Wrong: Using MJAI notation as dictionary key

```python
# This will fail because TILE_STRING_DICT expects integer keys
display = TILE_STRING_DICT['5z']  # KeyError: '5z'
```

### ✓ Correct: Convert first

```python
# Convert MJAI to Tenhou ID first
tenhou_id = mjai_tile_to_tenhou_id('5z')  # 124
tile_index = tenhou_id // 4  # 31
display = TILE_STRING_DICT[tile_index]  # '白'

# Or use the utility function
display = mjai_tile_to_display_string('5z')  # '白'
```

## Summary

- **'5z' is valid MJAI notation** for the White dragon (白)
- All 7 honor tiles (1z-7z) are supported
- Alternate format (P, F, C, etc.) is automatically normalized
- Use validation and conversion functions when working with tiles
- The server provides comprehensive logging for debugging
- All tile handling is tested and working correctly

## See Also

- [MJAI Protocol Reference](mjai_protocol.md)
- [MJAPI Server Documentation](MJAPI_SERVER.md)
- [Quick Start Guide](QUICKSTART_MJAPI.md)
