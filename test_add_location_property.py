import unittest
from unittest.mock import patch, mock_open
import json
import add_location_property

class TestAddLocationProperty(unittest.TestCase):

    def test_is_weapon(self):
        # Case: Category is 'Weapon Systems'
        self.assertTrue(add_location_property.is_weapon({'category': 'Weapon Systems'}))
        # Case: ID is 'sensor_decoy'
        self.assertTrue(add_location_property.is_weapon({'id': 'sensor_decoy'}))
        # Case: Other category and ID
        self.assertFalse(add_location_property.is_weapon({'category': 'Defense Systems', 'id': 'not_a_decoy'}))
        # Case: Missing keys
        self.assertFalse(add_location_property.is_weapon({}))

    def test_is_engine(self):
        # Case: Group is 'Sublight Drives' and has speed stats
        self.assertTrue(add_location_property.is_engine({
            'group': 'Sublight Drives',
            'stats': {'speed': 5}
        }))
        # Case: Group is 'Sublight Drives' but missing stats
        self.assertFalse(add_location_property.is_engine({'group': 'Sublight Drives'}))
        # Case: Group is 'Sublight Drives' but missing speed in stats
        self.assertFalse(add_location_property.is_engine({
            'group': 'Sublight Drives',
            'stats': {}
        }))
        # Case: Other group
        self.assertFalse(add_location_property.is_engine({'group': 'Thrusters'}))
        # Case: Missing keys
        self.assertFalse(add_location_property.is_engine({}))

    def test_get_location(self):
        # Case: Weapon
        self.assertEqual(add_location_property.get_location({'category': 'Weapon Systems'}), 'Hardpoint')
        # Case: Engine
        self.assertEqual(add_location_property.get_location({
            'group': 'Sublight Drives',
            'stats': {'speed': 5}
        }), 'Aft Section')
        # Case: Modification
        self.assertEqual(add_location_property.get_location({'category': 'Modifications'}), 'Installed')
        # Case: Weapon Upgrade (as category, though it might be a group in practice)
        self.assertEqual(add_location_property.get_location({'category': 'Weapon Upgrades'}), 'Installed')
        # Case: Storage
        self.assertEqual(add_location_property.get_location({'group': 'Storage'}), 'Cargo Hold')
        # Case: Default
        self.assertEqual(add_location_property.get_location({'category': 'Starship Accessories'}), 'Internal Bay')
        # Case: Empty/Unknown
        self.assertEqual(add_location_property.get_location({}), 'Internal Bay')

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        'EQUIPMENT': [
            {'id': 'w1', 'category': 'Weapon Systems'},
            {'id': 'e1', 'group': 'Sublight Drives', 'stats': {'speed': 2}},
            {'id': 'm1', 'category': 'Modifications'},
            {'id': 's1', 'group': 'Storage'},
            {'id': 'a1', 'category': 'Starship Accessories'}
        ]
    }))
    @patch('json.dump')
    def test_main(self, mock_json_dump, mock_file_open):
        add_location_property.main()

        # Check if open was called for reading and writing
        mock_file_open.assert_any_call('data.json', 'r', encoding='utf-8')
        mock_file_open.assert_any_call('data.json', 'w', encoding='utf-8')

        # Check what was passed to json.dump
        args, _ = mock_json_dump.call_args
        written_data = args[0]

        expected_locations = {
            'w1': 'Hardpoint',
            'e1': 'Aft Section',
            'm1': 'Installed',
            's1': 'Cargo Hold',
            'a1': 'Internal Bay'
        }

        for item in written_data['EQUIPMENT']:
            self.assertEqual(item['location'], expected_locations[item['id']])

if __name__ == '__main__':
    unittest.main()
