
import sys
import os
from datetime import date
import time 
import subprocess
import champc_lib.config_env as conf
import champc_lib.build as build
import champc_lib.asmdb_launch as asmdb_launch
import champc_lib.launch as launcher
import champc_lib.collector as collect

commands = ["build","launch","collect"]

#input 1 is the command
#[build] [launch] [collect]

if len(sys.argv) < 3:
  print("Error: Command must include control configuration file")
  exit()

command = sys.argv[1].lower()
if command not in commands:
  print("Invalid Command: " + command)
  exit()

env_con = conf.env_config()
env_con.load_env_config(sys.argv[2])
env_con.config_check(command)

#for build, include the name of the json file
if command == "build":
  build.build_champsim(env_con)
  
elif command == "launch": 

  if len(sys.argv) > 3:
    if sys.argv[3] == "-asmdb":
      asmdb_launch.asmdb_check(env_con)
      a_params = asmdb_launch.asmdb_params()
      asmdb_launch.launch(env_con)
  else:
    launcher.terra_launch(env_con)

elif command == "collect":
  collect.collect_and_write(env_con)
  print("Complete")
