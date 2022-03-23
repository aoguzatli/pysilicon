# Edit the version number first at setup.cfg
python3 -m build
python3 -m twine upload dist/*
git add -A
git commit -m "Added scan_in and scan_out function override capability to JTAG to allow fast scan. Added a few hex functions to essentials."
git push origin master