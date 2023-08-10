# Install Using Conda Environment

## Installing Conda

Conda is an open-source package management system and environment management system that runs on Windows, macOS, and Linux. Here are the steps to install Conda using the Anaconda distribution:

1. Go to the [Anaconda download page](https://www.anaconda.com/products/individual) and download the appropriate version for your operating system.

2. Follow the installation instructions for your operating system. During the installation process, you can choose whether to add Anaconda to your system PATH and whether to make Anaconda your default Python distribution.

3. Once the installation is complete, open a terminal or command prompt and run the following command to verify that Conda is installed:

## Install The Environment

follow the steps below to install the environment, install using option 1 or option 2!

### Option 1: install using terminal commands

Open a terminal or command prompt and run the following command to create a new environment called "c4dynamics_env":

```bash
cd c4dynamics
conda env create -f c4dynamics_env.yaml
```

To run the environment in your terminal, run:
```
conda activate c4dynamics
```

If you work with vscode, go to:
View
Command Pallete
Select Interpreter

From the list that opened, select the python executable from anaconda\c4dynamics

### Option 2: Install using Anaconda Navigator

1. Open Anaconda Navigator.

2. Click on the "Environments" tab on the left-hand side of the window.

3. Click on the "Import" button at the bottom of the window.

4. In the "Import Environment" dialog box, select the "From YAML file" option.

5. Click on the "Browse" button and navigate to the directory of the c4dynamics repository.

6. Select the c4dynamics_env.yaml YAML file and click on the "Open" button.

7. In the "Import Environment" dialog box, specify a name for the environment in the "Name" field.

8. Click on the "Import" button to import the environment.

9. Once the environment has been imported, you can activate it by clicking on the environment name in the "Environments" tab and selecting "Open Terminal" or "Open with Jupyter Notebook" to start working with the environment.

That's it! You have now imported a Conda environment using Anaconda Navigator.


## What are Conda Environments?

Conda is an open-source package management system and environment management system that runs on Windows, macOS, and Linux. Conda environments are isolated environments that contain a specific version of Python and a set of packages and dependencies. Each environment can have its own set of packages and dependencies, which makes it easy to manage different projects with different requirements.

Here are some benefits of using Conda environments:

- **Isolation:** Each environment is isolated from other environments and from the system Python installation. This means that you can have different versions of Python and different packages installed in different environments without conflicts.

- **Reproducibility:** By specifying the packages and dependencies for each environment in a YAML file, you can easily recreate the environment on another machine or share it with others. This makes it easy to reproduce your results and collaborate with others.

- **Flexibility:** Conda environments can be used for any type of project, from data analysis to machine learning to web development. You can easily switch between environments and install new packages and dependencies as needed.

- **Ease of use:** Conda provides a simple and intuitive command-line interface for creating, activating, and managing environments. You can also use Conda with popular IDEs like Visual Studio Code and PyCharm.

Overall, Conda environments are a powerful tool for managing packages and dependencies in Python projects. They provide isolation, reproducibility, flexibility, and ease of use, which makes them a great choice for any type of project.

If you haven't used Conda environments before, we highly recommend giving them a try. They can save you a lot of time and headaches in the long run!



