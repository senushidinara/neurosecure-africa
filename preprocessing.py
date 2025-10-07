import numpy as np
from scipy import signal

# ==============================================================================
# Constants (Mock values for brainwave frequencies in Hz)
# ==============================================================================
# Delta (0.5–4 Hz), Theta (4–8 Hz), Alpha (8–12 Hz), Beta (12–30 Hz), Gamma (30–100+ Hz)
GAMMA_FREQ_RANGE = (30, 100)
THETA_FREQ_RANGE = (4, 8)
SAMPLING_RATE = 256 # Hz (typical EEG sampling rate)

def filter_noise(raw_data: np.ndarray, fs: int = SAMPLING_RATE, cutoff_low: float = 0.5, cutoff_high: float = 120) -> np.ndarray:
    """
    Filters environmental and biological noise from raw EEG/MEG signals.

    This function applies a bandpass filter to keep only relevant brainwave frequencies.
    Uses a simple Butterworth filter for demonstration.

    Args:
        raw_data: 1D NumPy array of raw time-series neurodata.
        fs: Sampling frequency in Hz.
        cutoff_low: Lower cutoff frequency (Hz).
        cutoff_high: Upper cutoff frequency (Hz).

    Returns:
        1D NumPy array of filtered data.
    """
    if raw_data.ndim != 1:
        # Assuming single channel for simplicity in this example
        print("Warning: Data should be 1D for this simple filter implementation.")
        return raw_data

    nyquist = 0.5 * fs
    low = cutoff_low / nyquist
    high = cutoff_high / nyquist
    
    # Create a 4th-order Butterworth filter
    b, a = signal.butter(4, [low, high], btype='band')
    
    # Apply the filter
    filtered_data = signal.lfilter(b, a, raw_data)
    
    return filtered_data

def normalize_signals(data: np.ndarray) -> np.ndarray:
    """
    Normalizes the amplitude of the filtered brain signals using Z-score normalization.

    Args:
        data: 1D NumPy array of filtered neurodata.

    Returns:
        1D NumPy array of normalized data.
    """
    mean = np.mean(data)
    std_dev = np.std(data)
    
    # Avoid division by zero if std_dev is near zero
    if std_dev < 1e-6:
        return data - mean
    
    normalized_data = (data - mean) / std_dev
    return normalized_data

def segment_sleep_cycles(normalized_data: np.ndarray, sleep_stage_markers: np.ndarray) -> dict:
    """
    Segments the normalized data into REM and non-REM cycles based on external markers.

    In a real system, these markers would come from an automatic sleep staging algorithm.

    Args:
        normalized_data: 1D NumPy array of normalized neurodata.
        sleep_stage_markers: Array of labels (e.g., 0=Wake, 1=NREM1, 2=NREM2, 3=SWS, 4=REM).

    Returns:
        A dictionary containing segmented 'rem' and 'non_rem' data arrays.
    """
    # Mock segmentation logic:
    rem_indices = np.where(sleep_stage_markers == 4)[0]
    non_rem_indices = np.where(sleep_stage_markers < 4)[0] # Simplified to include all non-wake stages

    segmented = {
        'rem': normalized_data[rem_indices] if rem_indices.size > 0 else np.array([]),
        'non_rem': normalized_data[non_rem_indices] if non_rem_indices.size > 0 else np.array([]),
    }

    return segmented

# Example Usage:
if __name__ == "__main__":
    # Create mock raw data (10 seconds at 256Hz)
    mock_time = np.linspace(0, 10, 10 * SAMPLING_RATE, endpoint=False)
    # Simulate a signal with some noise (e.g., 50Hz power line noise)
    mock_raw_data = np.sin(2 * np.pi * 5 * mock_time) + 0.5 * np.sin(2 * np.pi * 50 * mock_time) + np.random.normal(0, 0.5, len(mock_time))

    print(f"Original Data shape: {mock_raw_data.shape}")

    # 1. Filter Noise
    filtered_data = filter_noise(mock_raw_data)
    print(f"Filtered Data shape: {filtered_data.shape}")

    # 2. Normalize Signals
    normalized_data = normalize_signals(filtered_data)
    print(f"Normalized Data stats (mean, std): {np.mean(normalized_data):.2f}, {np.std(normalized_data):.2f}")

    # 3. Segment Sleep Cycles (Mock markers: alternating 1 second segments of REM (4) and Non-REM (2))
    markers = np.concatenate([np.full(SAMPLING_RATE, 2), np.full(SAMPLING_RATE, 4)] * 5)
    
    segmented_data = segment_sleep_cycles(normalized_data, markers)
    print(f"REM Data points: {len(segmented_data['rem'])}")
    print(f"Non-REM Data points: {len(segmented_data['non_rem'])}")
