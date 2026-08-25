---
name: 3gpp-specifications
description: TS and TR numbering, spec file formats, FTP directory structure, and accessing 3GPP specifications. Use when working with 3GPP specification numbering, finding spec files, or understanding spec directory organization.
---

# 3GPP Specifications

## Overview

3GPP specifications are the primary deliverables of the 3GPP partnership. They include:

- **Technical Specifications (TS)** - Normative technical documents
- **Technical Reports (TR)** - Informative studies and reports

## TS vs TR Distinction

### TS (Technical Specification)

- **Purpose**: Define requirements, protocols, and interfaces
- **Status**: Can be revised via Change Requests (CRs)
- **Format**: Word™ (.doc) and Zip™ archives
- **Numbering**: `21.456` (Series + Spec number)
- **Authority**: Produced by WG or TSG

### TR (Technical Report)

- **Purpose**: Informative studies, analysis, or background information
- **Status**: Fixed at publication, can be revised via CRs
- **Format**: Word™ (.doc) and Zip™ archives
- **Numbering**: `TR 21.900` (TR + number)
- **Authority**: Produced by WG or TSG

## Numbering Scheme

### Format

**Two-digit series number + Three-digit spec number:**

```text
<series>.<spec>
```

**Examples:**

- TS 21.456 - Series 21, spec 456
- TS 22.101 - Series 22, spec 101
- TR 21.900 - Technical Report 21, number 900

### Specification Series Meanings

Each two-digit series corresponds to a specific technical domain:

| Series | Domain | Responsible TSG |
|--------|--------|-----------------|
| 21 | Requirements | SA |
| 22 | Service aspects ("stage 1") | SA1 |
| 23 | Technical realization ("stage 2") | SA2 |
| 24 | Signalling protocols ("stage 3") - UE to network | CT1 |
| 25 | Radio aspects (UTRA/UTRAN) | RAN |
| 26 | CODECs | SA4 |
| 27 | Data services | CT1 |
| 28 | Signalling protocols ("stage 3") - RSS-CN | CT4 |
| 29 | Signalling protocols ("stage 3") - Intra-CN | CT3/CT4 |
| 31 | UE terminal conformance (USIM) | CT6 |
| 32 | OAM&P and Charging | SA5 |
| 33 | Security | SA3 |
| 34 | UE and USIM test specifications | CT6/RAN5 |
| 35 | Security algorithms | SA3 |
| 36 | LTE (Evolved UTRA/E-UTRAN) | RAN |
| 37 | Multiple radio access technology aspects | RAN |
| 38 | 5G NR (New Radio) | RAN |

**Key patterns:**

- **Series 21-24**: Core requirements, services, architecture, signalling
- **Series 25, 36-38**: Radio technologies (UTRA → LTE → NR)
- **Series 31-35**: Security and terminal testing
- **Series 26, 32**: Media codecs and network management

### Document Type Prefixes

- **TS**: Technical Specifications (normative)
- **TR**: Technical Reports (informative)

## Spec File Formats

### Word™ Format

- **Purpose**: Formal specification document for review and change
- **Extension**: `.doc`
- **Structure**: Can include revision marks ("Track Changes")

### Zip™ Format

- **Purpose**: Archive format for distribution
- **Extension**: `.zip`
- **Contents**: Word™ .doc files and additional resources

## FTP Directory Structure

### Root Directory

```
https://www.3gpp.org/ftp/Specs/<YYYY>-<MM>/
```

**TSG Round Examples:**

- RAN#110: `https://www.3gpp.org/ftp/Specs/2025-12/`
- SA#110: `https://www.3gpp.org/ftp/Specs/2025-12/`
- CT#110: `https://www.3gpp.org/ftp/Specs/2025-12/SpecslistexTSG/TSG110.htm`

### Directory Contents

Each TSG round directory contains:

