import argparse
import configparser
import luadata
import os
import shutil
import sys


# Command to modify mission file will end up looking like this:
# addMissionDefaults <configFile> <missionFile> [opts]
# Note: configFile name should be in the form of (e.g.) 'A-10C_2.cfg'
# as the program uses the filename to define ac types

config_file = 'A-10C_2.cfg'
V_NONE = 0
V_HIGH = 3

# Config file constants
UHF_FREQ_LEN = 9
VHF_AM_FREQ_LEN = 9
VHF_FM_FREQ_LEN = 8
UHF_NUM_PRESETS = 20
VHF_AM_NUM_PRESETS = 20
VHF_FM_NUM_PRESETS = 20

# Directory tree constants
WORKING_DIRNAME = 'working_dir'
UHF_DIR_NAME = 'UHF_RADIO'
VHF_AM_DIR_NAME = 'VHF_AM_RADIO'
VHF_FM_DIR_NAME = 'VHF_FM_RADIO'

# Front panel default names
#  <key> is config file parameter name
#  <val> is lua expanded name as needed within lua mission file
FRONT_PANEL_SELNS = {'dialMode': 'mode_dial',
                     'dialSel': 'selection_dial',
                     'dialChan': 'channel_dial',
                     'manFreq': 'manual_frequency'}

uhf_freqs = {}
uhf_presets = {}
vhf_am_freqs = {}
vhf_am_presets = {}
vhf_fm_freqs = {}
vhf_fm_presets = {}
uhf_ac_list = []
vhf_am_ac_list = []
vhf_fm_ac_list = []


def getpresets(con, radio, num_presets, freq_len):
    """
    :param con: config file structure
    :param radio: Radio type (eg UHF_RADIO)
    :param num_presets: Number of presets possible
    :param freq_len: Length of frequency value (# of digits)
    :return: populated aircraft instance number list, dictionary of preset#:freq
    """

    loc_ac_list = []
    loc_freqs = {}
    loc_selns = {}

    if con.has_section(radio):
        if con.has_option(radio, 'acList'):
            loc_ac_list = con[radio]['acList'].split(',')
        else:
            loc_ac_list = '1'

        if verbosity > 1:
            print(f'Found {radio} section')
            print(f'acList = {loc_ac_list}')

        for i in range(0, num_presets+1):
            try:
                loc_freqs[i] = con[radio][f'Pre_{i}'].replace('.', '').ljust(freq_len, '0')
                if verbosity > 1:
                    print(f'Preset [{i}] -> {loc_freqs[i]}')
            except KeyError:
                if verbosity > 2:
                    print(f'Preset [{i}] missing')

        for sel in FRONT_PANEL_SELNS:
            if con.has_option(radio, sel):
                if verbosity > 1:
                    print(f'Found radio panel section {sel} -> {con[radio][sel]}')
                if '.' in con[radio][sel]:   # Pad any frequency entries
                    loc_selns[FRONT_PANEL_SELNS[sel]] = con[radio][sel].replace('.', '').ljust(freq_len, '0')
                else:
                    loc_selns[FRONT_PANEL_SELNS[sel]] = con[radio][sel]

    return loc_ac_list, loc_freqs, loc_selns


# Parse args
parser = argparse.ArgumentParser(description='Python script to add startup defaults to DCS mission file.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input_filename')
parser.add_argument('-c', '--config', help='Name of configuration file.', default=config_file)
parser.add_argument('-v', '--verbosity', help=f'Verbosity level {V_NONE} (silent) to {V_HIGH} (most verbose).',
                    type=int, default=1)
args = parser.parse_args()
ac_type = args.config[:-4]
verbosity = args.verbosity

# Parse config file
config = configparser.ConfigParser()
try:
    config.read(args.config)
except (configparser.MissingSectionHeaderError, configparser.DuplicateOptionError, configparser.DuplicateSectionError,
        configparser.ParsingError, configparser.InterpolationError) as err:
    print(err)
    print('*** Exiting due to malformed config file ***')
    exit(-1)

