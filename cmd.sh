#!/bin/bash

workdir="/home/pi/piaudiocast"

cd $workdir

case "$1" in 
    "poweroff")
		sudo shutdown -h now
	;;
	"reboot")
		sudo shutdown -r now
	;;
	"picast")
		if [ "$2" = "start" ]
		then
			echo "Starting piAudioCast"
			amixer set Headphone 90%
		    sudo -E /usr/bin/python3 $workdir/picast.py >$workdir/picast.log 2>&1 &
		elif [ "$2" = "stop" ]
		then
			if [ ! -z "$(pgrep -f picast.py)" ]
			then
				let pid=$(pgrep -f picast.py)
				echo "piAudioCast is stopped (kill)."
				sudo -E kill -9 $pid
				if [ ! -z "$(pgrep -f picast.py)" ]
				then
					let pid=$(pgrep -f picast.py)
					echo "piAudioCast is stopped (kill)."
					sudo -E kill -9 $pid
				else
					echo "piAudioCast is not running."
				fi
			else
				echo "piAudioCast is not running."
			fi
		elif [ "$2" = "restart" ]
		then
			if [ ! -z "$(pgrep -f picast.py)" ]
			then
				let pid=$(pgrep -f picast.py)
				echo "piAudioCast is stopped (kill)."
				sudo -E kill -9 $pid
				if [ ! -z "$(pgrep -f picast.py)" ]
				then
					let pid=$(pgrep -f picast.py)
					echo "piAudioCast is stopped (kill)."
					sudo -E kill -9 $pid
				else
					echo "piAudioCast is not running."
				fi
			else
				echo "piAudioCast is not running."
			fi
			sleep 2
			echo "Starting piAudioCast"
			amixer set Headphone 90%
			sudo -E /usr/bin/python3 $workdir/picast.py >$workdir/picast.log 2>&1 &
		fi
	;;
	"start")
		sh $workdir/cmd.sh picast start
	;;
esac
		