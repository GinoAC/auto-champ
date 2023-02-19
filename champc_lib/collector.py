import os
from datetime import date

#stats value class
class stats:
    def __init__(self):
        self.environ = ""
        self.instructions = {}

        self.l1i_mpki = {}
        self.l1i_accesses = {}
        self.l1i_misses = {}
        self.l2c_load_accesses = {}
        self.l2c_load_misses = {}
        self.l2c_mpki = {}
        self.llc_load_accesses = {}
        self.llc_load_misses = {}
        self.llc_mpki = {}

        self.l1i_pf_issued = {}
        self.l1i_pf_requested = {}
        self.l1i_pf_filled = {}
        self.l1i_pq_full = {}

        self.l1i_pf_access= {}
        self.l1i_pf_hit = {}
        self.l1i_pf_miss = {}
        self.l1i_pf_useful = {}
        self.l1i_pf_useless = {}
        self.l1i_pf_perc_useful = {}
        self.l1i_pf_perc_useless = {}

        self.hit_pf_mshr = {}
        self.pf_hit_mshr = {}
        self.l1i_pq_hit = {}

        self.ipc = {} # [workload] : [ipc] pairs
        self.over_bl_ipc = {} # [workload] : [ipc] pairs
        self.geomean_ipc = 1.0

def get_stats(stat_dir):

  #stats dictionary for { BINARY : [Workload Stats] }
  bin_stats = {}

  count = 0
  num_files = len(os.listdir(stat_dir)) 
  for fil in os.listdir(stat_dir): 
    count += 1
    print("\r%.2f percent of files loaded" % (100 * float(count)/float(num_files)), end="")

    split_name = fil.split(".")
    wl_name = split_name[0]
    if "champsimtrace" not in split_name:
      binary = split_name[2][3:]
    else:
      binary = split_name[-2][3:]

    try:
      f = open(stat_dir + fil, "r")
    except IOError:
      print("Collect Error: Could not open file -- " + stat_dir+fil)
      exit()
    
    l1i_mshr_scrape = 0

    for line in f:
      s = line.strip()
      check_f = s.split("_")
      if len(check_f) > 1 and check_f[0][0:3] == "cpu":
        s = check_f[1]
      s = s.split(" ")
      c = []
      for a in s:
        if a != '':
          c.extend([a])
      
      if len(c) < 2:
        continue
      
      if binary not in bin_stats.keys():
        bin_stats[binary] = stats() 
      if c[0] == "Simulation" and c[1] == "Instructions:":
        bin_stats[binary].instructions[wl_name] = c[2]
      elif c[0] == "L1I" and c[1] == "LOAD":
        bin_stats[binary].l1i_mpki[wl_name] = (float(c[7])/(float(bin_stats[binary].instructions[wl_name])/1000.0))
        bin_stats[binary].l1i_accesses[wl_name] = float(c[3])
        bin_stats[binary].l1i_misses[wl_name] = float(c[7])
      elif c[0] == "L1I" and c[1] == "PREFETCH" and c[2] == "ACCESS:":
        bin_stats[binary].l1i_pf_access[wl_name] = float(c[3])
        bin_stats[binary].l1i_pf_hit[wl_name] = float(c[5])
        bin_stats[binary].l1i_pf_miss[wl_name] = float(c[7])
      elif c[0] == "L1I" and c[1] == "PREFETCH" and c[2] == "REQUESTED:":
        bin_stats[binary].l1i_pf_requested[wl_name] = float(c[3])
        bin_stats[binary].l1i_pf_issued[wl_name] = float(c[5])
        bin_stats[binary].l1i_pf_useful[wl_name] = float(c[7])
        bin_stats[binary].l1i_pf_useless[wl_name] = float(c[9])
        #bin_stats[binary].l1i_pf_filled[wl_name] = float(c[11])

        if float(bin_stats[binary].l1i_pf_issued[wl_name]) != 0.0:
          bin_stats[binary].l1i_pf_perc_useful[wl_name] = float(c[7])/bin_stats[binary].l1i_pf_miss[wl_name]
          bin_stats[binary].l1i_pf_perc_useless[wl_name] = float(c[9])/bin_stats[binary].l1i_pf_miss[wl_name]
        else:
          bin_stats[binary].l1i_pf_perc_useful[wl_name] = 0.0
          bin_stats[binary].l1i_pf_perc_useless[wl_name] = 0.0

      elif c[0] == "L2C" and c[1] == "LOAD":
        bin_stats[binary].l2c_mpki[wl_name] = (float(c[7]))/(float(bin_stats[binary].instructions[wl_name])/1000.0)
        bin_stats[binary].l2c_load_accesses[wl_name] = float(c[3])
        bin_stats[binary].l2c_load_misses[wl_name] = float(c[7])
        
      elif c[0] == "LLC" and c[1] == "LOAD":
        bin_stats[binary].llc_mpki[wl_name] = (float(c[7])/(float(bin_stats[binary].instructions[wl_name])/1000.0))
        bin_stats[binary].llc_load_accesses[wl_name] = float(c[3])
        bin_stats[binary].llc_load_misses[wl_name] = float(c[7])
        break
      elif c[0] == "CPU" and c[2] == "cumulative":
        bin_stats[binary].ipc[wl_name] = float(c[4])
        #print(bin_stats[binary].ipc[wl_name])
      elif c[0] == "HIT" and c[2] == "PF" and l1i_mshr_scrape < 2:
        #bin_stats[binary].hit_pf_mshr[wl_name] = int(c[4])
        #bin_stats[binary].pf_hit_mshr[wl_name] = int(c[9])
        #bin_stats[binary].l1i_pq_hit[wl_name] = int(c[13])
        #bin_stats[binary].l1i_pq_full[wl_name] = int(c[16])
        l1i_mshr_scrape += 1 
    #check what was not available in the file and set its value to zero
    #TODO: BETTER SOLUTION
    if wl_name not in bin_stats[binary].instructions.keys():
      bin_stats[binary].instructions[wl_name] = 0
    if wl_name not in bin_stats[binary].l1i_pf_issued.keys():
      bin_stats[binary].l1i_pf_issued[wl_name] = 0
      bin_stats[binary].l1i_pf_useful[wl_name] = 0
      bin_stats[binary].l1i_pf_useless[wl_name] = 0
      bin_stats[binary].l1i_pf_perc_useful[wl_name] = 0.0
      bin_stats[binary].l1i_pf_perc_useless[wl_name] = 0.0
    if wl_name not in bin_stats[binary].l1i_mpki.keys():
      bin_stats[binary].l1i_mpki[wl_name] = 0 
    if wl_name not in bin_stats[binary].l2c_mpki.keys():
      bin_stats[binary].l2c_mpki[wl_name] = 0 
    if wl_name not in bin_stats[binary].llc_mpki.keys():
      bin_stats[binary].llc_mpki[wl_name] = 0 
    if wl_name not in bin_stats[binary].ipc.keys():
      bin_stats[binary].ipc[wl_name] = 0.0 
    if wl_name not in bin_stats[binary].hit_pf_mshr.keys():
      bin_stats[binary].hit_pf_mshr[wl_name] = 0
    if wl_name not in bin_stats[binary].pf_hit_mshr.keys():
      bin_stats[binary].pf_hit_mshr[wl_name] = 0
 

 
    f.close()
  print("")
  return bin_stats 

