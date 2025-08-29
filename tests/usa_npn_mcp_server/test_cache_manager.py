"""Unit tests for CacheManager class."""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

from usa_npn_mcp_server.api_client import CacheManager


class TestCacheManager:
    """Test suite for CacheManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.cache_manager = CacheManager(max_size_mb=1, max_age_minutes=1)
        self.sample_data = [
            {"id": 1, "name": "test1", "value": 10.5},
            {"id": 2, "name": "test2", "value": 20.3},
        ]
        self.sample_params = {"start_date": "2025-01-01", "end_date": "2025-01-31"}

    def test_generate_hash_consistency(self):
        """Test that generate_hash produces consistent results for same inputs."""
        tool_name = "status-intensity"
        params = {"start_date": "2025-01-01", "end_date": "2025-01-31"}

        hash1 = self.cache_manager.generate_hash(tool_name, params)
        hash2 = self.cache_manager.generate_hash(tool_name, params)

        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length

    def test_generate_hash_different_inputs(self):
        """Test that different inputs produce different hashes."""
        tool_name = "status-intensity"
        params1 = {"start_date": "2025-01-01", "end_date": "2025-01-31"}
        params2 = {"start_date": "2025-02-01", "end_date": "2025-02-28"}

        hash1 = self.cache_manager.generate_hash(tool_name, params1)
        hash2 = self.cache_manager.generate_hash(tool_name, params2)

        assert hash1 != hash2

    def test_generate_hash_param_order_independence(self):
        """Test that parameter order doesn't affect hash."""
        tool_name = "status-intensity"
        params1 = {
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "species_id": 3,
        }
        params2 = {
            "species_id": 3,
            "end_date": "2025-01-31",
            "start_date": "2025-01-01",
        }

        hash1 = self.cache_manager.generate_hash(tool_name, params1)
        hash2 = self.cache_manager.generate_hash(tool_name, params2)

        assert hash1 == hash2

    def test_add_entry_basic(self):
        """Test basic entry addition to cache."""
        hash_id = "test_hash_123"
        tool_name = "status-intensity"

        self.cache_manager.add_entry(
            hash_id, tool_name, self.sample_params, self.sample_data
        )

        assert hash_id in self.cache_manager.cache
        entry = self.cache_manager.cache[hash_id]
        assert entry["raw_data"] == self.sample_data
        assert entry["metadata"]["tool_name"] == tool_name
        assert entry["metadata"]["params"] == self.sample_params
        assert entry["metadata"]["record_count"] == len(self.sample_data)
        assert isinstance(entry["metadata"]["timestamp"], datetime)
        assert entry["metadata"]["size_bytes"] > 0

    def test_get_entry_existing(self):
        """Test retrieving an existing cache entry."""
        hash_id = "test_hash_123"
        tool_name = "status-intensity"

        self.cache_manager.add_entry(
            hash_id, tool_name, self.sample_params, self.sample_data
        )
        entry = self.cache_manager.get_entry(hash_id)

        assert entry is not None
        assert entry["raw_data"] == self.sample_data
        assert entry["metadata"]["tool_name"] == tool_name

    def test_get_entry_nonexistent(self):
        """Test retrieving a non-existent cache entry."""
        entry = self.cache_manager.get_entry("nonexistent_hash")
        assert entry is None

    def test_get_entry_expired(self):
        """Test that expired entries are automatically removed."""
        hash_id = "test_hash_123"
        tool_name = "status-intensity"

        # Add entry
        self.cache_manager.add_entry(
            hash_id, tool_name, self.sample_params, self.sample_data
        )

        # Mock time to simulate expiration
        with patch("usa_npn_mcp_server.api_client.datetime") as mock_datetime:
            future_time = datetime.now() + timedelta(minutes=2)
            mock_datetime.now.return_value = future_time

            entry = self.cache_manager.get_entry(hash_id)
            assert entry is None
            assert hash_id not in self.cache_manager.cache

    def test_cleanup_cache_expired_entries(self):
        """Test cleanup removes expired entries."""
        hash_id1 = "test_hash_1"
        hash_id2 = "test_hash_2"
        tool_name = "status-intensity"

        # Add entries
        self.cache_manager.add_entry(
            hash_id1, tool_name, self.sample_params, self.sample_data
        )
        self.cache_manager.add_entry(
            hash_id2, tool_name, self.sample_params, self.sample_data
        )

        assert len(self.cache_manager.cache) == 2

        # Mock time to expire first entry
        with patch("usa_npn_mcp_server.api_client.datetime") as mock_datetime:
            # First entry expired, second still valid
            future_time = datetime.now() + timedelta(minutes=2)
            mock_datetime.now.return_value = future_time

            # Manually set second entry timestamp to be recent
            self.cache_manager.cache[hash_id2]["metadata"]["timestamp"] = (
                future_time - timedelta(seconds=30)
            )

            self.cache_manager.cleanup_cache()

            assert hash_id1 not in self.cache_manager.cache
            assert hash_id2 in self.cache_manager.cache

    def test_cleanup_cache_size_limit(self):
        """Test cleanup removes oldest entries when size limit exceeded."""
        # Use smaller cache for this test
        small_cache = CacheManager(max_size_mb=0.1, max_age_minutes=10)  # 100KB limit

        # Create data that will exceed the limit
        large_data = [{"data": "x" * 50000}]  # ~50KB per entry

        hash_id1 = "test_hash_1"
        hash_id2 = "test_hash_2"
        hash_id3 = "test_hash_3"
        tool_name = "status-intensity"

        # Add entries one by one
        small_cache.add_entry(hash_id1, tool_name, self.sample_params, large_data)
        time.sleep(0.001)
        small_cache.add_entry(hash_id2, tool_name, self.sample_params, large_data)
        time.sleep(0.001)
        small_cache.add_entry(
            hash_id3, tool_name, self.sample_params, large_data
        )  # Should trigger cleanup

        # Should have removed oldest entries to stay under size limit
        total_size = small_cache.get_total_size()
        assert total_size <= small_cache.max_size_bytes

        # At least one entry should remain
        assert len(small_cache.cache) >= 1

    def test_get_total_size(self):
        """Test total cache size calculation."""
        assert self.cache_manager.get_total_size() == 0

        hash_id = "test_hash_123"
        tool_name = "status-intensity"

        self.cache_manager.add_entry(
            hash_id, tool_name, self.sample_params, self.sample_data
        )

        total_size = self.cache_manager.get_total_size()
        assert total_size > 0
        assert total_size == self.cache_manager.cache[hash_id]["metadata"]["size_bytes"]

    def test_get_cache_stats_empty(self):
        """Test cache statistics for empty cache."""
        stats = self.cache_manager.get_cache_stats()

        assert stats["total_entries"] == 0
        assert stats["total_size_mb"] == 0.0
        assert stats["entries"] == []

    def test_get_cache_stats_with_entries(self):
        """Test cache statistics with entries."""
        hash_id1 = "test_hash_1"
        hash_id2 = "test_hash_2"
        tool_name = "status-intensity"
        params1 = {"start_date": "2025-01-01", "end_date": "2025-01-31", "state": "CA"}
        params2 = {
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
            "species_id": 3,
        }

        self.cache_manager.add_entry(hash_id1, tool_name, params1, self.sample_data)
        time.sleep(0.001)
        self.cache_manager.add_entry(hash_id2, tool_name, params2, self.sample_data)

        stats = self.cache_manager.get_cache_stats()

        assert stats["total_entries"] == 2
        assert stats["total_size_mb"] >= 0  # Size should be non-negative
        assert len(stats["entries"]) == 2

        # Check entry structure
        entry = stats["entries"][0]  # Most recent first
        assert "hash_id" in entry
        assert "tool_name" in entry
        assert "timestamp" in entry
        assert "record_count" in entry
        assert "size_kb" in entry
        assert "params_summary" in entry

        # Check params_summary filtering (should include start_date, end_date, etc.)
        assert "start_date" in entry["params_summary"]
        assert "end_date" in entry["params_summary"]

        # Verify sorting (newest first)
        assert stats["entries"][0]["timestamp"] >= stats["entries"][1]["timestamp"]

        # Verify individual entry sizes are positive
        assert stats["entries"][0]["size_kb"] > 0
        assert stats["entries"][1]["size_kb"] > 0

    def test_cache_manager_custom_limits(self):
        """Test CacheManager with custom size and age limits."""
        custom_cache = CacheManager(max_size_mb=5, max_age_minutes=30)

        assert custom_cache.max_size_bytes == 5 * 1024 * 1024
        assert custom_cache.max_age == timedelta(minutes=30)

    def test_multiple_entries_same_tool(self):
        """Test adding multiple entries for the same tool with different parameters."""
        tool_name = "status-intensity"
        params1 = {"start_date": "2025-01-01", "end_date": "2025-01-31"}
        params2 = {"start_date": "2025-02-01", "end_date": "2025-02-28"}

        hash_id1 = self.cache_manager.generate_hash(tool_name, params1)
        hash_id2 = self.cache_manager.generate_hash(tool_name, params2)

        self.cache_manager.add_entry(hash_id1, tool_name, params1, self.sample_data)
        self.cache_manager.add_entry(hash_id2, tool_name, params2, self.sample_data)

        assert len(self.cache_manager.cache) == 2
        assert hash_id1 != hash_id2

        entry1 = self.cache_manager.get_entry(hash_id1)
        entry2 = self.cache_manager.get_entry(hash_id2)

        assert entry1["metadata"]["params"] == params1
        assert entry2["metadata"]["params"] == params2

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        hash_id = "test_hash_empty"
        tool_name = "status-intensity"
        empty_data = []

        self.cache_manager.add_entry(hash_id, tool_name, self.sample_params, empty_data)

        entry = self.cache_manager.get_entry(hash_id)
        assert entry is not None
        assert entry["raw_data"] == []
        assert entry["metadata"]["record_count"] == 0

    def test_large_parameter_values(self):
        """Test handling of large parameter values in hash generation."""
        tool_name = "status-intensity"
        large_params = {
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "species_id": list(range(1000)),  # Large list
            "description": "x" * 10000,  # Large string
        }

        hash_id = self.cache_manager.generate_hash(tool_name, large_params)

        assert len(hash_id) == 32  # MD5 hash should still be 32 characters

        # Should be able to add and retrieve
        self.cache_manager.add_entry(hash_id, tool_name, large_params, self.sample_data)
        entry = self.cache_manager.get_entry(hash_id)
        assert entry is not None
