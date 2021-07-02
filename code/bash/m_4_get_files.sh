echo "backup m_4 files make sure it's mounted !"
rsync -rtuvP --human-readable --modify-window=1 --stats --exclude-from ./syncexclude.txt /media/pi/circuitpython/ ~/git/playground/mmMover2020_03/code/m_4
