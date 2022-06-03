# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- Bug where the presence of an MR with no discussions on it would cause
  the app to crash.

## [0.2.0] - 2022-06-02

### Added

- Interactive configuration of tool.
- Tab completion file generation.
- Source branch name is now shown in the info box for each MR.

### Changed

- Configure what projects to track from configuration file.
- Configure GitLab and JIRA URLs from configuration file.
- Color for MRs now depend on MR number, rather than being random.
