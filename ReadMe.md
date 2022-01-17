# dcsMisConfigure:

## A hack of a utility to add preset conditions to already existing DCS mission files.

Currently ONLY supporting radio presets.

Command: `python dcsMisConfigure.py -c <ac_type>.cfg <mission name>`


The `<ac_type>.cfg` file has the following categories:<m>

**[UHF_RADIO]**

**[VHF_AM_RADIO]**

**[VHF_FM_RADIO]**

within each radio type, optional parameters are:

*acList*

*pre_1*

*pre_2*

...thru... 

*pre_20*

*acList* is a comma separated list of integers specifying which aircraft numbers within the mission that these presets apply to

*pre_<n>* specifies the frequency set within the radios when the player spawns in an aircraft




NOTES:
* This is a hack. A complete fragile mess. It depends on a very specific directory structure that as of today (Jan, 2022) exists within a DCS mission
* In the current mission design, some aircraft appears to allow setting of start-up frequencies with similar results to this code. HOWEVER, those parameters are embedded within the mission lua script and does not unwrap into the directory structure ala this tool.
* When specifying the configuration parameters, the file name of the config file is important as the tool uses that name to create the directory structure (and thus specify the aircraft type). The included example config file shows the naming convention for the A-10C II as is used by DCS.
* I cannot reiterate enough how fragile this thing is. If you aren't comfortable in mucking through python code and checking the mission structure (before and after this tool is run), I would suggest staying the heck away for now.