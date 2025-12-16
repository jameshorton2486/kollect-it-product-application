import unittest
from modules.config_validator import ConfigValidator

class TestConfigValidator(unittest.TestCase):
    def test_validate_minimal_config(self):
        # minimal valid-ish config structure
        cfg = {
            "api": {"SERVICE_API_KEY": "abc", "production_url": "https://example.com"},
            "imagekit": {"public_key": "pk", "private_key": "sk", "url_endpoint": "https://ik"},
            "ai": {"model": "test-model"},
            "categories": {"collectibles": {"prefix": "COLL", "name": "Collectibles"}},
            "image_processing": {"max_dimension": 2400, "webp_quality": 88}
        }
        validator = ConfigValidator(cfg)
        result = validator.validate()
        # older validators return tuple (is_valid, errors, warnings)
        if isinstance(result, tuple):
            is_valid, errors, warnings = result
            self.assertTrue(is_valid)
        else:
            self.assertTrue(result.get("valid", False))

if __name__ == '__main__':
    unittest.main()
