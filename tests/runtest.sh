#! /bin/sh

echo -n "Generating testsuite..."
/bin/rm -f testsuite.* master2.ps
gunzip <master.ps.gz >master2.ps
for device in laserjet ljet3 ljet4 lj5gray lj5mono pxlmono pxlcolor pdfwrite pswrite psgray psmono psrgb epson epsonc eps9mid eps9high ; do
    gs -dQUIET -dBATCH -dNOPAUSE -sOutputFile="testsuite.$device" -sDEVICE="$device" master2.ps ;
    done
echo 

echo -n "File master.ps should be 16 pages long, result is : "
python ../pykota/pdlanalyzer.py master2.ps

echo "Analyzing testsuite..."
for file in testsuite.* ; do
    echo -n "$file ===> " && python ../pykota/pdlanalyzer.py "$file" ;
done    
