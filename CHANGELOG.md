# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2022-06-02

### Added

- Interactive configuration of tool.
- Tab completion file generation.
- Source branch name is now shown in the info box for each MR.
- Flag for hiding discussions you don't need to reply to (`--minimal`).
  That is, if you are the last person to have written in a discussion
  in an MR that you are a part of, that discussion will be hidden rather
  than just greyed out.

### Changed

- Configure what projects to track from configuration file.
- Configure GitLab and JIRA URLs from configuration file.
- Color for MRs now depend on MR number, rather than being random.
