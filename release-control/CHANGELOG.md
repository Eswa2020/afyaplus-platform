# Changelog, afyaplus-logistics MCP

All notable changes to this MCP server are documented here.
Format: Keep a Changelog. Versioning: SemVer.


## [Unreleased]

### Breaking (draft, do not deploy to partners yet)
- **check_stock**: rename the required argument `item` to `item_code`.
  Agents that cached the old schema still send `item=` and will fail on every call.
  Target: **2.0.0**. Ship a dual-argument shim in 1.2.x that accepts both names
  and warns on `item`, then remove `item` no earlier than 2026-12-31.

  
## [1.1.0], 2026-10-02
### Added
- `list_low_stock(clinic_id, threshold=10)`: items at one clinic with fewer than
  `threshold` units on hand. Default matches the reorder rule in `check_stock`.
- Resource `version://current` returning the server semver.
### Fixed
- `check_stock` was registered twice (duplicate decorator). Schema unchanged.

## [1.0.0], Week 6 baseline
### Added
- `check_stock(item)`, `plan_delivery_route(start_clinic_id)`,
  `get_delivery_eta(from_clinic_id, to_clinic_id)`
- Resource `clinics://directory`