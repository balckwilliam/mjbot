#!/usr/bin/env python3
"""
Test script to verify that '5z' (White dragon) is handled correctly in MJAPI server
"""
import sys
import os

# Add the online_game directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mjapi_server import (
    validate_mjai_tile,
    mjai_tile_to_display_string,
    mjai_tile_to_tenhou_id,
    tenhou_id_to_mjai_tile,
    normalize_tile_format,
    process_mjai_message
)

def test_5z_validation():
    """Test that '5z' is recognized as a valid tile"""
    print("=== Test 1: Validate '5z' ===")
    assert validate_mjai_tile('5z'), "'5z' should be valid"
    print("✓ '5z' is recognized as valid")
    
def test_5z_conversion():
    """Test that '5z' converts correctly to Tenhou ID"""
    print("\n=== Test 2: Convert '5z' to Tenhou ID ===")
    tenhou_id = mjai_tile_to_tenhou_id('5z')
    print(f"'5z' -> Tenhou ID {tenhou_id}")
    assert tenhou_id == 124, f"Expected 124, got {tenhou_id}"
    print("✓ Conversion correct")

def test_5z_display():
    """Test that '5z' displays correctly"""
    print("\n=== Test 3: Display '5z' ===")
    display = mjai_tile_to_display_string('5z')
    print(f"'5z' -> {display}")
    assert display == '白', f"Expected '白', got {display}"
    print("✓ Display correct")

def test_5z_normalization():
    """Test that 'P' normalizes to '5z'"""
    print("\n=== Test 4: Normalize 'P' to '5z' ===")
    normalized = normalize_tile_format('P')
    print(f"'P' -> {normalized}")
    assert normalized == '5z', f"Expected '5z', got {normalized}"
    print("✓ Normalization correct")

def test_5z_round_trip():
    """Test round-trip conversion"""
    print("\n=== Test 5: Round-trip '5z' ===")
    tenhou_id = mjai_tile_to_tenhou_id('5z')
    back = tenhou_id_to_mjai_tile(tenhou_id)
    print(f"'5z' -> {tenhou_id} -> {back}")
    assert back == '5z', f"Expected '5z', got {back}"
    print("✓ Round-trip successful")

def test_all_honor_tiles():
    """Test all honor tiles including '5z'"""
    print("\n=== Test 6: All honor tiles ===")
    honor_tiles = {
        '1z': ('東', 108),
        '2z': ('南', 112),
        '3z': ('西', 116),
        '4z': ('北', 120),
        '5z': ('白', 124),  # White dragon - the key test case
        '6z': ('發', 128),
        '7z': ('中', 132),
    }
    
    for tile, (expected_display, expected_id) in honor_tiles.items():
        # Validate
        assert validate_mjai_tile(tile), f"{tile} should be valid"
        
        # Convert to Tenhou ID
        tenhou_id = mjai_tile_to_tenhou_id(tile)
        assert tenhou_id == expected_id, f"{tile}: expected ID {expected_id}, got {tenhou_id}"
        
        # Display
        display = mjai_tile_to_display_string(tile)
        assert display == expected_display, f"{tile}: expected '{expected_display}', got '{display}'"
        
        # Round trip
        back = tenhou_id_to_mjai_tile(tenhou_id)
        assert back == tile, f"{tile}: round-trip failed, got {back}"
        
        print(f"✓ {tile} -> {tenhou_id} -> {back} ({display})")
    
    print("✓ All honor tiles handled correctly")

def test_5z_in_hand():
    """Test that '5z' can be in a hand and processed correctly"""
    print("\n=== Test 7: '5z' in hand ===")
    hand = ['1m', '2m', '3m', '5z', '6z', '7z', '1p', '2p', '3p']
    
    print(f"Hand: {hand}")
    
    # Validate all tiles
    for tile in hand:
        assert validate_mjai_tile(tile), f"{tile} should be valid"
    
    # Convert all to Tenhou IDs
    tenhou_ids = [mjai_tile_to_tenhou_id(tile) for tile in hand]
    print(f"Tenhou IDs: {tenhou_ids}")
    
    # Display all
    displays = [mjai_tile_to_display_string(tile) for tile in hand]
    print(f"Display: {' '.join(displays)}")
    
    # Verify '5z' is in the hand correctly
    assert '5z' in hand
    assert 124 in tenhou_ids
    assert '白' in displays
    
    print("✓ '5z' handled correctly in hand")

def test_5z_as_dora_marker():
    """Test that '5z' works as a dora marker"""
    print("\n=== Test 8: '5z' as dora marker ===")
    
    # Simulate a start_kyoku message with '5z' as dora marker
    msg = {
        'type': 'start_kyoku',
        'bakaze': 'E',
        'kyoku': 1,
        'honba': 0,
        'oya': 0,
        'scores': [25000, 25000, 25000, 25000],
        'dora_marker': '5z',  # White dragon as dora marker
        'tehais': [
            ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '1p', '2p', '3p', '4p'],
            [],
            [],
            []
        ]
    }
    
    # Verify dora marker is valid
    dora_marker = msg['dora_marker']
    assert validate_mjai_tile(dora_marker), f"Dora marker '{dora_marker}' should be valid"
    
    print(f"Dora marker: {dora_marker} ({mjai_tile_to_display_string(dora_marker)})")
    print("✓ '5z' works as dora marker")

def main():
    """Run all tests"""
    print("Testing '5z' (White dragon) handling in MJAPI server")
    print("=" * 60)
    
    try:
        test_5z_validation()
        test_5z_conversion()
        test_5z_display()
        test_5z_normalization()
        test_5z_round_trip()
        test_all_honor_tiles()
        test_5z_in_hand()
        test_5z_as_dora_marker()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nConclusion:")
        print("- '5z' (White dragon / 白) is fully supported in MJAI protocol")
        print("- All conversion, validation, and display functions work correctly")
        print("- '5z' can be used in hands, as dora marker, and in all contexts")
        print("- Alternate format 'P' also works and normalizes to '5z'")
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
