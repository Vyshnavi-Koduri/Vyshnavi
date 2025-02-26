import os
import subprocess
import re
import csv

# Folder containing your RTL files and output CSV filename.
RTL_FOLDER = "/home/sidda/rtl_dataset"
OUTPUT_CSV = "timing_dataset.csv"
def run_command(cmd):
    """Runs a shell command, returning (stdout, stderr)."""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode(errors='replace'), err.decode(errors='replace')

def synthesize_and_map(rtl_file, top_name):
    """
    1) Uses Yosys to read the RTL file, synthesize with top module 'top_name',
       and calls ABC to map to basic gates (without NOT) and write a BLIF file.
    2) Runs ABC to print stats and paths.
    Returns (logic_depth, full ABC output).
    """
    blif_file = f"{top_name}.blif"
    if os.path.exists(blif_file):
        os.remove(blif_file)

    # Yosys script: note we removed NOT from the gate list.
    yosys_script = f"""
      read_verilog {rtl_file};
      synth -top {top_name};
      abc -g AND,OR,XOR;
      write_blif {blif_file};
    """
    yosys_cmd = f"yosys -p \"{yosys_script}\""
    yosys_out, yosys_err = run_command(yosys_cmd)
    if "ERROR:" in yosys_out or "ERROR:" in yosys_err:
        print(f"[Yosys Error] in {rtl_file}:\n{yosys_out}\n{yosys_err}")
        return None, yosys_out + "\n" + yosys_err

    # Run ABC to get logic depth from the BLIF
    abc_cmd = f'abc -c "read_blif {blif_file}; print_stats; print_paths;"'
    abc_out, abc_err = run_command(abc_cmd)
    if "ERROR:" in abc_out or "ERROR:" in abc_err:
        print(f"[ABC Error] in {rtl_file}:\n{abc_out}\n{abc_err}")
        return None, abc_out + "\n" + abc_err

    logic_depth = extract_logic_depth(abc_out)
    return logic_depth, abc_out

def extract_logic_depth(abc_output):
    """
    Parses the ABC output for a line that contains 'longest path' (case insensitive)
    and returns the trailing number as an integer.
    Adjust this function if your ABC output differs.
    """
    for line in abc_output.splitlines():
        if "longest path" in line.lower():
            match = re.search(r"(\d+)$", line)
            if match:
                return int(match.group(1))
    return None

def create_sdc_file(top_name):
    """
    Creates a minimal SDC file for OpenSTA with a 10 ns clock on port 'clk'.
    """
    sdc_filename = f"{top_name}.sdc"
    sdc_content = """\
create_clock -period 10 [get_ports clk]
set_input_delay 0 -clock clk [all_inputs]
set_output_delay 0 -clock clk [all_outputs]
report_timing
"""
    with open(sdc_filename, "w") as f:
        f.write(sdc_content)
    return sdc_filename

def run_sta_and_extract_delay(top_name, sdc_file):
    """
    Runs OpenSTA using the provided SDC file.
    Parses the output for a line containing 'Data Path Delay' to extract the delay.
    Returns (timing_delay, full STA output).
    """
    sta_cmd = f"sta -f {sdc_file}"
    sta_out, sta_err = run_command(sta_cmd)
    if "ERROR:" in sta_out or "ERROR:" in sta_err:
        print(f"[STA Error] in {top_name}:\n{sta_out}\n{sta_err}")
        return None, sta_out + "\n" + sta_err
    timing_delay = extract_timing_delay(sta_out)
    return timing_delay, sta_out

def extract_timing_delay(sta_output):
    """
    Parses OpenSTA output for 'Data Path Delay' and returns the delay as a float.
    Adjust the parsing if your OpenSTA output format is different.
    """
    for line in sta_output.splitlines():
        if "Data Path Delay" in line:
            parts = line.strip().split()
            try:
                return float(parts[-1])
            except ValueError:
                continue
    return None

def process_rtl_file(rtl_file):
    """
    Processes a single RTL file through Yosys, ABC, and OpenSTA.
    Returns a tuple (rtl_file, logic_depth, timing_delay).
    Skips files likely to be non-synthesizable (e.g., testbenches).
    """
    top_name = os.path.splitext(os.path.basename(rtl_file))[0]

    # Skip files that are likely testbenches or non-synthesizable
    if any(substr in top_name.lower() for substr in ["tb", "test", "dummy", "glbl", "blackbox"]):
        print(f"Skipping non-synthesizable file: {rtl_file}")
        return rtl_file, None, None

    logic_depth, abc_log = synthesize_and_map(rtl_file, top_name)
    if logic_depth is None:
        return rtl_file, None, None

    sdc_file = create_sdc_file(top_name)
    timing_delay, sta_log = run_sta_and_extract_delay(top_name, sdc_file)
    return (rtl_file, logic_depth, timing_delay)

def main():
    rtl_files = [
        os.path.join(RTL_FOLDER, f)
        for f in os.listdir(RTL_FOLDER)
        if f.endswith(".v")
    ]

    results = []
    for rtl_file in rtl_files:
        print(f"Processing {rtl_file} ...")
        try:
            result = process_rtl_file(rtl_file)
            results.append(result)
        except Exception as e:
            print(f"Error processing {rtl_file}: {e}")
            results.append((rtl_file, None, None))

    with open(OUTPUT_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["RTL File", "Logic Depth", "Timing Delay"])
        writer.writerows(results)

    print(f"Done! Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
