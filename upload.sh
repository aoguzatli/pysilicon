# Edit the version number first at setup.cfg
python3 -m build
python3 -m twine upload dist/*
git add -A
git commit -m "Added support to read/write to a list of handles as a verilog vector."
git push origin master
