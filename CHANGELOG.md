# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project restructuring with improved folder organization
- `.editorconfig` for consistent code formatting across editors
- `CONTRIBUTING.md` with contribution guidelines
- `CHANGELOG.md` for version history tracking
- Improved `.gitignore` with better organization
- Enhanced `.dockerignore` to include documentation files

### Changed
- Repository structure reorganized for better clarity and maintainability
- Updated documentation to reflect new structure
- Improved configuration files with better documentation

### Deprecated
- `src/scripts/export_to_pdf.py` — Use `src/scripts/export_presentation.py` instead

### Removed
- Deprecated exporter will be removed in v2.0.0 (scheduled)
- Duplicate reveal.js library references (cleanup recommended)

### Fixed
- `.dockerignore` now properly preserves documentation in container
- Improved test organization and discoverability

---

## [1.0.0] - 2026-01-15

### Added
- Initial release of COC IIoT Talk 2026 presentation
- Complete Dockerized toolchain for AsciiDoc-based presentations
- Reveal.js integration with custom Apache-aligned theme
- Live-reload development server with Docker Compose
- Decktape-based PDF export functionality
- Support for speaker notes and presentation controls
- Comprehensive documentation and quick-start guide
- Python-based presentation export with Docker containerization
- Test suite for Python and JavaScript components
- AsciiDoc parser with reveal.js compilation support

### Features
- **AsciiDoc Support** — Write slides in semantic AsciiDoc syntax
- **Live Reloading** — Automatic compilation and browser refresh on file changes
- **Offline Capability** — Bundled reveal.js library for offline presentations
- **PDF Export** — Containerized export using Decktape
- **Speaker Notes** — Dedicated speaker view with notes and timers
- **Custom Theme** — Apache-aligned styling system
- **Cross-Platform** — Works on Windows, macOS, and Linux

### Technical Details
- **Node.js 20+** runtime
- **Docker** containerization with compose support
- **Python 3.6+** for export utilities
- **Reveal.js 5.x** presentation framework
- **Asciidoctor** for document processing

---

## Deprecation Notice

### `export_to_pdf.py` (Scheduled for removal in v2.0.0)

The old `src/scripts/export_to_pdf.py` is deprecated. Please migrate to:

```bash
# Old (deprecated):
python src/scripts/export_to_pdf.py docs/presentation.adoc

# New (current):
python src/scripts/export_presentation.py --source docs/presentation.adoc
```

The new exporter offers:
- Better reliability with Decktape
- Improved slide rendering
- More configuration options
- Better error reporting

---

## Planned Updates

### v1.1.0 (Upcoming)
- [ ] CI/CD workflow automation
- [ ] Automatic PDF generation on release
- [ ] Better test coverage reporting
- [ ] Performance optimizations for large presentations

### v2.0.0 (Future)
- [ ] Remove deprecated `export_to_pdf.py`
- [ ] Modernize dependencies
- [ ] Enhanced accessibility features
- [ ] Improved speaker notes UI

---

## Support

For questions, issues, or contributions, please refer to:
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
- [README.md](README.md) — Project documentation
- [GitHub Issues](https://github.com/ottlukas/coc_iiot_talk_2026/issues) — Bug reports and features

---

## Version History

| Version | Release Date | Status |
|---------|-------------|--------|
| 1.0.0 | 2026-01-15 | Released |
| Unreleased | TBD | In Development |

