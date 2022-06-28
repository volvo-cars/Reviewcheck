# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.4.0] - 2022-06-28

### Added

- Clean shutdown on keyboard interruption.
- Date is shown for comments and MRs. It's shown next to the comment for
  comments and in the info box for MRs.

### Changed

- Now actually clear screen between runs (with `--refresh`), and separate
  runs by a header.
- The width of the TUI has been reduced slightly.

### Breaking

- Removed the `--fast` flag because recent performance improvements make it
  superfluous.

## [0.3.1] 2022-06-08

No changes.

## [0.3.0] 2022-06-07

### Added

- `--version` flag added.
- Flag for hiding discussions you don't need to reply to (`--minimal`).
  That is, if you are the last person to have written in a discussion
  in an MR that you are a part of, that discussion will be hidden rather
  than just greyed out.

### Fixed

- Bug where the presence of an MR with no discussions on it would cause
  the app to crash.
- Session is now reset for each time we get new data from GitLab.

## [0.2.0] - 2022-06-02

### Added

- Interactive configuration of tool.
- Tab completion file generation.
- Source branch name is now shown in the info box for each MR.

### Changed

- Configure what projects to track from configuration file.
- Configure GitLab and JIRA URLs from configuration file.
- Color for MRs now depend on MR number, rather than being random.
