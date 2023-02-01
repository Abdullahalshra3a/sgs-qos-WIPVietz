# Installation Instructions
## Python part
### 1. Minizinc installation (only if the CSP should be calculated on the fly (default))
- Install Minzinc according to their [tutorial](https://www.minizinc.org/).
- [Under Windows]: Add Minizinc to the "Path" Environment variable.
### 2. Environment setup (using Anaconda)
All the dependencies are written inside in [environment.yml](environment.yml).
Use this command to create a new conda environment with all the dependencies:
```commandline
conda env create --file environment.yml
```

## Java part (Network calculus)
For the compilation, a JDK 16 (tested with OpenJDK 16) is required.  
Currently, the java part is developed under IntelliJ (2022.2).  
The main file to be compiled is [NCEntryPoint.java](java/NCEntryPoint.java).
You can find the pre-compiled libs needed for compilation in the [libs_compiled folder](java/libs_compiled).


# How to Run
## 1. Start the java part
Either run the java project in IntelliJ directly, or compile a JAR file and execute it in the shell with:
````commandline
java -jar <<JAR_NAME>>
````
Important: The java part has to run _**before**_ the Python part.

## 2. Run a scenario
The current "standard" scenario is [FauScenario.py](CSP/scenarios/FauScenario.py).
Run the file and you will see results in both the python and the java output.