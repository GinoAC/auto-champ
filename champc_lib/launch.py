import sys
import os
from datetime import date
import time 
import subprocess


def check_load(env_con):
  username = env_con.fields["username"]
  job_limit = int(env_con.fields["job_limit"])
  procs_running = int(subprocess.check_output("squeue -u " + username + " | wc -l",\
    stderr = subprocess.STDOUT, shell = True)) - 1
  print(time.strftime("%H:%M:%S", time.localtime()) + ": Jobs running " + str(procs_running) + " Limit " + str(job_limit))
  if procs_running < job_limit:
    return False
  else:
    time.sleep(30)
    return True

def create_results_directory(env_con):

  results_path = env_con.fields["results_path"]
  num_cores = env_con.fields["num_cores"]
  if not os.path.isdir(results_path + str(date.today()) + "/" + str(num_cores) + "_cores/1/"):
    print("Creating new directory: " + results_path + str(date.today()) + "/" + str(num_cores) + "_cores/1/")
    os.system("mkdir " + results_path + str(date.today()) + "/")
    os.system("mkdir " + results_path + str(date.today()) + "/" + str(num_cores) + "_cores/")
    os.system("mkdir " + results_path + str(date.today()) + "/" + str(num_cores) + "_cores/1/")
    results_path += str(date.today()) + "/" + str(num_cores) + "_cores/1/"
  else:
    num_dirs = 1
    for f in os.listdir(results_path + str(date.today()) + "/" + str(num_cores) + "_cores/"):
      if os.path.isdir(results_path + str(date.today()) + "/" + str(num_cores) + "_cores/" + f):
        num_dirs += 1
    print("Creating new results directory: " + results_path + str(date.today()) + "/" + str(num_cores) + "_cores/" + str(num_dirs) + "/")
    os.system("mkdir " + results_path + str(date.today()) + "/" + str(num_cores) + "_cores/" + str(num_dirs) + "/")
    results_path += str(date.today()) + "/" + str(num_cores) + "_cores/" + str(num_dirs) + "/"
  return results_path



def sbatch_launch(env_con, launch_str, result_str, output_name): 

  while check_load(env_con):
    continue
  
  launch_file = env_con.fields["launch_file"]
  num_cores = env_con.fields["num_cores"]
  limit_hours = env_con.fields["limit_hours"]
  ntasks = env_con.fields["ntasks"]
  mail = env_con.fields["mail"]
  account = env_con.fields["account"]

  sanity = 0
  
  temp_launch = open(launch_file, "w")
  temp_launch.write("#!/bin/bash\n")
  temp_launch.write("##ENVIRONMENT SETTINGS; CHANGE WITH CAUTION\n")
  temp_launch.write("#SBATCH --get-user-env=L #Replicate login environment\n")

  temp_launch.write("##NECESSARY JOB SPECIFICATIONS\n")
  temp_launch.write("#SBATCH --job-name=" + output_name + "                 # Set the job name to \"JobExample1\"\n")
  temp_launch.write("#SBATCH --time=" + str(limit_hours) + ":00:00                         # Set the wall clock limit to 50h\n")
  temp_launch.write("#SBATCH --ntasks=" + str(ntasks) + "                                  # Request 1 task\n")
  temp_launch.write("#SBATCH --mem=1024M                                         # Request 1GB per node\n")
  temp_launch.write("#SBATCH --output=" + result_str +".%j   #Send stdout/err to \"Example1Out.[jobID]\"\n")

  temp_launch.write("##OPTIONAL JOB SPECIFICATIONS\n")
  temp_launch.write("##SBATCH --mail-type=FAIL              		                \# Send email for failed job events only\n")
  temp_launch.write("##SBATCH --mail-user=" + mail + "	                    # Send all emails to email_address\n")
  temp_launch.write("##SBATCH --account="+ str(account) + "                   # Change once hours are used up\n")
  temp_launch.write("##First Executable Line\n")
  temp_launch.write(launch_str)

  temp_launch.close()
  os.system("sbatch " + launch_file)
  os.system("rm " + launch_file)

def terra_launch(env_con):
  #location of the files describing the binaries and 
  #the workloads being launched

  #open the files
  binary_list_file = open(env_con.fields["binary_list"], "r")
  workloads_list_file = open(env_con.fields["workload_list"], "r")

  #init the structs holding the list of launching items
  binaries = []
  workloads = []
 
  #workload director
  workload_dir = env_con.fields["workload_path"]

  #gather each binary 
  for line in binary_list_file:
    if line[0] != "#":
      binaries.append(line.strip())

  #first entry in the workload file is the 
  first = True
  for line in workloads_list_file:
    workloads.append(line.strip())

  binary_list_file.close()
  workloads_list_file.close()

  print("Binaries launching: ")
  print("Launching workloads: ")
  count = 0

  #This prints the workloads in 4 columns
  for a in workloads:
    count += 1
    print(a, end="\t")
    if count == 4:
      count = 0
      print()
  print()

  print("Launching " + str((len(binaries) * len(workloads))) + " continue? [Y/N]") 
  cont = input().lower()
  if cont != "y":
    print("Exiting job launch...")
    exit()
  print("Launching jobs...")

  binaries_path = env_con.fields["binaries_path"]
  results_path = ""

  if env_con.output_path == "":
    results_path = create_results_directory(env_con)
  else:
    results_path = env_con.output_path

  warmup = env_con.fields["warmup"]
  sim_inst = env_con.fields["sim_inst"]

  results_str = "" 
  launch_str = "{}{} -warmup_instructions {} -simulation_instructions {} -traces {}\n" 
  results_output_s = ""
  trace_str = "" 
  output_name = "" 
  num_launch = 0
 
  print("Job binaries: {}".format(binaries))

  for a in binaries:
    for b in workloads:
      splitload = b.split(" ")

      #supporting multicore by iterating through the workload list
      if(len(splitload) > 1):
        for subwl in splitload:
          #create results file name
          results_output_s += subwl.strip() + "_"
          #trace str needs to include wl directory since it references each trace's location
          trace_str += workload_dir.strip() + subwl.strip() + " "
        results_output_s += "multi"
      else:
        results_output_s = b
        trace_str = workload_dir + b

      output_name = results_output_s + "_" + a
      results_str = results_path + results_output_s + "_" + a
      f_launch_str = launch_str.format(binaries_path, a, str(env_con.fields["warmup"]), str(env_con.fields["sim_inst"]), trace_str)
      print("Launching command: {}".format(f_launch_str))
      sbatch_launch(env_con, f_launch_str, results_str, output_name)
      num_launch += 1
      print("Launching Job " + str(num_launch))

