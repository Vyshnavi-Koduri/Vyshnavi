# RTL-Feature-Extraction

### **Introduction of the problem statement**  
Timing analysis is a critical step in the design of any complex IP or SoC, as it ensures that signals meet timing constraints under a given clock frequency. However, traditional timing analysis is performed after synthesis, which is a computationally expensive process. If timing violations are detected post-synthesis, significant design changes may be required, leading to project delays.  

To address this challenge, an AI-based approach can be developed to predict the combinational logic depth of critical signals in behavioral RTL before synthesis. This allows early detection of potential timing violations and enables designers to make informed architectural decisions.  

The goal of this approach is to build an ML model trained on a dataset of RTL implementations, where the combinational depth of signals is extracted from synthesis reports. By leveraging feature engineering techniques and machine learning, the model can predict logic depth based on RTL characteristics without requiring full synthesis, significantly reducing the time required for timing analysis.

### **Why depth is extracted from synthesis reports?**
Synthesis reports are commonly used to extract combinational depth because they provide an accurate representation of the final gate-level netlist, including the logic depth and critical path delays after technology mapping and optimization. However, there are other methods to estimate combinational depth

### **Alternative Methods for Extracting Combinational Depth**  
Instead of relying on synthesis reports, combinational depth can be estimated using:  
1. **Static RTL Analysis** – Parses RTL to build a logic dependency graph and estimates depth by finding the longest path.  
2. **Graph-Based Models** – Constructs a directed acyclic graph (DAG) of logic operations and determines depth using graph traversal techniques.  
3. **EDA Tool Reports (Pre-Synthesis)** – Uses tools like RTL linting and complexity analyzers to extract fan-in, fan-out, and estimated gate delays.  
4. **ML-Based Prediction** – Trains an AI model on RTL-derived features (e.g., number of gates, logic dependencies) to predict depth without synthesis. 

### **Approach of the Problem Statement**  

The problem aims to predict the **combinational logic depth** of signals in RTL before synthesis to identify potential **timing violations** early in the design cycle. The proposed approach follows these key steps:  

Here's a more detailed breakdown of each step in the approach to predicting combinational logic depth:  

### **1. Data Collection**  
- **Objective:** Gather RTL designs and their corresponding combinational logic depth values.  
- **Methods:**
  - Extract RTL from open-source repositories or company design databases.  
  - Identify critical timing signals that are likely to have violations.  
  - Obtain synthesis reports from tools like Synopsys Design Compiler, Cadence Genus, or OpenROAD.  
  - Store extracted data in a structured format (CSV, JSON) for analysis.  
- **Challenges:**  
  - Limited availability of pre-synthesized RTL datasets.  
  - Variability in synthesis results due to tool optimizations.  

### **2. Feature Engineering**  
- **Objective:** Identify and extract features that influence combinational logic depth.  
- **Key Features:**
  - **Fan-In/Fan-Out:** Number of inputs and outputs of a signal.  
  - **Gate Type Contribution:** Presence of AND, OR, NOT, XOR, MUX, etc.  
  - **Logic Levels:** The number of gate levels between the signal and the nearest flip-flop.  
  - **Signal Dependencies:** Complexity of expressions defining the signal.  
  - **Synthesis Optimizations:** Potential reductions in gate count due to optimizations.  
  We are using **features** to solve this problem because they provide a structured representation of RTL circuits that machine learning models can use to predict **combinational logic depth**.  

### **Why Use Features?**
1. **Abstracting Complex RTL Information**  
   - Raw RTL code is difficult for an ML model to process directly.  
   - Extracting features like **fan-in, fan-out, gate count, and mux usage** helps break down circuit complexity into numerical values that ML models can analyze.  

2. **Avoiding Full Synthesis**  
   - Traditional timing analysis requires a **complete synthesis flow**, which is computationally expensive.  
   - By extracting **static features from RTL**, we can estimate timing properties **without running synthesis**.  

3. **Improving Prediction Accuracy**  
   - The **depth of a combinational circuit** depends on various factors like **number of logic gates, dependencies, net length,** etc.  
   - Machine learning models learn patterns from these features to make accurate predictions.  

4. **Generalization Across Different Designs**  
   - Instead of relying on precomputed synthesis results, a feature-based ML model can **generalize** to different RTL designs.  
   - This makes it **scalable** and **efficient** for early-stage design exploration.  

