# ECM1400 Programming Continuous Assessment

- [ ] Configuration File - api keys, user credentials, configuratio ninformation, location update intervals, filepaths for application resources, should be stored in a configuration file, create a `config.json` with all info for updating dashboard settings to run and personalise dashboard
- [ ] Logging - log all events that happen in your smart alarm? and categorise different types of event[s] that may be treated in different ways, suchh as errors if the web services don't respond
- [ ] Testing - Include unit testing for each functions, include a deployment test cycle, scheduling tests to regularly check the functionality of program, some sample tests are provided. Extend these tests and test your code using the `pytest` module
- [ ] Distribution and Documentation - Host code publicly on github. Documentation for user and a developer. User must know how to deploy and use the system, developer must know how the code is structured, what it does and how to extend it.

## TODO
- [ ] Make sure code matches specification, make tests for it?
- [ ] Manual Code testing, try to break each function, think about edge cases
- [ ] Optimisation, "speed test" code
- [ ] Add logging
- [ ] Add comments, docstrings
- [ ] Package

# Install

```bash
    python3 -m venv venv
    . venv/bin/activate
    pip install -e .
    export FLASK_APP=
    flask run
```