import re
import json
from collections import defaultdict


def file_paths(file_path= 'logs_2/postcts.log1'):
    with open(file_path, 'r') as file:
        file_data = file.read()
    return file_data


def parse_log_file():
    file_contents = file_paths()
    
    # Compile regex patterns for improved performance
    regex_pattern_summary = re.compile(
        r'\s+opt_design Final Summary(.*?)Routing Overflow:\s*(.*?)\n', re.DOTALL)
    regex_pattern_setupHold = re.compile(
        r'\|\s+(?:WNS \(ns\):\|\s*(-?\d+\.?\d+)|TNS \(ns\):\|\s*(-?\d+\.?\d+)|Violating Paths:\|\s*(\d+\.?\d+)\s*)')
    pattern_DRV = re.compile(
        r'\|\s+(max_cap|max_tran|max_fanout)\s*\|\s*(\d+\s*\(\d+\))\s*\|\s*(-?\d+\.?\d+)\s*')
    regex_pattern_density = re.compile(r'Density:\s*(\d+\.?\d+)\s*')
    # regex_pattern_routing = re.compile(
    #     r'Routing Overflow:\s*(-?\d+\.?\d+)\%\s*H and (-?\d+\.?\d+)\%\s*V')
    # or
    regex_pattern_routing = re.compile(
        r'(-?\d+\.?\d+)\%\s*H and (-?\d+\.?\d+)\%\s*V')
    regex_pattern_total_power = re.compile(
        r'^(Total Power\s*\n)[-]*\n(Total Internal Power:\s*(.*?)\s*(\d+\.?\d+)%\n)(Total Switching Power:\s*(.*?)\s*(\d+\.?\d+)%\n)(Total Leakage Power:\s*(.*?)\s*(\d+\.?\d+)%\n)', re.MULTILINE)
    regex_pattern_instance_design = re.compile(
        r'Instances in design\s*=\s*(\d+)')
    regex_pattern_vt = re.compile(
        r'(LVT|SVT|HVT) : inst = (\d+) \((\d+\.?\d+)%\)')
    regex_pattern_run_time = re.compile(
        r'totcpu=(.*?),\s*real=(.*?),\s*mem=(.*?)$')

    setUpMode = defaultdict(list)
    holdMode = defaultdict(list)
    DRV = {}
    density = []
    congestion_overflow = {"H": [], "V": []}
    VT_dist = defaultdict(list)
    insts_count = []
    power = {"Dynamic": [], "Leakage": []}
    runTime = []

    summary_match = regex_pattern_summary.findall(file_contents)

    # Finding Total Summary (WNS, TNS, FEP), DRV's, Density, Routing_Overflow
    if summary_match:
        summary_data = summary_match[-1][0]
        # print(summary_data)
        wns_tns_match = re.findall(regex_pattern_setupHold, summary_data)

        if len(wns_tns_match) > 4:
            setUpMode["WNS"].append(wns_tns_match[0][0])
            setUpMode["TNS"].append(wns_tns_match[1][1])
            setUpMode["FEP"].append(wns_tns_match[2][2])
            holdMode["WNS"].append(wns_tns_match[3][0])
            holdMode["TNS"].append(wns_tns_match[4][1])
            holdMode["FEP"].append(wns_tns_match[5][2])
        else:
            setUpMode["WNS"].append(wns_tns_match[0][0])
            setUpMode["TNS"].append(wns_tns_match[1][1])
            setUpMode["FEP"].append(wns_tns_match[2][2])
            holdMode["WNS"].append("-")
            holdMode["TNS"].append("-")
            holdMode["FEP"].append("-")

        matches = re.findall(pattern_DRV, summary_data)
        DRV = {key: {"terms": value, "slack": slack}
               for key, value, slack in matches}

        density_match = re.search(regex_pattern_density, summary_data)
        density_val = density_match.group(1) if density_match else "-"
        density.append(density_val)

        # routing_overflow_match = re.search(regex_pattern_routing, summary_match[-1])
        routing_overflow_match = re.search(
            regex_pattern_routing, summary_match[-1][1])
        routing_overflow_h = routing_overflow_match.group(
            1) if routing_overflow_match else "-"
        routing_overflow_v = routing_overflow_match.group(
            2) if routing_overflow_match else "-"
        congestion_overflow["H"].append(routing_overflow_h)
        congestion_overflow['V'].append(routing_overflow_v)
    else:
        print("Setup value pattern not found")

    # Finding the Total Power (Switching, Leakage)
    total_power_match = regex_pattern_total_power.search(file_contents)
    if total_power_match:
        power['Dynamic'].append(total_power_match.group(6))
        power['Leakage'].append(total_power_match.group(9))
    else:
        print("Pattern not found for Total Power.")

    # Find Instance count
    matches = regex_pattern_instance_design.findall(file_contents)
    if matches:
        instances_in_design = matches[-1].strip()
        insts_count.append(instances_in_design)
    else:
        print("Pattern not found for Instances in Design.")

    # Find LVT, SVT, HVT and %
    matches = regex_pattern_vt.findall(file_contents)
    for design_type, inst_value, percentage in matches[-3:]:
        VT_dist[design_type].append(inst_value)
        VT_dist[f"{design_type} %"].append(percentage)

    # Find Run_Time
    run_time_match = regex_pattern_run_time.search(file_contents)
    if run_time_match:
        runTime.append(run_time_match.group(2))
    else:
        print("Pattern not found for Run Time.")

    return {
        "setUpMode": dict(setUpMode),
        "holdMode": dict(holdMode),
        "DRV": DRV,
        "density": density,
        "congestion_overflow": congestion_overflow,
        "VT_dist": dict(VT_dist),
        "insts_count": insts_count,
        "power": power,
        "runTime": runTime
    }





# parsed_data = parse_log_file()

# output_file_path = 'parsed_data.json'

# # Write the data to the JSON file
# with open(output_file_path, 'w') as json_file:
#     json.dump(parsed_data, json_file, indent=4)



# def main():
#     file_contents = file_paths()
#     try:

#         pattern_text_between = r'\s+flow\.cputime\s+flow.realtime\s+timing\.setup\.tns\s+timing\.setup\.wns\s+snapshot\nUM:\s*\d+\.?\d+\s+\d+\.?\d+\s+report_finish'

#         # Use re.search() to find the pattern in the string
#         match = re.search(pattern_text_between, file_contents, re.DOTALL | re.MULTILINE)

#         if match:
#             print(match)
#         else:
#             print("Pattern not found.")
#     except Exception as e
#         print(e)




# file_path = 'logs_2/postcts.log1'
# main(file_path)

import os

def get_max_numbered_log(logfiles, base_name):
    pattern = re.compile(fr"{base_name}\.log(\d*)")
    number_logs = [file for file in log_files if pattern.fullmatch(file)]
    # print(number_logs)

    if number_logs:
        print(number_logs)

       
    return False

folder_path = 'D:/COE_07/COE-PRO/ZLogParse/logs_1'
log_files = os.listdir(folder_path)


selected_logs = []
base_names_to_check = ['floorplan', 'cts', 'prects', 'postcts']

for base_name in base_names_to_check:
    selected_log = get_max_numbered_log(log_files, base_name)
    # if selected_log:
    #     selected_logs.append(selected_log)

# print(selected_logs)
