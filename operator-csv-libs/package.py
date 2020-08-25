import os, yaml

# Channels are expected to be named <major>.<minor>-{candidate,fast,release}
PACKAGE_FILE_FORMAT = {
    'channels': [
            {'name': '{}-candidate',
            'currentCSV': ''},
            {'name': '{}-fast',
            'currentCSV': ''},
            {'name': '{}-stable',
            'currentCSV': ''}
    ],
    'defaultChannel': '{}-{}',
    'packageName': ''
}

def create_or_update_package(path, operator, channel, release, majorminor, default_channel, log):
    """ Crate or update a channel for a package. Creates the package file if it doesn't exist

    Args:
        path (string): Path of the operator manifests
        operator (string): Name of the oooperator
        channel (string): Partial channel name to add the CSV to (typically {candidate,fast,stable}). Does not require full name
        release (string): Release version. (i.e. 2.0.0)
        majorminor (string): Major, Minor version (i.e. 2.0)
        default_channel (string): Default channel when creating new package manifest
        log ([type]): [description]

    Returns:
        [bool]: Whether package was successfully created or updated
    """
    package_file = '{}/{}.package.yaml'.format(path, operator)
    # If package file doesn't exist, we'll create it
    if not os.path.isfile(package_file):
        log.info('Did not find package info, starting from blank template')
        package=PACKAGE_FILE_FORMAT

        # Update the major-minor channel name
        for c in package['channels']:
            c['name'] = c['name'].format(majorminor)
        package['defaultChannel'] = package['defaultChannel'].format(majorminor, default_channel)

        package['packageName'] = operator

        # Since no channels are populated we need to populate them all
        for c in package['channels']:
            c['currentCSV'] = '{}.v{}'.format(operator,release)
    else:
        log.info('Reading current package info from {}'.format(package_file))
        with open(package_file, 'r') as stream:
            package = yaml.load(stream, Loader=yaml.SafeLoader)

    # Update the latest CSV in the given channel
    for c in package['channels']:
        if channel in c['name']:
            log.info('Updating {} currentCSV to {}'.format(c['name'], '{}.v{}'.format(operator,release)))
            c['currentCSV'] = '{}.v{}'.format(operator,release)

    log.info('Wrinting out package file {}'.format(package_file))
    with open(package_file, 'w+') as f:
            yaml.dump(package, f, explicit_start=False, default_flow_style = False)

    return True