#! /bin/sh

echo -n "Generating testsuite..."
/bin/rm -f testsuite.*
for device in laserjet ljet3 ljet4 lj5gray lj5mono pxlmono pxlcolor pdfwrite pswrite psgray psmono psrgb ; do
    gs -dQUIET -dBATCH -dNOPAUSE -sOutputFile="testsuite.$device" -sDEVICE="$device" master.ps ;
    done
echo 

echo -n "File master.ps should be 16 pages long, result is : "
python ../pykota/pdlanalyzer.py master.ps

echo "Analyzing testsuite..."
for file in testsuite.* ; do
    echo -n "$file ===> " && python ../pykota/pdlanalyzer.py "$file" ;
done    
