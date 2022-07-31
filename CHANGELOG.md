# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.2] - 2022-07-31

### Fixed?

- Fix connection string for unix socket.

## [1.2.2] - 2022-07-31

### Fixed?

- Trying to not be an idiot.

## [1.2.1] - 2022-07-31

### Fixed

- Fix bug in which engine with socket was not being returned properly.

## [1.2.0] - 2022-07-24

### Changed

- Changed adapter to allow connecting to a socket.
- Fixed migration bug.

## [1.1.0] - 2022-06-5

### Changed

- Changed adapter to get a prefix name.
- Changed migrations to get a table prefix name.

## [1.0.1] - 2022-05-22

### Fix

- Adding missing cast in id field that was breaking the delete method.

## [1.0.0] - 2022-04-24

### Added

- Initial version of database adapter for postgres database.