# MiniSimmy3

Next-generation modular version of MiniSimmy2.

## Planned Structure

```
minisimmy3/
├── index.html          # Clean entry point
├── js/
│   ├── core.js           # p5.js setup, draw loop, global state
│   ├── creatures.js      # Creature class + behavior
│   ├── modules.js        # Module system & merging
│   ├── ui.js             # All modals (Inventory, Gene Vault, Furnace, etc.)
│   ├── economy.js        # Prestige, Aetherium, Furnace logic
│   ├── audio.js          # Sound system
│   └── utils.js          # Helpers & formatting
└── css/
    └── style.css
```

## Goals
- Clean separation of concerns
- Easier maintenance and iteration
- Better support for future features (Gene Vault 2.0, Ranch/Brain Lab, etc.)

This is the start of the refactor from the monolithic single-file version.