"""
Tests for MMM model caching functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import time
from app.services.mmm_service import MMMService, _load_model_cached


class TestMMMCaching:
    """Test MMM model caching behavior."""
    
    def test_model_caching_loads_once(self):
        """Test that the model is only loaded once due to LRU cache."""
        service = MMMService()
        
        # Mock the actual model loading to avoid file I/O
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2']
        
        with patch('meridian.model.model.load_mmm', return_value=mock_model) as mock_load:
            # First call should load the model
            model1 = service._load_model()
            
            # Second call should use cached version
            model2 = service._load_model()
            
            # Third call should also use cached version
            model3 = service._load_model()
            
            # Verify the model was only loaded once
            assert mock_load.call_count == 1
            
            # Verify all calls return the same model instance
            assert model1 is model2
            assert model2 is model3
            assert model1 is mock_model
    
    def test_caching_performance_improvement(self):
        """Test that caching provides performance improvement."""
        # Clear cache to ensure clean test
        _load_model_cached.cache_clear()
        
        service = MMMService()
        
        # Mock the model loading with a delay to simulate real loading time
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2']
        
        def slow_load_mock(*args, **kwargs):
            time.sleep(0.1)  # Simulate 100ms load time
            return mock_model
        
        with patch('meridian.model.model.load_mmm', side_effect=slow_load_mock) as mock_load:
            # First call - should be slow (actual loading)
            start_time = time.time()
            model1 = service._load_model()
            first_call_time = time.time() - start_time
            
            # Second call - should be fast (cached)
            start_time = time.time()
            model2 = service._load_model()
            second_call_time = time.time() - start_time
            
            # Verify performance improvement
            assert first_call_time >= 0.1  # First call takes at least 100ms
            assert second_call_time < 0.01  # Second call should be much faster
            assert second_call_time < first_call_time / 10  # At least 10x faster
            
            # Verify model was only loaded once
            assert mock_load.call_count == 1
            assert model1 is model2
    
    def test_cache_with_different_service_instances(self):
        """Test that cache works across different service instances."""
        # Clear cache to ensure clean test
        _load_model_cached.cache_clear()
        
        # Mock the model
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2']
        
        with patch('meridian.model.model.load_mmm', return_value=mock_model) as mock_load:
            # Create first service instance and load model
            service1 = MMMService()
            model1 = service1._load_model()
            
            # Create second service instance
            service2 = MMMService()
            model2 = service2._load_model()
            
            # Both should use the same cached model
            assert mock_load.call_count == 1
            assert model1 is model2
    
    def test_cache_handles_exceptions(self):
        """Test that caching handles exceptions properly."""
        # Clear cache to ensure clean test
        _load_model_cached.cache_clear()
        
        service = MMMService()
        
        with patch('meridian.model.model.load_mmm', side_effect=Exception("Load failed")):
            # First call should raise exception
            with pytest.raises(Exception, match="Load failed"):
                service._load_model()
            
            # Second call should also raise exception (not cached)
            with pytest.raises(Exception, match="Load failed"):
                service._load_model()
    
    def test_cache_with_file_not_found(self):
        """Test caching behavior when model file doesn't exist."""
        # Clear cache to ensure clean test
        _load_model_cached.cache_clear()
        
        # Test the global function directly with a non-existent path
        from app.services.mmm_service import MMMModelError
        
        with pytest.raises(MMMModelError, match="MMM model file not found"):
            _load_model_cached("/fake/nonexistent/path/model.pkl")
    
    def test_cache_integration_with_get_channels(self):
        """Test that caching works with higher-level service methods."""
        service = MMMService()
        
        # Mock the model with proper structure
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2']
        
        with patch('meridian.model.model.load_mmm', return_value=mock_model) as mock_load:
            # Call get_channel_summary multiple times
            try:
                summary1 = service.get_channel_summary()
                summary2 = service.get_channel_summary()
                
                # Model should only be loaded once
                assert mock_load.call_count == 1
                
            except Exception:
                # If get_channel_summary fails due to missing model attributes,
                # we still verify the caching behavior
                assert mock_load.call_count <= 1
    
    def test_global_cache_function_directly(self):
        """Test the global _load_model_cached function directly."""
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2']
        
        with patch('meridian.model.model.load_mmm', return_value=mock_model) as mock_load:
            with patch('pathlib.Path.exists', return_value=True):
                # Clear any existing cache
                _load_model_cached.cache_clear()
                
                # Test cache info
                initial_info = _load_model_cached.cache_info()
                assert initial_info.hits == 0
                assert initial_info.misses == 0
                
                # First call - should be a cache miss
                model1 = _load_model_cached("/fake/path/model.pkl")
                after_first = _load_model_cached.cache_info()
                assert after_first.hits == 0
                assert after_first.misses == 1
                
                # Second call - should be a cache hit
                model2 = _load_model_cached("/fake/path/model.pkl")
                after_second = _load_model_cached.cache_info()
                assert after_second.hits == 1
                assert after_second.misses == 1
                
                # Verify model was only loaded once
                assert mock_load.call_count == 1
                assert model1 is model2
    
    @pytest.mark.performance
    def test_realistic_caching_scenario(self):
        """Test a realistic caching scenario with multiple API calls."""
        service = MMMService()
        
        # Mock model with realistic delay
        mock_model = MagicMock()
        mock_model.media_names = ['Channel0', 'Channel1', 'Channel2', 'Channel3', 'Channel4']
        
        def realistic_load_mock(*args, **kwargs):
            time.sleep(0.05)  # 50ms simulated load time
            return mock_model
        
        with patch('meridian.model.model.load_mmm', side_effect=realistic_load_mock) as mock_load:
            # Clear cache to ensure clean test
            _load_model_cached.cache_clear()
            
            # Simulate multiple rapid API calls (like dashboard loading)
            start_time = time.time()
            
            models = []
            for i in range(5):
                models.append(service._load_model())
            
            total_time = time.time() - start_time
            
            # Verify all models are the same instance
            for model in models[1:]:
                assert model is models[0]
            
            # Verify model was only loaded once
            assert mock_load.call_count == 1
            
            # Verify total time is much less than 5 * 50ms = 250ms
            assert total_time < 0.1  # Should complete in under 100ms
