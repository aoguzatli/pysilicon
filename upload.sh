# Edit the version number first at setup.cfg
python3 -m build
python3 -m twine upload dist/*
git add -A
git commit -m "multi-bit scan"
git push origin master