- HTML index pages (SpecslistexTSG/TSG#>.htm)
- Individual spec files (.doc, .zip)
- Delta directories for parallel releases (e.g., 21.101d)
- CR database and work item references

## Spec Categories

### Major Categories

- **GSM (including GPRS and EDGE)**
- **W-CDMA (including HSPA)**
- **LTE** (including LTE-Advanced and LTE-Advanced Pro)
- **5G** (including 5G NR Standalone)

### Spec Numbering Pattern

**When a new spec is created:**

1. Allocated next sequential spec number
2. Example: If last spec in series 21 is 21.456, next is 21.457
3. Continues until end of series or major release change

**Example:**

```
Series 21: 21.001, 21.002, 21.003, ..., 21.456
Series 22: 22.001, 22.002, 22.003, ..., 22.101
```

## Spec Files

### File Naming Convention

Spec files follow 3GPP naming conventions:

- Series number and spec number
- Type identifier (TS/TR if applicable)
- Version number (for revised versions)
- Language code (if multilingual)

**Example:**

- `21.456.doc` - TS 21.456 Word™ document
- `21.456.zip` - Zip™ archive containing Word™ files
- `21.456_003.doc` - Version 003 revision

## Working Groups and Specs

### Working Group Responsibility

Each Working Group is responsible for specifications in their domain:

- **RAN**: Radio access technologies
- **SA**: System architecture and services
- **CT**: Core network and terminals

### Spec Assignment

Specs are assigned to Working Groups based on their scope:

- Technical specs typically belong to specific WGs
- TSG plenaries approve specs for all TSGs

## Release Management

### MCC (Mobile Competence Centre)

The MCC aims to make all specs available following TSG round as soon as possible.

### Target Dates

- **Standard**: 4 weeks after TSG plenary
- **Extra time**: Additional week for large volumes or holiday periods

## Version Control

### Spec Versions

- **Initial version**: When first published as TS/TR
- **Revisions**: Numbered versions created via Change Requests
- **Dot notation**: Decimal numbering (e.g., 21.456.1)

**Example Revision Numbering:**

- Initial: 21.456
- First revision: 21.456.1
- Second revision: 21.456.2
- Third revision: 21.456.3

### Version Number Format

Spec version numbers follow the format: `<series>.<version>`

**Examples:**

- `21.456.0` - Initial version of spec 21.456
- `21.456.1` - First revision of spec 21.456
- `22.101.3` - Third revision of spec 22.101

## Database References

### CR Database

Change Requests are tracked in a database accessible via:

- **Netovate Search**: Free CR database search tool
- **Portal CR Database**: 3GPP portal CR database
- **Spec History**: Each spec's history lists all approved CRs

### Work Items

3GPP Work Items define features to be developed. New specs and CRs are linked to Work Items.

## Key Points

- **Spec Numbering is hierarchical**: Series → Spec Number
- **TR numbers are separate series**: Use TR prefix for reports
- **Revisions create new versions**: Each CR creates a new version number
- **Multiple CRs can affect one spec**: All are merged into single version
- **Mirror CRs require same WI code**: For specs in multiple releases

## Cross-References

- **@3gpp-releases** - For release structure and freeze concepts
- **@3gpp-working-groups** - For understanding which WG owns which specs
- **@3gpp-change-request** - For modification process via CRs
- **@3gpp-meetings** - For understanding when specs are approved (at TSG plenaries)

## Resources

- **3GPP Official**: <https://www.3gpp.org/>
- **3GPP Portal**: <https://portal.3gpp.org/>
- **3GPP Work Plan**: <https://www.3gpp.org/specifications-technologies/3gpp-work-plan/>
- **MCC Info**: Available in spec list tables

## Usage in Code

### Finding Spec Files

```python
import requests
from bs4 import BeautifulSoup

# FTP directory for Release 18
base_url = "https://www.3gpp.org/ftp/Specs/2018-12/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# Parse all spec files
for link in soup.find_all("a", href=True):
    href = link.get("href")
    if href.endswith(".doc") or href.endswith(".zip"):
        print(f"Found spec: {href}")
```

### Spec Number Parsing

```python
import re

def parse_spec_number(filename: str) -> tuple:
    """Parse spec number from filename."""
    # Extract series number and spec number
    match = re.match(r"(\d{2})(\d{3})(\.doc|\.zip)", filename)
    if not match:
        return (None, None)
    
    return (match.group(1), match.group(2))
```

## Common Patterns

### Delta Directories

For parallel releases (e.g., Rel-4/5/6), 3GPP creates delta directories containing only changed specs.

**Purpose**: Reduce duplicate storage and make it easy to identify what's new in each release.

## Versioning in Practice

- **Dot notation**: Use decimal versions for clarity (e.g., 21.456.1)
- **Editorial changes**: Occasionally updated by MCC, not versioned
- **Major/minor changes**: Some specs have major version increments between releases

## Related Documents

- **Versioning Scheme**: <https://www.3gpp.org/specifications-technologies/specifications-by-series/version-numbering-scheme>
- **Work Items**: <https://www.3gpp.org/specifications-technologies/3gpp-work-plan/what-is-a-work-item>
