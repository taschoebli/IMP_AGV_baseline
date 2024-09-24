# Task-level Collaboration between Automated Guided Vehicles (AGV) for Efficient Warehouse Logistics

## Introduction
This project implements a prototype to explore task-level collaboration between automated guided vehicles (AGVs) within a warehouse environment. The prototype was developed using the DJI Robomaster EP Core robots and is designed to evaluate whether collaborative task sharing and execution can enhance efficiency and reduce delivery times in warehouse operations.
## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the repository**  
   Clone the project from the Git repository using the following command:
   ```
   git clone https://github.com/tobifra/multi-AGV-task-level-collaboration
   ```

2. **Navigate to the project directory**  
   Change into the project directory:
   ```
   cd multi-AGV-task-level-collaboration
   ```

3. **Install Python**  
   Ensure that Python is installed on your machine, with a minimum version of 3.6.6 and a maximum version of 3.8.9. You can check your Python version with:
   ```
   python --version
   ```
   If you need to install Python, download and install the correct version from the [official Python website](https://www.python.org/downloads/).

4. **Install dependencies**  
   Install all required Python packages listed in `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

5. **Navigate to the code directory**  
   Change into the code directory:
   ```
   cd code
   ```

6. **Set up environment variables**  
   Rename the `env.example` file to `.env`:
   ```
   mv env.example .env
   ```

7. **Run the program**  
   Finally, run the program using the following command:
   ```
   python main.py
   ```