### **Examples of Useful Features**
| Feature Name       | Why It Matters |
|--------------------|---------------|
| **Fan-in**        | Determines how many signals drive a logic gate, affecting depth. |
| **Fan-out**       | High fan-out can increase delay due to capacitive loading. |
| **Gate Count**    | More gates in a path generally lead to higher depth. |
| **Mux Count**     | Multiplexers introduce additional logic levels. |
| **Arithmetic Ops** | Adders and multipliers introduce varying levels of delay. |
| **Net Length**    | Longer interconnects can cause more propagation delay. |
| **Bitwidth**      | Affects data path complexity and logic depth. |

- **Challenges:**  
  - Extracting features statically from RTL without synthesis is difficult.  
  - Need to balance between feature complexity and model performance.  

### **3. Machine Learning Model Selection**  
- **Objective:** Identify an ML model capable of predicting combinational logic depth.  
- **Candidate Models:**
  - **Regression Models (Linear, Polynomial):** For simple depth predictions.  
  - **Decision Trees / Random Forests:** Handle non-linearity in combinational logic.  
  - **Neural Networks:** Can capture complex dependencies but require large datasets.  
  - **Graph Neural Networks (GNNs):** Model logic as a graph for better prediction.  
- **Challenges:**  
  - Selecting a model that balances accuracy and computational cost.  
  - Need for a large, diverse dataset for training.  

### **4. Training and Validation**  
- **Objective:** Train the selected model and evaluate its accuracy.  
- **Steps:**
  - Split dataset into training and testing sets.  
  - Train the model using supervised learning with extracted features.  
  - Use validation techniques (cross-validation, holdout sets) to refine the model.  
  - Compare predicted logic depth with actual values from synthesis.  
- **Challenges:**  
  - Model may overfit to a specific design style.  
  - Training dataset size and quality significantly affect performance.  

### **5. Deployment and Testing**  
- **Objective:** Integrate the trained ML model into an RTL design workflow.  
- **Steps:**
  - Implement the model in a script or tool that can analyze new RTL files.  
  - Run predictions on unseen RTL designs and compare results with synthesis reports.  
  - Provide early warnings for potential timing violations.  
- **Challenges:**  
  - Ensuring model predictions generalize well across different designs.  
  - Maintaining accuracy when applied to new RTL structures.  

### **METHOD - 1** 
- IN this method first, the problem statement is solved in data scraping method.
- This project explores the use of data scraping to predict combinational logic depth in RTL designs for early timing violation detection. Timing analysis is critical in VLSI design, but traditional methods involve a full synthesis flow, which is time-consuming. The goal here was to automate RTL feature extraction and timing prediction using open-source tools like Yosys, ABC, and OpenSTA.

## Code Overview
### 1. **RTL Data Scraping from GitHub**
This script searches GitHub for repositories containing RTL (Verilog/VHDL) files and extracts relevant ones to build a dataset.

#### **How it Works:**
- Uses the **GitHub API** to search for repositories with RTL code while avoiding testbenches and simulations.
- Clones the repositories and scans for Verilog (`.v`), SystemVerilog (`.sv`), or VHDL (`.vhdl/.vhd`) files.
- Filters out non-synthesizable files based on naming patterns (`tb`, `testbench`, `sim`).
- Copies valid RTL files into a local dataset directory (`rtl_dataset`).
- Deletes the temporary cloned repositories after extraction to save storage.

#### **Dependencies:**
- `requests` (for GitHub API calls)
- `gitpython` (for cloning repositories)
- `shutil` and `os` (for file operations)

### 2. **RTL Feature Extraction (Logic Depth & Timing Delay)**
This script analyzes the RTL files using open-source tools to extract key circuit properties.

#### **How it Works:**
- **Yosys:** Synthesizes the RTL design into a gate-level netlist.
- **ABC:** Computes the **longest combinational logic depth** from the netlist.
- **OpenSTA:** Runs static timing analysis (STA) to extract **timing delay** from the design.
- Saves the extracted features (`Logic Depth`, `Timing Delay`) in `timing_dataset.csv`.

#### **Why This is Useful:**
- Automates feature extraction without requiring full ASIC synthesis.
- Provides a dataset for AI/ML models to predict timing violations early.
- Eliminates the need for manual synthesis and analysis.

### 3. **Dataset Generation Pipeline**
This script runs a batch process on all RTL files to generate the final dataset.

#### **How it Works:**
- Iterates through all RTL files in `rtl_dataset`.
- Runs synthesis (`Yosys`), logic depth analysis (`ABC`), and timing analysis (`OpenSTA`).
- Extracts key parameters and stores them in a structured CSV (`timing_dataset.csv`).

