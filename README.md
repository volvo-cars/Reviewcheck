![reviewcheck logo](reviewcheck-logo-short.png)

# Reviewcheck

Reviewcheck is a tool to stay up to date with your reviews on GitLab. You can
configure it to use any GitLab instance you have access to. The tool checks all
open merge requests in the repos chosen by you, and lets you know if there are
open threads that need your attention.

Reviewcheck is in active development.

## Installation

While the project is still in development, the best way to install it is by
cloning the repository and running `poetry run reviewcheck` from within it. You
will need to have poetry installed. The process looks as follows:

```
pip install poetry
git clone https://github.com/volvo-cars/Reviewcheck
cd reviewcheck
poetry run reviewcheck
```

## Documentation

For now, the only documentation is this README and the `--help` flag of the
program itself. A proper
[Wiki](https://github.com/volvo-cars/Reviewcheck/wiki) is
under construction.

## FAQ [NYI]

See [FAQ (NYI)](docs/faq/faq.md) for more questions.

## Support

For support or other queries, contact project owner [Simon
Bengtsson](mailto:simon.bengtsson.3@volvocars.com) or project maintainer [Pontus
Laos](mailto:pontus.laos@volcoars.com).

## Contributing

See the [contributing guide](CONTRIBUTING.md) for detailed instructions on how to get
started with this project.

## Code of Conduct

This project adheres to the [Code of Conduct](./.github/CODE_OF_CONDUCT.md). By
participating, you are expected to honor this code.

## License

This repository is licensed under [Apache License 2.0](LICENSE) © 2022 Volvo Cars.
