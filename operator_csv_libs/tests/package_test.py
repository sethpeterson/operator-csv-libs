import unittest
from ..package import Package, PACKAGE_FILE_FORMAT, Channel

# CSV mocks
csv_name = 'candidate'
csv_currentCSV = 'csv'

# Package mocks
package_operator = "dummyOperatorName"
package_default_channel = "candidate"
package_file = PACKAGE_FILE_FORMAT
package_file['packageName'] = 'dummy'

class TestPackage(unittest.TestCase):
    def setUp(self):
        
        channels = []
        for channel in package_file['channels']:
            channels.append(Channel(channel['name'], channel['currentCSV']))
        self.mock_package_with_object = Package(package=package_file)
        self.mock_package_with_operator = Package(operator=package_operator, default_channel=package_default_channel)
        self.mock_package_empty = Package()

    def test_init(self):
        # If package_json is passed
        self.assertEqual(self.mock_package_with_object.operator, package_file['packageName'])
        self.assertEqual(self.mock_package_with_object.default_channel, package_file['defaultChannel'])
        self.assertIsInstance(self.mock_package_with_object.channels[0], Channel)
        self.assertIsInstance(self.mock_package_with_object.channels[1], Channel)
        
        # If package_json is not passed
        
        self.assertEqual(self.mock_package_with_operator.operator, package_operator)
        self.assertEqual(self.mock_package_with_operator.default_channel, package_default_channel)
        self.assertEqual(self.mock_package_with_operator.channels, [])
        
        # If no arguments passed
        self.assertEqual(self.mock_package_empty.operator, '')
        self.assertEqual(self.mock_package_empty.default_channel, '')
        self.assertEqual(self.mock_package_empty.channels, [])
    
    def test_get_channel(self):
        channel_name = '{}-candidate'
        got_channel = self.mock_package_with_object.get_channel(channel_name)
        self.assertIsInstance(got_channel, Channel)
        self.assertEqual(got_channel.get_name(), channel_name)

    def test_get_channels(self):
        got_channels = self.mock_package_with_object.get_channels()
        self.assertIsInstance(got_channels, list)
        self.assertEqual(got_channels, self.mock_package_with_object.channels)
    
    def test_create_channel(self):
        new_channel_name = '{}-snapshot'
        new_channel_current_csv = 'csv3'

        self.assertEqual(len(self.mock_package_with_object.channels), 3)

        self.mock_package_with_object.create_channel(new_channel_name, new_channel_current_csv, default=True)

        # Check if length of channels list increased by 1
        self.assertEqual(len(self.mock_package_with_object.channels), 4)
        self.assertIsInstance(self.mock_package_with_object.channels[-1], Channel)
        self.assertEqual(self.mock_package_with_object.channels[-1].get_name(), new_channel_name)
        self.assertEqual(self.mock_package_with_object.channels[-1].get_current_csv(), new_channel_current_csv)
        self.assertEqual(self.mock_package_with_object.default_channel, new_channel_name)
    
    def test_get_formatted(self):
        self.assertEqual(self.mock_package_with_object.get_formatted(), package_file)
        
    def test_set_default_channel(self):
        new_default_channel = '{}-fast'
        self.mock_package_with_object.set_default_channel(new_default_channel)
        self.assertEqual(self.mock_package_with_object.default_channel, new_default_channel)
    
    def test_set_operator(self):
        new_operator = 'newOperatorName'
        self.mock_package_with_object.set_operator(new_operator)
        self.assertEqual(self.mock_package_with_object.operator, new_operator)
    
    def test_update_channel(self):
        channel_name = '{}-candidate'
        new_csv = 'csv4'
        
        self.mock_package_with_object.update_channel(channel=channel_name, new_csv=new_csv)
        for c in self.mock_package_with_object.channels:
            if c.get_name() == channel_name:
                # print(c.get_name(), c.get_current_csv())
                self.assertEqual(c.get_current_csv(), new_csv)
        
        
class TestChannel(unittest.TestCase):
    def setUp(self):
        self.channel = Channel(csv_name, csv_currentCSV)

    def test_init(self):
        self.assertEqual(self.channel.name, csv_name)
        self.assertEqual(self.channel.currentCSV, csv_currentCSV)

    def test_get_current_csv(self):
        self.assertEqual(csv_currentCSV, self.channel.get_current_csv())

    def test_set_current_csv(self):
        newCSV = 'csv2'
        self.channel.set_current_csv(newCSV)
        self.assertEqual(self.channel.get_current_csv(), newCSV)

    def test_get_name(self):
        self.assertEqual(csv_name, self.channel.get_name())

    def test_set_name(self):
        newName = 'csv2'
        self.channel.set_name(newName)
        self.assertEqual(self.channel.get_name(), newName)
    
        