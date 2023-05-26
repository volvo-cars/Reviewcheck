# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.6.0] - 2023-05-26

### Added

- Display merge request where the user has left an emoji reaction but not
  upvoted (considered to have started a review but not completed it).
- Introduce Dockerfile and `--no-notifications` flag.

### Changed

- Improve notification message.
- Update lock file, with latest compatible packages.

### Fixed

- Fixed bug where all merge requests in a project were shown, rather than just
  the ones where the user is involved.

### Removed

- Drop support for Python 3.6.

## [0.5.1] - 2022-10-26

## [0.5.0] - 2022-10-14

### Added

- Show desktop notification when there is a new comment.
- Subject line added to desktop notifications.
- Adapt width of output to the terminal width, and allow configuring it. Default
  is to fill the whole terminal.

### Changed

- Make Jira regex case insensitive (when trying to figure out the ticket
  number).

### Fixed

- Ensure that username is made into uppercase, in adaption to GitLab API data.

## [0.4.0] - 2022-06-28

### Added

- Clean shutdown on keyboard interruption.
- Date is shown for comments and merge requests. It's shown next to the comment
  for comments and in the info box for merge requests.

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
  in an merge request that you are a part of, that discussion will be hidden
  rather than just greyed out.

### Fixed

- Bug where the presence of an merge request with no discussions on it would
  cause the app to crash.
- Session is now reset for each time we get new data from GitLab.

## [0.2.0] - 2022-06-02

### Added

- Interactive configuration of tool.
- Tab completion file generation.
- Source branch name is now shown in the info box for each merge request.

### Changed

- Configure what projects to track from configuration file.
- Configure GitLab and JIRA URLs from configuration file.
- Color for merge requests now depend on merge request number, rather than
  being random.