if verbosity > 0:
    print(f'{sys.argv[0]}: Reading mission defaults from: {args.config}')

# Get radio frequency presets
uhf_ac_list, uhf_freqs, uhf_presets = getpresets(config, 'UHF_RADIO', UHF_NUM_PRESETS, UHF_FREQ_LEN)
vhf_am_ac_list, vhf_am_freqs, vhf_am_presets = getpresets(config, 'VHF_AM_RADIO', VHF_AM_NUM_PRESETS, VHF_AM_FREQ_LEN)
vhf_fm_ac_list, vhf_fm_freqs, vhf_fm_presets = getpresets(config, 'VHF_FM_RADIO', VHF_FM_NUM_PRESETS, VHF_FM_FREQ_LEN)

# Create data structure to write lua settings file
uhf_lua_dict = {'presets': uhf_freqs, 'dials': uhf_presets}
vhf_am_lua_dict = {'presets': vhf_am_freqs, 'dials': vhf_am_presets}
vhf_fm_lua_dict = {'presets': vhf_fm_freqs, 'dials': vhf_fm_presets}

# Config file parsed, now create new mission.
if verbosity > 0:
    print(f'{sys.argv[0]}: Creating temp directory : {WORKING_DIRNAME}')
os.mkdir(WORKING_DIRNAME)
if verbosity > 0:
    print(f'{sys.argv[0]}: Copying original mission file : {args.input_filename}')
shutil.copy2(args.input_filename, WORKING_DIRNAME)
if verbosity > 0:
    print(f'{sys.argv[0]}: Unpacking mission within temp directory')
shutil.unpack_archive(args.input_filename, WORKING_DIRNAME, 'zip')
if verbosity > 0:
    print(f'{sys.argv[0]}: checking for existing directory structure')
path = os.path.join(WORKING_DIRNAME, 'Avionics')
if os.path.exists(path):
    print(f'WARNING: Mission file appears to already have settings installed.\nExiting')
    shutil.rmtree(WORKING_DIRNAME)
    exit(0)
if verbosity > 0:
    print(f'{sys.argv[0]}: Applying changes to mission structure')

# Create directory structure and write settings file for each radio type

# UHF Radio
if config.has_section('UHF_RADIO'):
    for subdir in uhf_ac_list:
        path = os.path.join(WORKING_DIRNAME, f'Avionics/{ac_type}/{subdir.strip()}/{UHF_DIR_NAME}')
        os.makedirs(path)
        luadata.write(f'{path}/SETTINGS.lua', uhf_lua_dict, encoding="utf-8", indent="\t", prefix="settings= ")

# VHF AM Radio
if config.has_section('VHF_AM_RADIO'):
    for subdir in vhf_am_ac_list:
        path = os.path.join(WORKING_DIRNAME, f'Avionics/{ac_type}/{subdir.strip()}/{VHF_AM_DIR_NAME}')
        os.makedirs(path)
        luadata.write(f'{path}/SETTINGS.lua', vhf_am_lua_dict, encoding="utf-8", indent="\t", prefix="settings= ")

# VHF FM Radio
if config.has_section('VHF_FM_RADIO'):
    for subdir in vhf_fm_ac_list:
        path = os.path.join(WORKING_DIRNAME, f'Avionics/{ac_type}/{subdir.strip()}/{VHF_FM_DIR_NAME}')
        os.makedirs(path)
        luadata.write(f'{path}/SETTINGS.lua', vhf_fm_lua_dict, encoding="utf-8", indent="\t", prefix="settings= ")

# Pack up the modified mission
new_name = args.input_filename.split('.')[0]
if verbosity > 0:
    print(f'{sys.argv[0]}: Compressing updated mission and saving as : {new_name}_mod.miz')
shutil.make_archive(f'{new_name}_mod', 'zip', WORKING_DIRNAME)
shutil.move(f'{new_name}_mod.zip', f'{new_name}_mod.miz')
if verbosity > 0:
    print(f'{sys.argv[0]}: Removing temp directory : {WORKING_DIRNAME}')
shutil.rmtree(WORKING_DIRNAME)
