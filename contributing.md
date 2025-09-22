
# Quickstart for Contributors 🚀

The best way to contribute to c4dynamics is by providing a well-documented use case notebook in the [Use Cases section](https://c4dynamics.github.io/C4dynamics/programs/index.html) of the documentation.
These notebooks help other engineers quickly understand how to apply the framework in practice.

--- 
## How to Add a Use Case Notebook

* Fork the repository (top-right corner of the GitHub page)
* Design your model or algorithm simulation
* Build with state objects 
* Extend with modules from the scientific library (e.g. sensors, filters, detectors)
* Write your program in a Jupyter notebook  
    - Keep it simple yet functional
    - Add comments and documentation to explain your approach
    - Test thoroughly: make sure it runs without errors and produces meaningful results
    - Visualize outputs: use c4dynamics tools 

--- 
## New Features and Features Modifications 

If you come up with an idea for a new function or capability, please open an issue first so it can be discussed. Once agreed, you can start working on it in a separate scope. However, any change to the c4dynamics module requires following c4dynamics standards:

* Coding
    - PEP8-adjacent: Follow Python conventions (imports at the top, clear indentation, type hints with Optional)
    - NumPy-based math: Use np.atleast_1d, np.atleast_2d, and standard linear algebra structures
    - Defensive coding: Check for None values, enforce shapes (np.atleast_2d), raise errors (TypeError) for invalid argument combinations

* Commenting 
    - Extensive docstrings (triple quotes inside class and methods):
        + Follow the NumPy docstring standard
        + Include doctest-style code snippets inside the docstrings for demonstration and validation
        + Provide references to related modules/classes (cross-referencing using `:class:` and `:mod:`)
    - Inline comments:
        + Short, pragmatic explanations inside functions 
        + Not verbose, just clarifies tricky implementation details

* Testing 
    - Doctest-first:
        + The examples inside the docstrings use also as test cases, runnable via `doctest.testmod()`
        + Use doctest options like +NUMPY_FORMAT to ignore formatting variations in arrays
    - Self-contained testing block:
        + Wrapped in if `__name__ == "__main__"`:, so tests can be run simply by executing the file.
    - Results are either printed to console (`cprint`) or redirected to a log file.
    - Use `FAIL_FAST` so tests stop at the first failure


Once your changes are ready, submit your version: 

* Fork the repository (top-right corner of the GitHub page)
* Add comments and documentation to explain your approach
* Add docstring examples and tests in the dedicated unittest files
* Test thoroughly: make sure it runs without errors and produces meaningful results
* Run the doctests locally. Run: ```python tests/run_doctests.py``` 
* Run the unit tests locally. Run: ```python tests/run_unittests.py```

