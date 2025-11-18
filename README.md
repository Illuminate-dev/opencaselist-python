# opencaselist-python
![Pypi version widget for this project](https://img.shields.io/pypi/v/opencaselist)

A Python client library for the [OpenCaselist.com](https://opencaselist.com) API, providing easy access to debate case disclosure information.

## Overview

OpenCaselist is a platform for debate case disclosure, allowing debaters to share their cases, rounds, and evidence. This Python client provides a fluent, intuitive interface to interact with the OpenCaselist API programmatically.

## Features

- **Fluent API Design**: Chain methods naturally to navigate the caselist hierarchy
- **Type-Safe Models**: Pydantic models ensure data validation and type safety
- **Comprehensive Coverage**: Access caselists, schools, teams, rounds, and cites
- **Authentication Support**: Secure login with username/password or environment variables
- **Error Handling**: Custom exceptions for clear error reporting

## Installation

```bash
pip install opencaselist
```

## Quick Start

```python
from opencaselist import OpenCaselistClient

# Initialize client (will prompt for credentials)
client = OpenCaselistClient()

# Or provide credentials directly
client = OpenCaselistClient(username="your_username", password="your_password")

# Or use environment variables
# Set OPENCASELIST_USER and OPENCASELIST_PASSWORD
client = OpenCaselistClient()
```

## Usage Examples

### Browse Caselists

```python
# Get all available caselists
caselists = client.caselists()
for caselist in caselists:
    print(f"{caselist.name} ({caselist.slug})")

# Get a specific caselist
caselist = client.caselist("hspolicy25").get()
print(f"{caselist.name} - {caselist.year}")
```

### Access Schools and Teams

```python
# Get all schools in a caselist
schools = client.caselist("hspolicy25").schools()

# Get teams from a specific school
teams = client.caselist("hspolicy25").school("NorthHollywood").teams()

# Get a specific team's details
team = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").get()
print(f"Team: {team.display_name}")
print(f"Debaters: {team.debater1_first} {team.debater1_last}")
```

### View Rounds

```python
# Get all rounds for a team
rounds = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").rounds()

# Filter by side (Affirmative or Negative)
aff_rounds = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").rounds(side="A")
neg_rounds = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").rounds(side="N")

# Get a specific round
round_obj = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").round("round_id").get()
print(f"{round_obj.tournament} - {round_obj.opponent}")
```

### Manage Cites

```python
# Get all cites for a team
cites = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").cites()

# View cite details
for cite in cites:
    print(f"{cite.title}: {cite.cites}")
```

### Create and Update Data

```python
# Create a new team
new_team = client.caselist("hspolicy25").school("NorthHollywood").create_team(
    name="AB",
    debater1_first="Alice",
    debater1_last="Baker",
    debater2_first="Bob",
    debater2_last="Anderson"
)

# Create a round
new_round = client.caselist("hspolicy25").school("NorthHollywood").team("AB").create_round(
    tournament="Tournament of Champions",
    side="A",
    opponent="Westminster KN",
    judge="John Smith",
    round="Semifinals"
)

# Update a round
updated_round = client.caselist("hspolicy25").school("NorthHollywood").team("AB").round("round_id").update(
    report="We read the climate change advantage..."
)

# Create a cite
new_cite = client.caselist("hspolicy25").school("NorthHollywood").team("AB").create_cite(
    title="Climate Advantage",
    cites="1AC - Climate warming leads to extinction\n2AC - Plan solves warming"
)
```

### Delete Resources

```python
# Delete a round
client.caselist("hspolicy25").school("NorthHollywood").team("AB").round("round_id").delete()

# Delete a cite
client.caselist("hspolicy25").school("NorthHollywood").team("AB").cite("cite_id").delete()

# Delete a team
client.caselist("hspolicy25").school("NorthHollywood").team("AB").delete()
```

### Search and Downloads

```python
# Search across caselists
results = client.search("climate change", caselist="hspolicy25")

# Get recent modifications
recent = client.caselist("hspolicy25").recent()

# Get bulk downloads
downloads = client.caselist("hspolicy25").downloads()

# Get team history
history = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").history()
```

## API Structure

The client follows OpenCaselist's hierarchical structure:

```
Client
├── caselists()                          # List all caselists
├── search(query)                        # Search functionality
└── caselist(slug)
    ├── get()                            # Get caselist details
    ├── schools()                        # List schools
    ├── recent()                         # Recent modifications
    ├── downloads()                      # Bulk downloads
    └── school(name)
        ├── get()                        # Get school details
        ├── teams()                      # List teams
        ├── create_team(**kwargs)        # Create team
        └── team(name)
            ├── get()                    # Get team details
            ├── patch(**kwargs)          # Update team
            ├── delete()                 # Delete team
            ├── rounds(side=None)        # List rounds
            ├── create_round(**kwargs)   # Create round
            ├── cites()                  # List cites
            ├── create_cite(**kwargs)    # Create cite
            ├── history()                # Team history
            └── round(id)
                ├── get()                # Get round details
                ├── update(**kwargs)     # Update round
                └── delete()             # Delete round
```

## Models

The library includes Pydantic models for type safety:

- **Caselist**: Represents a debate caselist (e.g., hspolicy25, hsld24)
- **School**: Represents a school with teams
- **Team**: Represents a debate team with debaters
- **Round**: Represents a debate round with tournament info
- **Cite**: Represents evidence citations

## Authentication

The client supports multiple authentication methods:

1. **Interactive prompts** (default):

   ```python
   client = OpenCaselistClient()  # Will prompt for username/password
   ```

2. **Direct credentials**:

   ```python
   client = OpenCaselistClient(username="user", password="pass")
   ```

3. **Environment variables**:

   ```bash
   export OPENCASELIST_USER="your_username"
   export OPENCASELIST_PASSWORD="your_password"
   ```

   ```python
   client = OpenCaselistClient()
   ```

4. **Manual login**:
   ```python
   client = OpenCaselistClient(auto_login=False)
   client.login(username="user", password="pass")
   ```

## Error Handling

The library provides custom exceptions for better error handling:

```python
from opencaselist.exceptions import (
    OpenCaselistError,      # Base exception
    AuthenticationError,    # Authentication failures
    NotFoundError,          # Resource not found (404)
    ValidationError,        # Request validation errors
    APIError               # General API errors
)

try:
    team = client.caselist("hspolicy25").school("NorthHollywood").team("BeLu").get()
except NotFoundError:
    print("Team not found")
except AuthenticationError:
    print("Invalid credentials")
except APIError as e:
    print(f"API error: {e}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/illuminate-dev/opencaselist-python.git
cd opencaselist-python

# Install dependencies
pip install -e ".[dev]"
```

### Project Structure

```
opencaselist-python/
├── src/opencaselist/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Main client and resources
│   ├── models.py            # Pydantic models
│   └── exceptions.py        # Custom exceptions
├── pyproject.toml           # Project configuration
├── README.md               # This file
└── LICENSE.txt             # MIT License
```

## Requirements

- Python 3.13+
- pydantic >= 2.12.4
- requests >= 2.32.5

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Links

- **OpenCaselist Website**: https://opencaselist.com
- **API Documentation**: https://api.opencaselist.com
- **Repository**: https://github.com/illuminate-dev/opencaselist-python
- **Issues**: https://github.com/illuminate-dev/opencaselist-python/issues

## Support

For issues related to:

- **This library**: Open an issue on GitHub
- **The OpenCaselist API**: Contact the OpenCaselist team
- **OpenCaselist website**: Visit https://opencaselist.com

## Acknowledgments

This library provides a Python interface to the OpenCaselist API. OpenCaselist is an independent platform for debate case disclosure.

---

**Author**: Henry Beveridge (henrydbeveridge@gmail.com)
