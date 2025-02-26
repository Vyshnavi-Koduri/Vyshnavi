import os
import subprocess
import pandas as pd

def run_command(cmd):
    """Executes shell commands and returns output."""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode(), error.decode()

def process_rtl(file_path):
    """Runs EDA tools on an RTL file and extracts features."""
    rtl_name = os.path.basename(file_path).split('.')[0]

    # Yosys: Convert RTL to Gate-Level Netlist
    yosys_cmd = f"yosys -p 'read_verilog {file_path}; synth -top {rtl_name}; write_blif {rtl_name}.blif;'"
    run_command(yosys_cmd)

    # ABC: Extract logic depth
    abc_cmd = f"abc -c 'read_blif {rtl_name}.blif; print_stats; print_paths;'"
    abc_output, _ = run_command(abc_cmd)
    
    # OpenSTA: Extract timing
    sta_cmd = f"sta -f {rtl_name}.sdc"
    sta_output, _ = run_command(sta_cmd)

    # Extract key values
    logic_depth = extract_logic_depth(abc_output)
    timing_delay = extract_timing_delay(sta_output)

    return {"RTL File": file_path, "Logic Depth": logic_depth, "Timing Delay": timing_delay}

def extract_logic_depth(abc_output):
    """Parses logic depth from ABC output."""
    for line in abc_output.split("\n"):
        if "Longest Path" in line:
            return int(line.split()[-1])
    return None

def extract_timing_delay(sta_output):
    """Parses timing delay from OpenSTA output."""
    for line in sta_output.split("\n"):
        if "Data Path Delay" in line:
            return float(line.split()[-1])
    return None

# Set RTL folder path
rtl_folder = "/home/sidda/rtl_dataset"
rtl_files = [os.path.join(rtl_folder, f) for f in os.listdir(rtl_folder) if f.endswith(".v")]

# Process all RTL files
dataset = [process_rtl(file) for file in rtl_files]

# Save dataset as CSV
df = pd.DataFrame(dataset)
df.to_csv("timing_dataset.csv", index=False)

print("Dataset saved as timing_dataset.csv")
