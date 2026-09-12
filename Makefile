install:
	uv tool install git+https://github.com/r3dBust3r/42SessionGuard.git
	42sessionguard --setup

help:
	uv run src/main.py --help

uninstall:
	uv tool uninstall 42sessionguard
	sed -i '/# 42SessionGuard/d;/^42sessionguard$$/d' ~/.profile
	rm -rf ~/.local/share/42SessionGuard

run:
	42sessionguard