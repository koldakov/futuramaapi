# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.1] - 2025-07-26

### Fixed

- 500 error on secret message request

## [1.9.0] - 2025-05-21

### Added

- Endpoint to retrieve random character
- Endpoint to retrieve random episode
- Endpoint to retrieve random season

## [1.8.6] - 2025-05-09

### Added

- Total API requests counter to the main page (except GraphQL request)

## [1.8.5] - 2025-04-18

### Improved

- General codebase

### Fixed

- 500 error when character id > 2147483647 provided

## [1.8.4] - 2025-03-26

### Improved

- General codebase
- FuturamaAPI stability

## [1.8.3] - 2025-03-16

### Fixed

- Secret message return URL

### Improved

- General codebase

## [1.8.2] - 2024-03-14

### Improved

- General codebase

## [1.8.1] - 2024-02-01

### Improved

- General codebase

## [1.8.0] - 2024-12-7

### Fixed

- Minor bugs

### Improved

- General codebase

### Added

- Link to GitHub as it's much easier for you to find source code

### Deprecated

- `/api/users/list` endpoint. Instead, it's advised to use `/api/users` endpoint

## [1.7.1] - 2024-11-15

### Fixed

- Minor bugs

## [1.7.0] - 2024-09-24

### Added

- Now we are following your notes to enhance user experience.

## [1.6.1] - 2024-09-14

### Fixed

- Minor bugs

## [1.6.0] - 2024-09-13

### Added

- URL to track site uptime status to the about page

## [1.5.2] - 2024-09-11

### Security

- Updated libraries. This addresses the following vulnerability:
  - [CWE-1395](https://cwe.mitre.org/data/definitions/1395.html).

## [1.5.1] - 2024-09-08

### Fixed

- Minor bugs

## [1.5.0] - 2024-09-06

### Changed

- From now, shortened users links are available only with /s/ prefix in the path.
Example: https://futuramaapi.com/s/qaSon2Q

## [1.4.1] - 2024-09-06

### Fixed

- Minor bugs

## [1.4.0] - 2024-09-04

### Added

- Project description to docs
- Link to go back home

## [1.3.2] - 2024-08-28

### Fixed

- Minor bugs

## [1.3.1] - 2024-07-22

### Improved

- Codebase

### Fixed

- Small bugs

## [1.3.0] - 2024-07-13

### Added

- Retrieve users
- Search users by username

## [1.2.1] - 2024-07-13

### Fixed

- Logout through UI

## [1.2.0] - 2024-07-12

### Added

- Kindly Sign In and Log Out via UI

## [1.1.3] - 2024-07-07

### Fixed

- GraphQL API for Character, Characters, Episode and Season

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

[1.9.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.9.1
[1.9.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.9.0
[1.8.6]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.6
[1.8.5]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.5
[1.8.4]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.4
[1.8.3]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.3
[1.8.2]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.2
[1.8.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.1
[1.8.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.8.0
[1.7.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.7.1
[1.7.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.7.0
[1.6.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.6.1
[1.6.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.6.0
[1.5.2]: https://github.com/koldakov/futuramaapi/releases/tag/1.5.2
[1.5.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.5.1
[1.5.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.5.0
[1.4.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.4.1
[1.4.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.4.0
[1.3.2]: https://github.com/koldakov/futuramaapi/releases/tag/1.3.2
[1.3.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.3.1
[1.3.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.3.0
[1.2.1]: https://github.com/koldakov/futuramaapi/releases/tag/1.2.1
[1.2.0]: https://github.com/koldakov/futuramaapi/releases/tag/1.2.0
[1.1.3]: https://github.com/koldakov/futuramaapi/releases/tag/1.1.3
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
