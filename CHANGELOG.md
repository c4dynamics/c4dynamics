# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

### Breaking
- Fix: Core `State` object assignment behavior corrected — assigning a vector
	with a mismatched `dtype` to a `State` field now updates the underlying
	backing array reliably instead of silently failing to modify internal memory.
	- Impact: Code that relied on implicit (and previously unreliable) assignments
		may now see the array updated as expected or receive a clear `TypeWarning`
		when incompatible types are provided.
	- Migration: Ensure assigned arrays match the state's dtype or use the
		provided setter helper. Example migration patterns:
		```py
	
		# Problematic (old behavior may have silently failed)
		s = c4d.state(x = 0, y = 0, z = 0)
		state.X = np.array([1, 2, 3], dtype = np.float64) 

		# Recommended (explicit dtype match)
		s = c4d.state(x = 0., y = 0., z = 0.) 	# initialize explicitly as float
		state.X = np.asarray([1, 2, 3], dtype=state.X.dtype)

		```
	- Rationale: Prevents silent state corruption and makes assignment
		semantics deterministic across NumPy versions and platforms.


## [2.0.0] - 2024-11-11
### Added
- Complete state space objects mechanism.
- Seeker and radar measurements modules.
- Kalman filter and Extended Kalman filter implementations.
- YOLOv3 object detection API.
- Functionality to fetch datasets for running examples.
- Comprehensive documentation updates.

## [1.2.0] - 2024-03-05
### Added
- `animate` function to visualize rigid body Euler angles with a model.
- Utilities: `cprint`, `gen_gif`, `plottools`, and `tictoc`.

## [1.1.0] - 2024-02-17
### Added
- New class: `fdataframe` for frame's datapoints, inheriting from `datapoint`.
- Documentation for the respective modifications.

### Changed
- Converted `norms` from a function to a property.
- Updated class architecture to include `__slots__` to limit new variable declarations.

### Fixed
- Bug in `cprint()` function.

## [1.0.0] - 2023-07-19
### Added
- Initial release of C4dynamics framework.
- Core functionalities for dynamic systems algorithm development.
- Modules for state space representations, sensors, detectors, and filters.
- Example programs and basic documentation.


