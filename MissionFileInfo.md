# Mission file (.miz) structure

### A generic mission file created from within DCS has a structure like this:

I10n/  
../DEFAULT/  
../../dictionary  
../../mapResource  
mission
options  
theatre  
warehouses

### A "fully specified" preset mission structure looks like this:

Avionics/  
../<aircraft_type>/  
../../<aircraft_id_#>/  
../../../CDU/  
../../../../SETTINGS.lua  
../../../DSMS_INTERFACE/  
../../../../SETTINGS.lua  
../../../IFFCC/  
../../../../SETTINGS.lua  
../../../LITENING_INTERFACE/  
../../../../SETTINGS.lua  
../../../MFCD_LEFT/  
../../../../SETTINGS.lua  
../../../MFCD_RIGHT/  
../../../../SETTINGS.lua  
../../../SADL/  
../../../../SETTINGS.lua  
../../../TAD/  
../../../../SETTINGS.lua  
../../../UHF_RADIO/  
../../../../SETTINGS.lua  
../../../VHF_AM_RADIO/  
../../../../SETTINGS.lua  
../../../VHF_FM_RADIO/  
../../../../SETTINGS.lua  

** NOTE ** The names of the directories UNDER the <aircraft_id_#> are dependent on the aircraft type;
the list above comes from the A-10C_2 type with three radios

Each SETTINGS.lua file has specific entries for the settings.  
These are detailed in separate lua files by example (for the A10-C_2).   
