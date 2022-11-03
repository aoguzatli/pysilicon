# Edit the version number first at setup.cfg
python3 -m build
python3 -m twine upload dist/*
git add -A
git commit -m "Some general improvements."
git push origin master