// Note (Chunk 66):
// Modal management follows a consistent pattern:
// - showXxxModal() removes 'hidden' and adds 'flex'
// - hideXxxModal() removes 'flex' and adds 'hidden'
// All major modals (Inventory, Gene Vault, Furnace, Game Guide) follow this pattern.
// This keeps the UI behavior predictable and easy to maintain.