def collect_and_write(env_con):
  workload_keys = []

  bin_stats = get_stats(env_con.fields["results_collect_path"]) 
  if "baseline" in env_con.fields.keys():
    baseline = env_con.fields["baseline"]
  else:
    baseline = ""

  if baseline != "" and baseline not in bin_stats.keys():
    print("Stats Collection Error: Baseline [%s] not present in results directory" % (baseline))
    exit()

  #creates a csv file based on the date
  #and the number of same-dated files
  csv_name = str(date.today()) + ".csv"
  tag = 0
  while os.path.exists(csv_name):
    tag += 1
    csv_name = str(date.today()) + "_" + str(tag) + ".csv"
  csv_file = open(csv_name, "w")

  #no baseline specified, need to get a complete list of workloads
  if baseline == "":
    max_wl = 0
    max_bin = ""
    for binary in bin_stats.keys():
      if len(bin_stats[binary].ipc.keys()) > max_wl:
        max_wl = len(bin_stats[binary].ipc.keys())
        max_bin = binary
    for wl in bin_stats[binary].ipc.keys():
      workload_keys.append(wl)
    workload_keys = sorted(workload_keys)
  else:
    #sort the workloads alphabetically
    for wl in bin_stats[baseline].ipc.keys():
      workload_keys.append(wl)
    workload_keys = sorted(workload_keys)
    
  for binary in bin_stats.keys():
    if binary == baseline:
      continue

    #no baseline specified, overbl is 0
    #for each of the workloads in each binary,
    #get the performance speedup over baseline 
    #and calculate the geomean IPC
    for wl in workload_keys:

      if baseline == "":
        bin_stats[binary].over_bl_ipc[wl] = 0.0
      else:
        if wl in bin_stats[binary].ipc.keys():
          bin_stats[binary].over_bl_ipc[wl] = float(bin_stats[binary].ipc[wl])/float(bin_stats[baseline].ipc[wl])
        else:
          bin_stats[binary].over_bl_ipc[wl] = 0.0
          bin_stats[binary].ipc[wl] = 0.0
      if float(bin_stats[binary].over_bl_ipc[wl] != 0.0):
        bin_stats[binary].geomean_ipc *= float(bin_stats[binary].over_bl_ipc[wl])

  for binary in bin_stats.keys():
    if len(bin_stats[binary].over_bl_ipc.keys()) != 0:
      bin_stats[binary].geomean_ipc =  float(bin_stats[binary].geomean_ipc ** (1.0/len(bin_stats[binary].over_bl_ipc.keys())))
    else:
      bin_stats[binary].geomean_ipc = 0.0

  #write header first
  csv_file.write("Binary, Trace, L1I_accesses, L1I_misses, L1I_MPKI, L1I_pf_requested, L1I_pq_full, L1I_pf_issued, L1I_pf_filled, L1I_pq_hit, " +\
   "L1I_hit_on_pf_mshr, L1I_pf_hit_on_mshr, L1I_pf_access, L1I_pf_hit, L1I_pf_miss, L1I_pf_useful, L1I_pf_useless, L1I_pf_perc_useful,"+\
  "L1I_pf_perc_useless, L2C_accesses, L2C_misses, L2C_MPKI, LLC_accesses, LLC_misses, LLC_MPKI, IPC, IPC_over_baseline\n")

  #write the baseline first for reference
  if baseline != "":
    for wl in workload_keys:
      if wl in bin_stats[baseline].ipc.keys():
        csv_file.write("%s , %s, %s, %s, %s, %s, %s, %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s, %s\n" % \
        (baseline, wl, 
        str(bin_stats[baseline].l1i_accesses[wl]), str(bin_stats[baseline].l1i_misses[wl]), str(bin_stats[baseline].l1i_mpki[wl]), 
        str(bin_stats[baseline].l1i_pf_requested[wl]), "0",#str(bin_stats[baseline].l1i_pq_full[wl]),
        str(bin_stats[baseline].l1i_pf_issued[wl]), "0", #str(bin_stats[baseline].l1i_pf_filled[wl]), 
        "0", #str(bin_stats[baseline].l1i_pq_hit[wl]),
        "0","0",#str(bin_stats[baseline].hit_pf_mshr[wl]), str(bin_stats[baseline].pf_hit_mshr[wl]),
        str(bin_stats[baseline].l1i_pf_access[wl]), str(bin_stats[baseline].l1i_pf_hit[wl]), str(bin_stats[baseline].l1i_pf_miss[wl]), 
        str(bin_stats[baseline].l1i_pf_useful[wl]), str(bin_stats[baseline].l1i_pf_useless[wl]),
        str(bin_stats[baseline].l1i_pf_perc_useful[wl]), str(bin_stats[baseline].l1i_pf_perc_useless[wl]),
        str(bin_stats[baseline].l2c_load_accesses[wl]), str(bin_stats[baseline].l2c_load_misses[wl]), str(bin_stats[baseline].l2c_mpki[wl]), 
        str(bin_stats[baseline].llc_load_accesses[wl]), str(bin_stats[baseline].llc_load_misses[wl]), str(bin_stats[baseline].llc_mpki[wl]),
        str(bin_stats[baseline].ipc[wl]), str(0)))

  #for each binary, write its stats per workload 
  for binary in sorted(bin_stats.keys()):
    if binary == baseline:
      continue
    for wl in workload_keys:
      if wl in bin_stats[binary].ipc.keys() and bin_stats[binary].ipc[wl] != 0.0:
        csv_file.write("%s , %s, %s, %s, %s, %s, %s, %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s , %s, %s\n" % \
        (binary, wl, 
        str(bin_stats[binary].l1i_accesses[wl]), 
        str(bin_stats[binary].l1i_misses[wl]), 
        str(bin_stats[binary].l1i_mpki[wl]), 
        str(bin_stats[binary].l1i_pf_requested[wl]), "0",# str(bin_stats[binary].l1i_pq_full[wl]),
        str(bin_stats[binary].l1i_pf_issued[wl]), "0",#str(bin_stats[binary].l1i_pf_filled[wl]), 
        "0", #str(bin_stats[binary].l1i_pq_hit[wl]),
        "0","0",#str(bin_stats[binary].hit_pf_mshr[wl]), str(bin_stats[binary].pf_hit_mshr[wl]),
        str(bin_stats[binary].l1i_pf_access[wl]), str(bin_stats[binary].l1i_pf_hit[wl]), str(bin_stats[binary].l1i_pf_miss[wl]), 
        str(bin_stats[binary].l1i_pf_useful[wl]), str(bin_stats[binary].l1i_pf_useless[wl]),
        str(bin_stats[binary].l1i_pf_perc_useful[wl]), str(bin_stats[binary].l1i_pf_perc_useless[wl]),
        str(bin_stats[binary].l2c_load_accesses[wl]), str(bin_stats[binary].l2c_load_misses[wl]), str(bin_stats[binary].l2c_mpki[wl]), 
        str(bin_stats[binary].llc_load_accesses[wl]), str(bin_stats[binary].llc_load_misses[wl]), str(bin_stats[binary].llc_mpki[wl]),
        str(bin_stats[binary].ipc[wl]), str(0)))
      else:
        csv_file.write("%s , %s , %d , %d , %d , %d , %d , %d , %d , %d , %d , %d\n" % \
        (binary, wl, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
  print("Writing results to " + csv_name)

