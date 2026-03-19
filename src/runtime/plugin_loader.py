from __future__ import annotations

import inspect
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import List
from abstractions.plugin import Plugin


class PluginLoader:
    def __init__(self, plugins_dir: str | Path | None = None) -> None:
        # Default to ../plugins if no directory is provided
        if plugins_dir is None:
            plugins_dir = Path(__file__).parent / ".." / "plugins"

        self.plugins_dir = Path(plugins_dir).resolve()

    def load(self) -> List[Plugin]:
        # Return empty list if plugin folder does not exist
        if not self.plugins_dir.exists():
            print(f"[PluginLoader] Folder not Found: {self.plugins_dir}")
            return []

        plugins: List[Plugin] = []

        # Iterate over all Python files in the plugin directory
        for file in sorted(self.plugins_dir.glob("*.py")):
            # Skip private/helper files
            if file.name.startswith("_"):
                continue

            mod = self._import_module(file)
            if not mod:
                continue

            # Find all classes defined in the module
            for _, cls in inspect.getmembers(mod, inspect.isclass):
                # Ignore imported classes from other modules
                if cls.__module__ != mod.__name__:
                    continue

                # Only load subclasses of Plugin (excluding Plugin itself)
                if not issubclass(cls, Plugin) or cls is Plugin:
                    continue

                # Skip abstract base classes
                if inspect.isabstract(cls):
                    continue

                try:
                    plugins.append(cls())  # Instantiate plugin
                except TypeError as e:
                    print(f"[PluginLoader] Couldn't load a instance of {cls.__name__}: {e}")

        return plugins

    def _import_module(self, file: Path):
        # Create unique module name to avoid conflicts
        module_name = f"plugins_{file.stem}_{abs(hash(str(file)))}"

        spec = spec_from_file_location(module_name, file)
        if not spec or not spec.loader:
            print(f"[PluginLoader] Spec failed for: {file}")
            return None

        mod = module_from_spec(spec)

        try:
            # Execute the module (dynamic import)
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            return mod
        except Exception as e:
            print(f"[PluginLoader] Error while importing  {file}: {e}")
            return None