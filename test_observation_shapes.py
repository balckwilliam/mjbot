#!/usr/bin/env python3
"""
Test script to verify observation shape handling in ot_server
"""
import numpy as np
import sys

def test_observation_processing():
    """Test that different observation shapes are handled correctly"""
    
    # Test case 1: Original 291 features (2D)
    obs_291_2d = np.random.rand(291, 34)
    print(f"Test 1: Shape {obs_291_2d.shape} (original 2D format)")
    
    # Test case 2: Original 291 features (flattened)
    obs_291_flat = np.random.rand(291 * 34)
    print(f"Test 2: Length {len(obs_291_flat)} (original flattened format)")
    
    # Test case 3: Extended 1012 features (2D)
    obs_1012_2d = np.random.rand(1012, 34)
    print(f"Test 3: Shape {obs_1012_2d.shape} (extended 2D format)")
    
    # Test case 4: Extended 1012 features (flattened)
    obs_1012_flat = np.random.rand(1012 * 34)
    print(f"Test 4: Length {len(obs_1012_flat)} (extended flattened format)")
    
    # Test the extraction logic
    def extract_features(obs):
        """Simulate the extraction logic from ot_server.py"""
        if isinstance(obs, list):
            obs = np.array(obs)
        
        if hasattr(obs, 'ndim') and obs.ndim == 2:
            if obs.shape[1] == 34:
                if obs.shape[0] == 291:
                    state_array = obs
                    print(f"  ✓ Accepted as-is: {state_array.shape}")
                elif obs.shape[0] > 291:
                    state_array = obs[:291, :]
                    print(f"  ✓ Extracted first 291 features: {obs.shape} -> {state_array.shape}")
                else:
                    print(f"  ✗ Too few features: {obs.shape}")
                    return None
            else:
                print(f"  ✗ Invalid second dimension: {obs.shape}")
                return None
        elif len(obs) == 291 * 34:
            state_array = obs.reshape(291, 34)
            print(f"  ✓ Reshaped from flat: {len(obs)} -> {state_array.shape}")
        elif len(obs) > 291 * 34 and len(obs) % 34 == 0:
            num_features = len(obs) // 34
            state_array = obs.reshape(num_features, 34)[:291, :]
            print(f"  ✓ Reshaped and extracted: {len(obs)} ({num_features}x34) -> {state_array.shape}")
        else:
            print(f"  ✗ Invalid observation length: {len(obs)}")
            return None
        
        return state_array
    
    # Run tests
    print("\nRunning extraction tests:")
    print("-" * 60)
    
    result1 = extract_features(obs_291_2d)
    assert result1 is not None and result1.shape == (291, 34), "Test 1 failed"
    
    result2 = extract_features(obs_291_flat)
    assert result2 is not None and result2.shape == (291, 34), "Test 2 failed"
    
    result3 = extract_features(obs_1012_2d)
    assert result3 is not None and result3.shape == (291, 34), "Test 3 failed"
    
    result4 = extract_features(obs_1012_flat)
    assert result4 is not None and result4.shape == (291, 34), "Test 4 failed"
    
    print("-" * 60)
    print("✓ All tests passed!")
    
    # Verify that the extracted features are the first 291 rows
    extracted = obs_1012_2d[:291, :]
    assert np.array_equal(result3, extracted), "Test 3 extraction mismatch"
    print("✓ Verified that extraction takes first 291 features")
    
    return True

if __name__ == '__main__':
    try:
        test_observation_processing()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
