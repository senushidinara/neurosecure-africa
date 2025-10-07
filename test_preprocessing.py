import pytest
import numpy as np
from src.preprocessing import filter_noise, normalize_signals, segment_sleep_cycles, SAMPLING_RATE

# Fixture to provide simple mock data
@pytest.fixture
def mock_raw_data():
    """Generates 5 seconds of mock neurodata."""
    duration = 5
    n_samples = duration * SAMPLING_RATE
    # Simple sine wave plus noise
    time = np.linspace(0, duration, n_samples, endpoint=False)
    data = np.sin(2 * np.pi * 10 * time) + 0.1 * np.random.normal(0, 1, n_samples)
    return data

def test_filter_noise_output_shape(mock_raw_data):
    """Test that the output shape of filtering matches the input shape."""
    filtered = filter_noise(mock_raw_data)
    assert filtered.shape == mock_raw_data.shape, "Filtered data shape mismatch"

def test_filter_noise_reduction(mock_raw_data):
    """
    Test that high-frequency noise is conceptually reduced (though hard to test
    specifically without spectral analysis, we check data variance change).
    """
    # Create data with a strong high-frequency component (e.g., 80Hz)
    n_samples = len(mock_raw_data)
    time = np.linspace(0, 5, n_samples, endpoint=False)
    high_freq_noise = np.sin(2 * np.pi * 80 * time) * 2 
    noisy_data = mock_raw_data + high_freq_noise

    filtered = filter_noise(noisy_data, cutoff_high=40) # Cut off 80Hz

    # Check that variance is significantly reduced after filtering high freq component
    # This is a heuristic test, not a precise spectral check.
    assert np.var(filtered) < np.var(noisy_data), "Variance should decrease after filtering noise"


def test_normalize_signals_stats(mock_raw_data):
    """Test that normalized data has a mean close to 0 and std dev close to 1."""
    normalized = normalize_signals(mock_raw_data)
    
    # Check within a small tolerance
    assert np.isclose(np.mean(normalized), 0.0, atol=1e-6), "Normalized mean is not close to zero"
    assert np.isclose(np.std(normalized), 1.0, atol=1e-6), "Normalized standard deviation is not close to one"

def test_segment_sleep_cycles_content():
    """Test if segmentation correctly separates REM and non-REM data points."""
    # Data is simply 0s followed by 1s (total 100 samples)
    data = np.arange(100) 
    # Markers: first 50 are Non-REM (2), next 50 are REM (4)
    markers = np.concatenate([np.full(50, 2), np.full(50, 4)]) 
    
    segmented = segment_sleep_cycles(data, markers)
    
    assert len(segmented['rem']) == 50, "Incorrect number of REM samples"
    assert len(segmented['non_rem']) == 50, "Incorrect number of Non-REM samples"
    
    # Check that the content is correct (REM should be 50-99, Non-REM should be 0-49)
    assert np.array_equal(segmented['non_rem'], data[:50]), "Non-REM segmentation incorrect"
    assert np.array_equal(segmented['rem'], data[50:]), "REM segmentation incorrect"

def test_segment_sleep_cycles_empty():
    """Test scenario where one segment is empty."""
    data = np.arange(50)
    # All markers are Non-REM
    markers = np.full(50, 2)
    
    segmented = segment_sleep_cycles(data, markers)
    
    assert len(segmented['rem']) == 0, "REM segment should be empty"
    assert len(segmented['non_rem']) == 50, "Non-REM segment should contain all data"
