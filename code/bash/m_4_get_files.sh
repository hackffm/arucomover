echo "backup m_4 files make sure it's mounted !"
rsync -rtuvP --human-readable --modify-window=1 --stats --exclude-from ./syncexclude.txt /media/pi/circuitpython/ ../m_4
