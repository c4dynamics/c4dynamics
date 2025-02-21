# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

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


