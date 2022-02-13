# Edit the version number first at setup.cfg
python3 -m build
python3 -m twine upload dist/*
git add -A
git commit -m "Fixed a bug with wide scan out."
git push origin master