# debug-tools
Collection of debug tools for FW/hardware projects.

# Prerequisites
Ensure you have `homebrew` (package manager) and `python3`installed on your local macOS machine. `python3` and `pip` are the main neccesary packages for running this program. 

# Install and Setup
* Clone the repo and `cd` into it.
* We will used python's virtual environments `venv` for managing the installed packages. To create a `venv`, run `python3 -m venv .venv`.
* To activate the `venv`, run `source .venv/bin/activate`. Note that while the `venv` needs to only be created once, it should be always activated when running this program.
* To install the necessary packages, run `make setup`.
* To run the main data collection program, run `make run`. This runs the `automation.py` script. For living graphing, use the following command: `python3 script2.py`.
* To deactivate the `venv` in your current terminal afterwards, run `make deactivate`. The `venv` will have to be activated again next time you wish to run the program.
* To clean and remove your local `venv`, run `make clean`. The `venv` will have to be created again next time you wish to run the program. 
