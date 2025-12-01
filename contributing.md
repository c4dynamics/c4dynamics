# Quickstart for Contributors 🚀

Welcome! Whether it’s your first contribution or you’re an experienced engineer, this guide will help you contribute to **c4dynamics**.

We mainly accept contributions in two areas:

1. **Use Case Notebooks** – Practical examples demonstrating framework usage.
2. **New Features / Feature Modifications** – Extensions or improvements to the framework itself.

---

## 1️⃣ Use Case Notebook

The best way to contribute to c4dynamics is by providing a well-documented use case notebook in the [Use Cases section](https://c4dynamics.github.io/c4dynamics/programs/index.html) of the documentation. 

These notebooks help engineers quickly understand how to apply **c4dynamics** in practice.

### steps: 

1. **Fork the repository** (top-right corner on GitHub).
2. **Set up your environment** (install dependencies, etc.).
3. **Design your model or algorithm simulation.**
4. **Build using state objects** and extend with modules from the scientific library (e.g., sensors, filters, detectors).
5. **Write your program in a Jupyter notebook.**

   * Keep it simple yet functional.
   * Add comments and documentation to explain your approach.
6. **Test thoroughly:** Ensure it runs without errors and produces meaningful results.
7. **Visualize outputs** using **c4dynamics** tools.
8. **Submit your contribution**:

   * Add your notebook to the `Use Cases` section of the documentation.
   * Include any comments, explanations, and docstring examples.

---

## 2️⃣ New Features or Modifying Existing Ones

If you have an idea for a new function or feature:

1. **Open an issue first** to discuss the proposal.
2. Once approved, **work in a separate feature branch**.

### Coding Standards

* **Follow Python conventions** (PEP8-adjacent).
* **Use NumPy-based math:** `np.atleast_1d`, `np.atleast_2d`, standard linear algebra structures.
* **Defensive coding:** Check for `None`, enforce shapes, raise `TypeError` for invalid arguments.

### Commenting & Documentation

* **Docstrings:** Use triple quotes, follow NumPy style, include doctest examples, reference related modules/classes.
* **Inline comments:** Short, clear explanations of tricky code parts.

### Testing

* **Doctests:** Include examples inside docstrings. Run via `doctest.testmod()`.
* **Self-contained testing block:** Wrap in `if __name__ == "__main__":`.
* **Unit tests:** Add tests to the dedicated unittest files.
* **Run tests locally:**

  ```bash
  python tests/run_doctests.py
  python tests/run_unittests.py
  ```

### Submitting Changes

1. Fork the repository (if not already done).
2. Commit your changes with clear messages.
3. Push your feature branch.
4. Open a Pull Request (PR) for review.

---

## ✅ Tips for First-Time Contributors

* Start with a small **use case notebook** to get familiar with the framework.
* Don’t worry about perfection—your contribution will be reviewed and improved collaboratively.
* Read the examples in existing notebooks to see formatting and documentation standards.

