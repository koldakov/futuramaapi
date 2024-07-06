# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2024-07-06

### Fixed

- Don't raise Internal Server Error on Not Found error

## [1.1.1] - 2024-07-06

### Added

- Secret messages are being stored in a secure way
- After first shown secret messages are removed

### Security

- Updated libraries. This addresses the following vulnerability:
  - [CVE-2024-39689](https://nvd.nist.gov/vuln/detail/CVE-2024-39689).

## [1.1.0] - 2024-06-04

### Added

- Secret messages generation that can be shown only once

## [1.0.8] - 2024-05-28

### Added

- Shortened URLs generation. Sign-up and generate shortened URLs like https://futuramaapi.com/AAAAAAA.
For now auto generation available only
- Paginated shortened URLs retrieve
- Link retrieve by link id

### Security

- Improved the code

## [1.0.7] - 2024-05-24

### Fixed

- Callback can cause server errors

## [1.0.6] - 2024-05-18

### Security

- Updated libraries. This addresses the following vulnerability:
  - [CVE-2024-37891](https://nvd.nist.gov/vuln/detail/CVE-2024-37891).

## [1.0.5] - 2024-05-17

### Improved

- Documentation

## [1.0.4] - 2024-05-17

### Added

- Password reset feature

## [1.0.3] - 2024-05-13

### Fixed

- View URL on index page

## [1.0.2] - 2024-05-12

### Fixed

- Project version in documentation

### Improved

- Code base

## [1.0.1] - 2024-05-12

### Added

- Button spacing for mobile
- FuturamaAPI version to header

## [1.0.0] - 2024-05-01

### Added

- API: Character selection by id
- API: Paginated characters selection by gender, status, species, order by, order by direction
- API: Character search by name
- API: Episode selection by id
- API: Paginated episodes selection
- API: Season selection by id
- API: Paginated seasons selection
- API: Callbacks for characters, episodes, seasons
- API: Server Sent Events (SSE) for characters
- API: User registration
- API: User authorization
- API: User activation
- API: User confirmation resend message
- API: User information update
- GraphQL: Character selection by id
- GraphQL: Paginated (Edged) characters selection by gender, status, species, order by, order by direction
- GraphQL: Episode selection by id
- GraphQL: Paginated (Edged) episodes selection
- GraphQL: Season selection by id
- GraphQL: Paginated (Edged) seasons selection

[1.1.2]: https://github.com/koldakov/futuramaapi/releases/tag/1.1.2
[1.1.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.1.1
[1.1.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.1.0
[1.0.8]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.8
[1.0.7]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.7
[1.0.6]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.6
[1.0.5]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.5
[1.0.4]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.4
[1.0.3]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.3
[1.0.2]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.2
[1.0.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.1
[1.0.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.0.0
