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

parser = argparse.ArgumentParser(description='Python script to add startup defaults to DCS mission file.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input_filename')
parser.add_argument('-c', '--config', help='Name of configuration file.', default=config_file)
parser.add_argument('-v', '--verbosity', help=f'Verbosity level {V_NONE} (silent) to {V_HIGH} (most verbose).',
                    type=int, default=1)
args = parser.parse_args()

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

ac_type = args.config[:-4]
uhf_freqs = {}
vhf_am_freqs = {}
vhf_fm_freqs = {}

if verbosity > 0:
    print(f'{sys.argv[0]}: Reading mission defaults from: {args.config}')

# Grab UHF frequencies
if config.has_section('UHF_RADIO'):
    if config.has_option('UHF_RADIO', 'acList'):
        uhf_ac_list = config['UHF_RADIO']['acList'].split(',')
    else:
        uhf_ac_list = '1'
    if verbosity > 1:
        print('Found UHF Radio section')
        print(f'acList = {uhf_ac_list}')

    for i in range(0, UHF_NUM_PRESETS+1):
        try:
            uhf_freqs[i] = config['UHF_RADIO'][f'Pre_{i}'].replace('.', '').ljust(UHF_FREQ_LEN, '0')
            if verbosity > 1:
                print(f'Preset [{i}] -> {uhf_freqs[i]}')
        except KeyError:
            if verbosity > 2:
                print(f'Preset [{i}] missing')

# Grab VHF AM frequencies
if config.has_section('VHF_AM_RADIO'):
    if config.has_option('VHF_AM_RADIO', 'acList'):
        vhf_am_ac_list = config['VHF_AM_RADIO']['acList'].split(',')
    else:
        vhf_am_ac_list = '1'
    if verbosity > 1:
        print('Found VHF AM Radio section')
    for i in range(0, VHF_AM_NUM_PRESETS+1):
        try:
            vhf_am_freqs[i] = config['VHF_AM_RADIO'][f'Pre_{i}'].replace('.', '').ljust(VHF_AM_FREQ_LEN, '0')
            if verbosity > 1:
                print(f'Preset [{i}] -> {vhf_am_freqs[i]}')
        except KeyError:
            if verbosity > 2:
                print(f'Preset [{i}] missing')

# Grab VHF FM frequencies
if config.has_section('VHF_FM_RADIO'):
    if config.has_option('VHF_FM_RADIO', 'acList'):
        vhf_fm_ac_list = config['VHF_FM_RADIO']['acList'].split(',')
    else:
        vhf_fm_ac_list = '1'
    if verbosity > 1:
        print('Found VHF FM Radio section')
    for i in range(0, VHF_FM_NUM_PRESETS+1):
        try:
            vhf_fm_freqs[i] = config['VHF_FM_RADIO'][f'Pre_{i}'].replace('.', '').ljust(VHF_FM_FREQ_LEN, '0')
            if verbosity > 1:
                print(f'Preset [{i}] -> {vhf_fm_freqs[i]}')
        except KeyError:
            if verbosity > 2:
                print(f'Preset [{i}] missing')

# Create data structure to write lua settings file
uhf_lua_dict = {'presets': uhf_freqs}
vhf_am_lua_dict = {'presets': vhf_am_freqs}
vhf_fm_lua_dict = {'presets': vhf_fm_freqs}

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
    print(f'Removing temp directory : {WORKING_DIRNAME}')
shutil.rmtree(WORKING_DIRNAME)
