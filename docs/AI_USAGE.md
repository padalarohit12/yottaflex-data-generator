# AI Usage Documentation

## Overview
This project was developed with AI assistance. All AI interactions are documented for transparency.

## Where AI Helped

### Code Generation & Development
- **Generator implementation**: AI assisted in designing and implementing the data generator architecture (src/generate.py, src/generator.py, src/anomalies.py, src/export.py, src/validate.py, src/config.py, src/models.py, src/rng.py, src/id_generator.py)
- **Anomaly injection**: AI helped design and implement the 5 required edge cases with proper labeling
- **Schema design**: AI assisted in creating the database schema and relationships
- **Export functionality**: AI helped implement CSV, JSON, and SQL export with checksums

### Documentation
- **Project documentation**: AI assisted in creating README, project plans, and schema documentation
- **Data dictionary**: AI helped create comprehensive field-level documentation

### Review & Validation
- **Code review**: Generated code was reviewed for correctness, determinism, and requirement compliance
- **Validation logic**: AI helped ensure proper referential integrity and data quality checks

## Modifications & Validation
- All generated code was reviewed and tested
- Starter scale data was generated and validated successfully
- All 5 edge cases are properly labeled in ground truth (separate from feature data)
- Deterministic generation verified with fixed seed (20261022)

## Principles Followed
- **Ground truth separation**: Anomalies labeled in separate ground_truth/ directory, never leaked to feature tables
- **Determinism**: All randomness controlled via seeded RNG
- **Reproducibility**: Same seed produces consistent results
- **Transparency**: All AI usage documented as required
