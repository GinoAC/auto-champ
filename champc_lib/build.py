import os
def build_champsim(env_con):
  
  build_list = env_con.fields["build_list"]

  if build_list == "all":
    for js in os.listdir(env_con.fields["configs_path"]):
      if js[-4:] == "json":
        os.system("./config.sh " + env_con.fields["configs_path"] + js)
        os.system("make")
  else:
    build_file = open(build_list)
    
    if env_con.fields["master_build"] == "1":
      for line in build_file:
        if line[0] != "#":
          target = line.strip().split(" ")
          if len(target) != 7:
            print("Build Error: Requires 7 arguments for build, " + str(len(target)) + " entered for: ")
            print(line)
            exit()
        else:
          continue

        print("Building: " + line)
        os.system("./build_champsim.sh " + line)
 
    else:
      for line in build_file:
        if line[0] != "#":
          target = line.strip()
        else:
          continue
        if target not in os.listdir(env_con.fields["configs_path"]):
          print("Build file: " + target + " not found ")
          exit()
        else:
            print("Building: " + target)
            os.system("./config.sh " + env_con.fields["configs_path"] + target)
            os.system("make")

