# GAURANGA Magisk Module

## Overview

This Magisk module provides root-level integration for GAURANGA System Agent.

## Features

- ✅ Auto-start on boot (with root)
- ✅ System-level permissions
- ✅ Background service with higher priority
- ✅ Access to system APIs
- ✅ Init.d script support

## Installation

1. Flash the module via Magisk Manager
2. Reboot device
3. GAURANGA will auto-start

## Files

```
magisk-module/
├── META-INF/
│   └── com/google/android/
│       └── update-binary
├── system/
│   ├── bin/
│   │   └── gauranga-agent
│   └── etc/
│       └── init.gauranga.rc
├── common/
│   └── install.sh
├── module.prop
└── README.md
```

## Requirements

- Magisk v24.0+
- Android 8.0+
- Root access

## Usage

After installation, GAURANGA Agent will automatically start on every boot.

To manually control:
```bash
# Start
gauranga-agent start

# Stop
gauranga-agent stop

# Status
gauranga-agent status
```

## Status: 🚀 READY