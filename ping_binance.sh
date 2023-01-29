# sh script to ping binance.us flash screen when it is down

while true
do
    # change font to solid cyan
    echo -e "\033[0;36m"
    ping -c 1 api.binance.us
    if [ $? != 0 ]
    then
        # change font to blinking red
        echo -e "\033[5;31m"
        echo "Binance is unreachable!"
        # echo "Binance is down!" | wall
    fi
    sleep 5
done