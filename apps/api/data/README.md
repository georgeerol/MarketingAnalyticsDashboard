# Data Directory

This directory contains the Google Meridian MMM model data and related files.

## Structure

- `models/` - Contains the trained MMM model files
  - `saved_mmm.pkl` - Google Meridian model trace (place the file here)
- `samples/` - Sample data for testing and development

## Usage

The MMM model file should be placed at:
```
apps/api/data/models/saved_mmm.pkl
```

This location allows the API to easily access the model data while keeping it organized and separate from the application code.