#### **Benefits:**
- Enables large-scale data collection without manual intervention.
- Can be used to train ML models for early-stage RTL timing estimation.

### 4. **Complete Automation (Full Pipeline Execution)**
This script combines **data scraping + feature extraction + dataset creation** into a single execution flow.

#### **Workflow:**
1. **Fetch RTL files** from GitHub.
2. **Process each file** to extract logic depth and timing delay.
3. **Store results** in a CSV for model training.

#### **Advantages of this End-to-End Approach:**
- Fully automated dataset creation.
- Scales efficiently to analyze multiple RTL files.
- Saves time compared to manual synthesis runs.

## Disadvantages of Data Scraping Approach
While the data scraping method provides a way to automate dataset collection, it has several limitations:

1. **Inconsistent Data Availability**
   - The availability of RTL repositories with proper design constraints is limited.
   - Extracted designs may not always be suitable for synthesis and timing analysis.

2. **Errors and Dependencies**
   - GitHub API rate limits can restrict the number of repositories fetched.
   - Cloning repositories and extracting files can fail due to repository structures.
   - Dependencies on Yosys, ABC, and OpenSTA introduce installation and compatibility issues.

3. **Limited Generalization**
   - The scraped dataset may not cover diverse design styles.
   - Synthesis optimizations applied by different tools can alter logic depth, making predictions inconsistent.

4. **Processing Overhead**
   - Running synthesis and timing analysis for every RTL file is computationally expensive.
   - Requires significant manual intervention to filter out non-synthesizable or irrelevant designs.

## Suggested Alternative Approach
Instead of relying on scraped RTL files, a more structured dataset can be generated by:
- Using **custom-designed** combinational circuits with controlled variations.
- Extracting **pre-verified** timing reports from industrial designs.
- Implementing **static feature analysis** on RTL without full synthesis.
- Leveraging **graph-based models** to analyze logic dependencies in RTL.

## Conclusion
Data scraping offers an automated way to collect RTL data but suffers from availability issues, processing overhead, and lack of generalization. A structured approach with well-defined datasets is recommended for building an AI model for timing prediction.

### **To overcome the problems of Data scraping, an another approach is introduced**

This script trains a machine learning model to predict the **combinational logic depth** of RTL circuits based on extracted circuit features.

#### **How it Works:**
- Loads a structured dataset (`enhanced_synthetic_dataset_full.csv`) containing RTL circuit properties.
- Uses **Random Forest Regressor**, a powerful ensemble learning algorithm, to map circuit features to logic depth.
- Trains the model on extracted parameters like **Fan-in, Gate Count, Fan-out, Number of Muxes, Arithmetic Operations, Capacitance, Net Length, and Bitwidth**.
- Evaluates model performance using **Mean Absolute Error (MAE)**.

#### **Key Features Used for Prediction:**
| Feature             | Description |
|---------------------|-------------|
| Fan-in             | Number of inputs to a gate |
| Gate Count         | Total number of logic gates in the design |
| Fan-out            | Number of gates driven by a single gate |
| Number of Muxes    | Count of multiplexers in the design |
| Arithmetic Ops     | Number of arithmetic operations (e.g., adders, multipliers) |
| Capacitance (fF)   | Total circuit capacitance in femtofarads |
| Net Length (um)    | Total wire length in micrometers |
| Bitwidth           | Signal width of data paths |

#### **Training and Evaluation Process:**
1. **Splitting the Dataset**  
   - The dataset is divided into **80% training** and **20% testing** using `train_test_split`.
  
2. **Training the Model**  
   - A **Random Forest Regressor** with 200 decision trees (`n_estimators=200`) and max depth of 12 (`max_depth=12`) is trained on the extracted features.

3. **Model Evaluation**  
   - The trained model predicts logic depth on the test set.
   - The **Mean Absolute Error (MAE)** metric is used to measure accuracy.

#### **Example Prediction**
The trained model can estimate the logic depth for a new RTL circuit.  
For a circuit with the following properties:
- **Fan-in:** 4
- **Gate Count:** 500
- **Fan-out:** 10
- **Num Muxes:** 3
- **Arith Ops:** 5
- **Capacitance:** 300 fF
- **Net Length:** 50 µm
- **Bitwidth:** 16

The model predicts a **combinational logic depth** of:

```python
Predicted combinational logic depth for the sample features: <output_value>
```

#### **Benefits of This Approach**
- Eliminates the need for full synthesis by providing a **quick logic depth estimate**.
- Allows early-stage **timing violation detection** in RTL design.
- Can be **integrated into EDA workflows** to optimize circuit performance.  

---
