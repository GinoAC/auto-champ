import os

required_fields = ["build_list", "configs_path", "results_path", "workload_path", "binaries_path", 
                "limit_hours", "ntasks", "account", "workload_list", "warmup", "sim_inst",
                "results_collect_path"]
optional_fields = ["launch_file", "baseline"]

class env_config:
  def __init__(self):
    self.fields = {}
    self.ignore_bin = []
    self.output_path = ""

  def add_ignore_bin(self, bin_str):
    self.ignore_bin.append(bin_str)
 
  def load_env_config(self, config_name):
    if not os.path.exists(config_name):
      print("ERROR: CONTROL CONFIG FILE DOES NOT EXIST\nFile: " + config_name)
      exit()

    config_file = open(config_name, "r")

    for line in config_file:
      if line[0] == "#" or len(line) == 1:
        continue

      sline = line.strip().split("=")

      for a in range(0,len(sline)):
        sline[a] = sline[a].strip(" ")
        sline[a] = sline[a].strip("\n")

      if sline[0] in self.fields.keys():
        print("ERROR: REPEATING CONFIGURATION FIELD: "+ sline[0] +"\n")
        exit()
      
      self.fields[sline[0]] = sline[1]

#Running Asmdb or Anchor
      #elif sline[0] == "asmdb_path":
      #  self.asmdb_path = sline[1]
      #elif sline[0] == "asmdb_MT":
      #  self.asmdb_MT = sline[1]
      #elif sline[0] == "asmdb_FT":
      #  self.asmdb_FT = sline[1]
      #elif sline[0] == "asmdb_window":
      #  self.asmdb_window = sline[1]

  def build_check(self):
    if self.fields["build_list"] == "":
      print("Build Error: No defined build list")
      exit()
    if self.fields["configs_path"] == "":
      print("Build Error: No defined build configurations path")
      exit() 

  def config_check(self, command):
   
    #check required fields 
    failed_check = [] 
    for f in required_fields:
      if f not in self.fields.keys():
        failed_check.append(f)
    if len(failed_check) != 0:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      exit()

    failed_check = []
    #check optional fields 
    for f in optional_fields:
      if f not in self.fields.keys():
        failed_check.append(f)
    if len(failed_check) != 0:
      print("Fields were undefined or failed to load:")
      for fc in failed_check:
        print(fc)
      decision = "" 
      while decision != "y" and decision != "n":
        decision = input("Continue? [y/n] ").lower()
        if decision == "n":
          print("Canceling launch...")
          exit()

    if command == "collect":
      if not os.path.isdir(self.fields["results_collect_path"]):
        print("Stats Collection Error: Results collect path does not exist\nInput: %s" % (self.fields["results_collect_path"])) 
        exit()
      
  def stats_check(self):
    if self.fields["results_collect_path"] == "":
      print("Stats Collection Error: Results collect path not specified")
      exit()
    if "baseline" not in self.fields.keys() or self.fields["baseline"] == "":
      print("Stats Collection Warning: Baseline not specified. Will not generate IPC improvement.")
    
    
  
